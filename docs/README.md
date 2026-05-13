# Proxmox VE Telegram Monitor

A comprehensive Python monitoring solution for Proxmox VE hosts with Telegram bot notifications, automatic alerts, and interactive commands.

## Features

### Monitoring
- ✅ Real-time CPU, RAM, Swap, and Disk usage tracking
- ✅ Container (CT) and Virtual Machine (VM) status monitoring
- ✅ System uptime and temperature sensors
- ✅ Configurable alert thresholds (warning/critical levels)
- ✅ Automatic recovery detection

### Notifications
- 📨 Periodic status summaries (configurable interval)
- 🚨 Critical and warning alerts with automatic deduplication
- ✅ Recovery notifications when systems return to normal
- 🔔 Alert repeat control to prevent spam

### Telegram Bot Commands
- `/id` - Display your Telegram user ID (🔓 **publicly available** - no auth required!)
- `/start` - Welcome and bot status
- `/status` - Host system status report
- `/vms` - List all containers and VMs
- `/alerts` - Show currently active alerts
- `/help` - Show available commands

> **New Feature:** Any user can run `/id` to get their Telegram user ID, making it easy to add new authorized users without admin intervention!

### Security
- 🔐 Whitelist-based access control (allowed_user_ids)
- 🔒 Configuration file with restricted permissions
- 🛡️ No sensitive data in logs
- 🔑 Token stored only in config.yaml

## Requirements

- **OS**: Proxmox VE 7.x+ (Debian-based)
- **Python**: 3.11+
- **Package Manager**: `uv` (Python package installer)
- **Root Access**: Required for system metrics collection

## Installation

### 1. Create Project Directory

```bash
mkdir -p /opt/proxmox-monitor
cd /opt/proxmox-monitor
```

### 2. Initialize Python Environment

```bash
uv init
uv add python-telegram-bot pyyaml psutil
uv sync
```

### 3. Copy Project Files

```bash
# From your development machine or extracted archive
cp main.py proxmox.py alerts.py telegram.py /opt/proxmox-monitor/
cp config.yaml /opt/proxmox-monitor/
chmod 660 /opt/proxmox-monitor/config.yaml
```

### 4. Set Up Telegram Bot

1. **Create a Bot**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow the prompts to create your bot
   - Save your bot token

2. **Get Your User ID**
   - Search for `@userinfobot` in Telegram
   - Send any message to get your user ID
   - Or use `/id` command after bot starts

3. **Get Chat ID** (for group chats)
   - Add bot to your chat
   - Send a message
   - Check logs or use `curl` to find chat ID

### 5. Configure the Monitor

Edit `/opt/proxmox-monitor/config.yaml`:

```yaml
telegram:
  token: "YOUR_BOT_TOKEN"
  allowed_user_ids:
    - YOUR_USER_ID
    - ANOTHER_USER_ID  # Optional: for multiple users
  chat_id: YOUR_CHAT_ID

proxmox:
  node: "pve"  # Check with: pvesh get /nodes
  required_cts: [101, 102]  # CT IDs to monitor
  required_vms: [200]        # VM IDs to monitor

thresholds:
  cpu:
    warning: 80
    critical: 95
  ram:
    warning: 85
    critical: 95
  swap:
    warning: 50
    critical: 80
  disk:
    warning: 85
    critical: 95

scheduler:
  summary_interval: 300    # Send status every 5 minutes
  alert_repeat: 1800       # Repeat critical alerts every 30 minutes
```

### 6. Set Up systemd Service

```bash
# Copy systemd unit files
sudo cp systemd/proxmox-monitor.service /etc/systemd/system/
sudo cp systemd/proxmox-monitor.timer /etc/systemd/system/

# Set permissions
sudo chmod 644 /etc/systemd/system/proxmox-monitor.*

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable proxmox-monitor.service
sudo systemctl enable proxmox-monitor.timer
sudo systemctl start proxmox-monitor.service
sudo systemctl start proxmox-monitor.timer
```

