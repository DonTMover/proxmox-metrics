#!/bin/sh
# Entrypoint script for Proxmox Monitor Docker container
# Updates bot token from environment variable if provided

export PYTHONPATH="/app/src:$PYTHONPATH"

if [ -n "$PROXMOX_BOT_TOKEN" ]; then
    echo "ℹ️  Updating bot token from environment variable..."
    uv run python /app/scripts/update_token.py
fi

echo "🚀 Starting Proxmox Monitor..."
exec uv run python -m src.main
