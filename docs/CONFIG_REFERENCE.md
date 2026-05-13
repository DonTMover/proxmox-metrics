# Configuration Reference

## config.yaml - Complete Guide

### Telegram Section
```yaml
telegram:
  # Bot token from @BotFather
  # Format: "numbers:LETTERS_and_numbers"
  token: "YOUR_BOT_TOKEN_HERE"
  
  # List of Telegram user IDs allowed to use commands
  # Get your ID from @userinfobot
  allowed_user_ids:
    - 123456789      # Your personal ID
    - 987654321      # Other trusted users (optional)
  
  # Chat ID for sending notifications
  # Can be:
  # - Personal chat ID (positive number, e.g., 987654321)
  # - Group chat ID (negative number, e.g., -1001234567890)
  # - Channel ID (negative number with 100 prefix)
  chat_id: -1001234567890
```

### Proxmox Section
```yaml
proxmox:
  # Node name - run "pvesh get /nodes" to find
  # Usually "pve" for single-node setups
  node: "pve"
  
  # List of Container IDs to monitor for critical status
  # These will trigger alerts if they stop
  required_cts:
    - 101        # Nextcloud example
    - 102        # Other container
    - 103        # Add as needed
  
  # List of VM IDs to monitor for critical status
  required_vms:
    - 200        # Important VM
    - 201        # Another VM (optional)
```

### Thresholds Section
```yaml
thresholds:
  # CPU usage thresholds (%)
  cpu:
    warning: 80      # First alert level
    critical: 95     # Emergency level
  
  # RAM usage thresholds (%)
  ram:
    warning: 85
    critical: 95
  
  # Swap usage thresholds (%)
  # Note: Any swap usage can indicate pressure
  swap:
    warning: 50      # Half of swap in use
    critical: 80     # Almost full
  
  # Disk usage thresholds (%)
  disk:
    warning: 85      # Getting full
    critical: 95     # Emergency, almost full
```

### Scheduler Section
```yaml
scheduler:
  # How often to send periodic status summaries (seconds)
  # Examples:
  # 60     - Every 1 minute (very verbose)
  # 300    - Every 5 minutes (default, good balance)
  # 600    - Every 10 minutes (less frequent)
  # 1800   - Every 30 minutes (for minimal notifications)
  summary_interval: 300
  
  # Minimum time between repeating the same alert (seconds)
  # Examples:
  # 300    - 5 minutes (frequent alerts)
  # 1800   - 30 minutes (default, moderate)
  # 3600   - 1 hour (less spam)
  # 7200   - 2 hours (very infrequent)
  alert_repeat: 1800
```

### File Paths
```yaml
# State file location (tracks alert history)
state_file: "state.json"

# Log file location
log_file: "/var/log/proxmox-monitor.log"
```

## Common Configurations

### For High-Traffic Servers
```yaml
thresholds:
  cpu:
    warning: 70    # More sensitive
    critical: 90
  ram:
    warning: 80
    critical: 90
scheduler:
  summary_interval: 600    # Less frequent summaries
  alert_repeat: 900        # 15 minute repeat
```

### For Development/Testing
```yaml
scheduler:
  summary_interval: 60     # Every minute
  alert_repeat: 300        # Every 5 minutes
```

### For Production
```yaml
thresholds:
  cpu:
    warning: 75
    critical: 95
  ram:
    warning: 85
    critical: 95
  disk:
    warning: 85
    critical: 95
scheduler:
  summary_interval: 300
  alert_repeat: 1800
```

### For Minimal Notifications
```yaml
scheduler:
  summary_interval: 3600   # Hourly summaries
  alert_repeat: 3600       # Hourly alerts
```

## Finding Configuration Values

### Get Node Name
```bash
pvesh get /nodes
# Output shows node names
# For single node: usually "pve"
```

### Get Container IDs and Names
```bash
pct list
# Output: VMID STATUS NAME ...
# Example: 101 running nextcloud
```

### Get VM IDs and Names
```bash
qm list
# Output: VMID STATUS NAME ...
# Example: 200 running ubuntu-server
```

### Get Telegram IDs

**Personal User ID:**
1. Open Telegram
2. Search for `@userinfobot`
3. Send any message
4. Bot responds with your ID

**Group/Channel Chat ID:**
1. Add bot to group
2. Send a message
3. Run this to get ID:
```bash
curl https://api.telegram.org/botTOKEN/getUpdates | grep chat
```

Replace TOKEN with your bot token.

## Configuration Validation

### Check syntax
```bash
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

### Validate values
```python
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Check required fields
assert config['telegram']['token'], "Token required"
assert config['telegram']['allowed_user_ids'], "User IDs required"
assert config['telegram']['chat_id'], "Chat ID required"
print("✓ Config valid")
```

## Updating Configuration

1. **Edit config:**
   ```bash
   sudo nano /opt/proxmox-monitor/config.yaml
   ```

2. **Restart service:**
   ```bash
   sudo systemctl restart proxmox-monitor.service
   ```

3. **Verify changes:**
   ```bash
   sudo journalctl -u proxmox-monitor.service -f
   ```

## Troubleshooting Configuration

### Token not working
- Check format: `numbers:UPPERCASE_and_lowercase_123`
- Verify no extra spaces
- Regenerate from @BotFather

### Threshold too sensitive
- Increase warning/critical values
- Increase alert_repeat to reduce spam

### Not seeing summaries
- Check summary_interval (in seconds)
- Verify chat_id is correct
- Check logs for errors

### Bot not recognizing commands
- Verify user ID in allowed_user_ids
- Check Telegram privacy settings
- Restart bot: `systemctl restart proxmox-monitor.service`
