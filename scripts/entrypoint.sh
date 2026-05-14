#!/bin/sh
# Entrypoint script for Proxmox Monitor
# Works in both Docker and systemd environments

# Ensure root's local bin is in PATH (for uv on systemd)
export PATH="/root/.local/bin:$PATH"

# Detect uv location (Docker uses /app/.venv, systemd uses /root/.local/bin)
if command -v uv >/dev/null 2>&1; then
    UV_CMD="uv"
elif [ -x "/root/.local/bin/uv" ]; then
    UV_CMD="/root/.local/bin/uv"
else
    echo "Error: uv not found in PATH or at /root/.local/bin/uv"
    exit 1
fi

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
    "$UV_CMD" run python "$APP_DIR/scripts/update_token.py"
fi

echo "🚀 Starting Proxmox Monitor..."
cd "$APP_DIR"
exec "$UV_CMD" run python -m src.main
