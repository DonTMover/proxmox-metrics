# Use official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY . .

# Setup Python environment with uv
RUN uv sync

# Create directories for logs and state files
RUN mkdir -p /var/log /etc/proxmox-monitor

# Copy config
RUN cp config/config.empty.yaml /etc/proxmox-monitor/config.yaml

# Create entrypoint script that handles bot token from environment
RUN cat > /app/entrypoint.sh << 'EOF'
#!/bin/sh
if [ -n "$PROXMOX_BOT_TOKEN" ]; then
    python3 -c "
    import yaml
    from pathlib import Path
    
    # Update config with bot token from environment
    config_path = Path('config/config.yaml')
    if not config_path.exists():
        config_path = Path('/etc/proxmox-monitor/config.yaml')
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    config['telegram']['token'] = '$PROXMOX_BOT_TOKEN'
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    "
fi
exec .venv/bin/python3 -m src.main
EOF
chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the application with entrypoint
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
