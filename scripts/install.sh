#!/bin/bash
# Installation script for Proxmox Monitor
# Run as root: sudo bash install.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/proxmox-monitor"
SERVICE_FILE="/etc/systemd/system/proxmox-monitor.service"
TIMER_FILE="/etc/systemd/system/proxmox-monitor.timer"

echo -e "${GREEN}=== Proxmox Monitor Installation ===${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Check if Python 3.11+ is available
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"
if [[ $(echo -e "$REQUIRED_VERSION\n$PYTHON_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
    echo -e "${RED}Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}Python $PYTHON_VERSION OK${NC}"

# Check if uv is installed
echo "Checking for uv package manager..."
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}Installing uv package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
    # Also add to root's PATH permanently for sudo
    if ! grep -q "\.local/bin" /root/.bashrc 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.bashrc
    fi
fi
# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$PATH"
echo -e "${GREEN}uv OK${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Verify we have the required project files
echo -e "${YELLOW}Verifying project files...${NC}"
if [ ! -f "$PROJECT_ROOT/src/main.py" ] || [ ! -f "$PROJECT_ROOT/config/config.yaml" ]; then
    echo -e "${RED}Error: Project files not found in $PROJECT_ROOT${NC}"
    echo "Required files: src/main.py and config/config.yaml"
    exit 1
fi
echo -e "${GREEN}Project files found${NC}"

# Create install directory
echo -e "${YELLOW}Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"

# Copy project files
echo -e "${YELLOW}Copying project files...${NC}"
cp -r "$PROJECT_ROOT/src" "$INSTALL_DIR/"
cp -r "$PROJECT_ROOT/config" "$INSTALL_DIR/"
cp "$PROJECT_ROOT/pyproject.toml" "$INSTALL_DIR/"
cp -r "$PROJECT_ROOT/scripts" "$INSTALL_DIR/"
cp -r "$PROJECT_ROOT/systemd" /etc/systemd/system/ 2>/dev/null || cp "$PROJECT_ROOT/systemd"/* /etc/systemd/system/

# Initialize Python environment with uv
echo -e "${YELLOW}Setting up Python environment with uv...${NC}"
cd "$INSTALL_DIR"
if [ ! -f "uv.lock" ]; then
    echo "Running uv sync..."
    uv sync
    echo -e "${GREEN}Python environment setup complete${NC}"
else
    echo "Python environment already configured"
fi

# Set permissions
echo -e "${YELLOW}Setting file permissions...${NC}"
chmod 755 src/main.py src/proxmox.py src/alerts.py src/telegram_bot.py
chmod 750 "$INSTALL_DIR"

# Check if config.yaml exists
if [ ! -f "$INSTALL_DIR/config/config.yaml" ]; then
    echo -e "${YELLOW}config.yaml not found, creating from template...${NC}"
    if [ -f "$INSTALL_DIR/config/config.empty.yaml" ]; then
        cp "$INSTALL_DIR/config/config.empty.yaml" "$INSTALL_DIR/config/config.yaml"
        echo -e "${GREEN}Created config.yaml from template${NC}"
    else
        echo -e "${RED}Neither config.yaml nor config.empty.yaml found!${NC}"
        exit 1
    fi
fi

chmod 660 "$INSTALL_DIR/config/config.yaml"

# Setup systemd service
echo -e "${YELLOW}Setting up systemd service...${NC}"
chmod 644 /etc/systemd/system/proxmox-monitor.service /etc/systemd/system/proxmox-monitor.timer

# Update service file with correct path and use uv run
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$INSTALL_DIR|g" /etc/systemd/system/proxmox-monitor.service
sed -i "s|ExecStart=.*|ExecStart=/bin/sh $INSTALL_DIR/scripts/entrypoint.sh|g" /etc/systemd/system/proxmox-monitor.service

# Reload systemd
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Enable services
echo -e "${YELLOW}Enabling services...${NC}"
systemctl enable proxmox-monitor.service
systemctl enable proxmox-monitor.timer

# Start services
echo -e "${YELLOW}Starting services...${NC}"
systemctl start proxmox-monitor.service
systemctl start proxmox-monitor.timer

# Verify installation
echo -e "${GREEN}Verifying installation...${NC}"
sleep 2

if systemctl is-active --quiet proxmox-monitor.service; then
    echo -e "${GREEN}✓ Service is running${NC}"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    echo "Check logs: systemctl status proxmox-monitor.service"
    exit 1
fi

if systemctl is-active --quiet proxmox-monitor.timer; then
    echo -e "${GREEN}✓ Timer is active${NC}"
else
    echo -e "${RED}✗ Timer failed to start${NC}"
    exit 1
fi

# Final output
echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Service information:"
echo "  Location: $INSTALL_DIR"
echo "  Service:  $SERVICE_FILE"
echo "  Timer:    $TIMER_FILE"
echo ""
echo "Useful commands:"
echo "  Status:   systemctl status proxmox-monitor.service"
echo "  Logs:     journalctl -u proxmox-monitor.service -f"
echo "  Stop:     systemctl stop proxmox-monitor.service"
echo "  Start:    systemctl start proxmox-monitor.service"
echo "  Restart:  systemctl restart proxmox-monitor.service"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Test the bot with /start command in Telegram"
echo "  2. Customize thresholds in config.yaml"
echo "  3. Monitor logs: journalctl -u proxmox-monitor.service -f"
echo ""