### 7. Verify Installation

```bash
# Check service status
sudo systemctl status proxmox-monitor.service

# Check timer status
sudo systemctl status proxmox-monitor.timer
sudo systemctl list-timers

# View logs
sudo journalctl -u proxmox-monitor.service -f

# Test commands in Telegram
# Send /start to verify bot is working
```

## Configuration Details

### Alert Thresholds

| Metric | Level | Value | Description |
|--------|-------|-------|-------------|
| CPU | Warning | 80% | Alert when CPU exceeds 80% |
| CPU | Critical | 95% | Critical alert when CPU exceeds 95% |
| RAM | Warning | 85% | Alert when RAM usage exceeds 85% |
| RAM | Critical | 95% | Critical alert when RAM usage exceeds 95% |
| Swap | Warning | 50% | Alert when swap usage exceeds 50% |
| Swap | Critical | 80% | Critical alert when swap usage exceeds 80% |
| Disk | Warning | 85% | Alert when disk usage exceeds 85% |
| Disk | Critical | 95% | Critical alert when disk usage exceeds 95% |

### Scheduler Settings

- `summary_interval`: How often to send periodic status reports (in seconds)
  - Default: 300 (5 minutes)
  - Minimum: 60 (1 minute)
  - Useful values: 300 (5min), 600 (10min), 1800 (30min)

- `alert_repeat`: Minimum time between repeat alerts (in seconds)
  - Default: 1800 (30 minutes)
  - Critical alerts can repeat after this interval
  - Warning alerts won't spam if unchanged

## Monitoring Metrics

### Host Metrics
- **CPU**: Usage percentage and load average (1/5/15 min)
- **Memory**: RAM used/total (MB and percentage)
- **Swap**: Swap used/total (MB and percentage)
- **Disk**: Usage for `/`, `/var/lib/vz`, `/boot`
- **Uptime**: Days, hours, minutes since last boot
- **Temperature**: CPU and system temperatures (if available via `sensors`)

### Container/VM Metrics
- **ID & Name**: Container/VM identifier
- **Status**: Running or stopped
- **Type**: Container (CT) or Virtual Machine (VM)

## Alert Types

### Normal Operation Alerts
- ✅ Recovery: System returned to normal after alert
- ℹ️ Info: Informational messages

### Warning Alerts
- ⚠️ CPU warning (>80%)
- ⚠️ RAM warning (>85%)
- ⚠️ Swap warning (>50%)
- ⚠️ Disk warning (>85%)

### Critical Alerts
- 🔴 CPU critical (>95%)
- 🔴 RAM critical (>95%)
- 🔴 Swap critical (>80%)
- 🔴 Disk critical (>95%)
- 🔴 Required container/VM stopped

## Notification Examples

### Periodic Summary
```
🖥 Proxmox pve | 14:23
CPU: 45% ✅
RAM: 8/32GB (25%) ✅
Swap: 0.2/8GB (3%) ✅
Disk: / 62% ✅ | /var/lib/vz: 78% ⚠️ | /boot: 42% ✅
CT/VM: 8/9 running
🔴 CT101 (mycontainer) stopped
```

### Alert Notification
```
🚨 CPU
CPU usage 96.5%
```

### Recovery Notification
```
✅ CPU
CPU usage returned to normal (72%)
```

## Troubleshooting

### Bot Not Responding

**Check service status:**
```bash
sudo systemctl status proxmox-monitor.service
```

**View detailed logs:**
```bash
sudo journalctl -u proxmox-monitor.service -n 50
```

