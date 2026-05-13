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
    export PATH="$HOME/.local/bin:$PATH"
fi
echo -e "${GREEN}uv OK${NC}"

# Create install directory
echo -e "${YELLOW}Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Copy project files
echo -e "${YELLOW}Copying project files...${NC}"
if [ -f "main.py" ]; then
    echo "Files already present, skipping copy"
else
    echo "Error: Project files not found in current directory"
    exit 1
fi

# Initialize Python environment with uv
echo -e "${YELLOW}Setting up Python environment with uv...${NC}"
if [ ! -d ".venv" ]; then
    uv venv
    source .venv/bin/activate
    uv add python-telegram-bot pyyaml psutil
else
    echo "Virtual environment already exists"
fi

# Set permissions
echo -e "${YELLOW}Setting file permissions...${NC}"
chmod 755 main.py proxmox.py alerts.py telegram.py
chmod 750 "$INSTALL_DIR"

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo -e "${RED}config.yaml not found!${NC}"
    echo -e "${YELLOW}Please copy config.yaml.example to config.yaml and configure it${NC}"
    exit 1
fi

chmod 660 config.yaml

# Setup systemd service
echo -e "${YELLOW}Setting up systemd service...${NC}"
cp systemd/proxmox-monitor.service "$SERVICE_FILE"
cp systemd/proxmox-monitor.timer "$TIMER_FILE"
chmod 644 "$SERVICE_FILE" "$TIMER_FILE"

# Update service file with correct path
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$INSTALL_DIR|g" "$SERVICE_FILE"
sed -i "s|ExecStart=.*|ExecStart=$INSTALL_DIR/.venv/bin/python3 main.py|g" "$SERVICE_FILE"

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
