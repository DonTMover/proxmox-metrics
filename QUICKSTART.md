# Quick Start Guide

## 5-Minute Setup

### Step 1: Get Telegram Bot Token (2 min)
1. Open Telegram and find `@BotFather`
2. Send `/newbot`
3. Follow prompts to create bot
4. Save the token (looks like: `123456789:ABCdefGHijkLmnoPQRstuvWxyz123456`)

### Step 2: Get Your User ID (1 min)
1. Find `@userinfobot` on Telegram
2. Send any message
3. Bot responds with your ID (e.g., `987654321`)

### Step 3: Configure (1 min)
```bash
# Edit config.yaml
nano config.yaml
```

Replace in config.yaml:
- `YOUR_BOT_TOKEN` → your bot token
- `123456789` → your user ID (in allowed_user_ids)
- `YOUR_CHAT_ID` → your user ID (or group chat ID)
- `pve` → your Proxmox node name (check with: `pvesh get /nodes`)

### Step 4: Install (1 min)
```bash
cd /opt/proxmox-monitor
sudo bash install.sh
```

### Step 5: Verify (Done!)
```bash
# View logs
journalctl -u proxmox-monitor.service -f

# Test bot - send /start in Telegram
```

## Common Tasks

### Test Bot Connection
```bash
# Send test message from command line
curl -X POST "https://api.telegram.org/botTOKEN/sendMessage" \
  -d "chat_id=CHAT_ID&text=Test"
```

### View Live Logs
```bash
sudo journalctl -u proxmox-monitor.service -f
```

### Restart Service
```bash
sudo systemctl restart proxmox-monitor.service
```

### Check Service Status
```bash
sudo systemctl status proxmox-monitor.service
sudo systemctl status proxmox-monitor.timer
```

### Get Proxmox Node Name
```bash
pvesh get /nodes
# Look for name in output
```

### Find Proxmox Container/VM IDs
```bash
# List containers
pct list

# List virtual machines
qm list
```

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Bot not responding | Check token in config.yaml |
| Can't collect metrics | Check Proxmox commands: `which pvesh qm pct` |
| Service won't start | View logs: `journalctl -u proxmox-monitor.service` |
| High CPU usage | Check Python process: `top -p $(pgrep -f "main.py")` |
| Disk space issue | Check: `df -h /opt/proxmox-monitor` |

## After Installation

1. **Customize Thresholds** - Edit `config.yaml` alert levels
2. **Add Required Containers** - Set CT/VM IDs to monitor for stopped state
3. **Test Commands** - Send /status, /vms, /alerts in Telegram
4. **Review Logs** - Check `journalctl` for any warnings

## File Permissions
```bash
# Correct permissions
ls -la /opt/proxmox-monitor/
# config.yaml should show: -rw-rw---- (660)
# other files should show: -rwxr-xr-x (755)
```

## Next Steps

- Read full documentation: [README.md](README.md)
- Configure advanced options
- Set up backup/monitoring
- Join Proxmox community forums
