#!/bin/sh
# Entrypoint script for Proxmox Monitor Docker container
# Updates bot token from environment variable if provided

if [ -n "$PROXMOX_BOT_TOKEN" ]; then
    echo "ℹ️  Updating bot token from environment variable..."
    python3 /app/scripts/update_token.py
fi

echo "🚀 Starting Proxmox Monitor..."
exec .venv/bin/python3 -m src.main
