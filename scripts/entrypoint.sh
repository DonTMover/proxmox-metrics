#!/bin/sh
# Entrypoint script for Proxmox Monitor
# Works in both Docker and systemd environments

# Ensure root's local bin is in PATH (for uv on systemd)
export PATH="/root/.local/bin:$PATH"

# Set Python path for Docker or systemd
if [ -d "/app/src" ]; then
    export PYTHONPATH="/app/src:$PYTHONPATH"
    APP_DIR="/app"
else
    # systemd installation
    APP_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
    export PYTHONPATH="$APP_DIR/src:$PYTHONPATH"
fi

if [ -n "$PROXMOX_BOT_TOKEN" ]; then
    echo "ℹ️  Updating bot token from environment variable..."
    uv run python "$APP_DIR/scripts/update_token.py"
fi

echo "🚀 Starting Proxmox Monitor..."
cd "$APP_DIR"
exec uv run python -m src.main