**Verify config:**
```bash
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

### Telegram Token Issues

- Verify token format: Should start with numbers followed by colon
- Check for typos in config.yaml
- Regenerate token from @BotFather if needed

### Metrics Not Collecting

**Check required commands:**
```bash
which pvesh qm pct df free uptime sensors
```

**Test manual collection:**
```bash
uptime
free -m
df -h /
pct list
qm list
```

### Can't Read Containers

**Verify Proxmox access:**
```bash
pvesh get /nodes
pct list
qm list
```

**Check permissions:**
```bash
id  # Should show root
```

### State File Issues

**Reset alert state:**
```bash
rm /opt/proxmox-monitor/state.json
sudo systemctl restart proxmox-monitor.service
```

## Maintenance

### Viewing Logs

```bash
# Last 50 lines
sudo journalctl -u proxmox-monitor.service -n 50

# Follow logs in real-time
sudo journalctl -u proxmox-monitor.service -f

# Show today's logs
sudo journalctl -u proxmox-monitor.service --since today

# Show specific time range
sudo journalctl -u proxmox-monitor.service --since "2025-01-15 10:00" --until "2025-01-15 15:00"
```

### Updating Configuration

```bash
# Edit config
sudo nano /opt/proxmox-monitor/config.yaml

# Restart service to apply changes
sudo systemctl restart proxmox-monitor.service

# Verify changes
sudo journalctl -u proxmox-monitor.service -f
```

### Stopping/Starting Service

```bash
# Stop monitoring
sudo systemctl stop proxmox-monitor.service
sudo systemctl stop proxmox-monitor.timer

# Start monitoring
sudo systemctl start proxmox-monitor.service
sudo systemctl start proxmox-monitor.timer

# Restart monitoring
sudo systemctl restart proxmox-monitor.service
```

## Advanced Configuration

### Custom Alert Thresholds

Edit thresholds in `config.yaml` for your specific needs:

```yaml
thresholds:
  cpu:
    warning: 75      # Lower threshold for sensitive environments
    critical: 90
  ram:
    warning: 80
    critical: 92
```

### Multiple Chat IDs

To send notifications to multiple chats, you'll need to modify `telegram.py` to loop through multiple chat IDs.

### Disable Specific Alerts

Edit `main.py` and comment out alert checks in `_check_and_send_alerts()`:

```python
# Don't check temperature
# alerts.extend(self.alert_generator.check_temperature())
```

## Project Structure

```
proxmox-monitor/
├── main.py                      # Entry point and main loop
├── proxmox.py                   # Metrics collection from Proxmox
├── alerts.py                    # Alert logic and deduplication
├── telegram.py                  # Telegram bot interface
├── config.yaml                  # Configuration (customize this)
├── state.json                   # Alert state (auto-generated)
├── pyproject.toml              # Project metadata and dependencies
├── README.md                    # This file
└── systemd/
    ├── proxmox-monitor.service  # systemd service unit
    └── proxmox-monitor.timer    # systemd timer unit
```

## Security Considerations

1. **Config File Permissions**: Set to 660 (readable by root and group only)
   ```bash
   chmod 660 /opt/proxmox-monitor/config.yaml
   ```

2. **Token Security**: Never commit config.yaml to git
   ```bash
   echo "config.yaml" >> .gitignore
   ```

3. **Whitelist Users**: Only add trusted Telegram user IDs
   ```yaml
   allowed_user_ids:
     - YOUR_ID_ONLY
   ```

4. **File Ownership**: Ensure root owns the files
   ```bash
   sudo chown -R root:root /opt/proxmox-monitor/
   ```

## Performance Impact

- **CPU**: < 1% (minimal background task)
- **Memory**: ~50-100 MB (Python runtime)
- **Network**: ~1-2 KB per status update
- **Disk**: < 1 MB (logs, state file)

## License

Provide license information here (MIT, GPL, etc.)

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review service logs: `journalctl -u proxmox-monitor.service`
3. Verify configuration in `config.yaml`
4. Test metrics manually with shell commands

## Changelog

### v1.0.0 - Initial Release
- Core monitoring functionality
- Telegram bot with commands
- Alert system with deduplication
- systemd integration
- Comprehensive configuration options
