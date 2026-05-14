#!/usr/bin/env python3
"""Update config with bot token from environment variable"""
import yaml
import os
from pathlib import Path

# Try to find config file
config_path = Path("config/config.yaml")
if not config_path.exists():
    config_path = Path("/etc/proxmox-monitor/config.yaml")

# Update token if config exists
if config_path.exists():
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Get token from environment
        token = os.getenv("PROXMOX_BOT_TOKEN", "")
        if token:
            config["telegram"]["token"] = token
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
            print(f"✅ Bot token updated in {config_path}")
    except Exception as e:
        print(f"⚠️ Failed to update token: {e}")
