# Deployment Guide

## Pre-Deployment Checklist

- [ ] Proxmox VE 7.x+ is installed and running
- [ ] Python 3.11+ is available on the host
- [ ] Telegram bot token obtained from @BotFather
- [ ] Your Telegram user ID
- [ ] SSH access to Proxmox host with root permissions
- [ ] Internet connectivity from Proxmox host to Telegram API

## Step-by-Step Deployment

### Phase 1: Preparation (10 minutes)

#### 1.1 Create Telegram Bot
1. Open Telegram → Search: `@BotFather`
2. Send: `/newbot`
3. Enter bot name: "Proxmox Monitor" (can be anything)
4. Enter bot username: "proxmox_monitor_123" (must be unique)
5. Save the token → `YOUR_BOT_TOKEN`

#### 1.2 Get Your Telegram ID
1. Search: `@userinfobot`
2. Send any message
3. Bot responds with your ID → `YOUR_USER_ID`

#### 1.3 Create Chat (Optional - for group notifications)
1. Create new group or channel
2. Add your bot to it
3. Send a message
4. Find chat ID in logs or use API

### Phase 2: Installation (15 minutes)

#### 2.1 SSH into Proxmox Host
```bash
ssh root@proxmox.example.com
```

#### 2.2 Create Installation Directory
```bash
mkdir -p /opt/proxmox-monitor
cd /opt/proxmox-monitor
```

#### 2.3 Clone or Copy Project Files
**Option A: Git Clone (recommended)**
```bash
git clone https://github.com/yourusername/proxmox-monitor.git .
cd proxmox-monitor
```

**Option B: SCP from Local Machine**
```bash
# From your local machine
scp -r proxmox-monitor/* root@proxmox.example.com:/opt/proxmox-monitor/
```

#### 2.4 Verify Required Commands
```bash
# Check if Proxmox commands are available
which pvesh qm pct df free uptime
```

#### 2.5 Install Python 3.11+ (if needed)
```bash
# Check version
python3 --version

# If < 3.11, update
apt update
apt install python3.11 python3.11-venv
```

### Phase 3: Configuration (10 minutes)

#### 3.1 Edit Configuration
```bash
cd /opt/proxmox-monitor
nano config.yaml
```

#### 3.2 Replace Configuration Values

```yaml
# Replace these:
telegram:
  token: "YOUR_BOT_TOKEN"           # <- Paste bot token
  allowed_user_ids:
    - YOUR_USER_ID                  # <- Paste your user ID
  chat_id: YOUR_USER_ID             # <- Same as above, or group ID

proxmox:
  node: "pve"                        # <- Check with: pvesh get /nodes
  required_cts:
    - 101                            # <- Add your CTs
  required_vms:
    - 200                            # <- Add your VMs
```

#### 3.3 Verify Configuration
```bash
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

#### 3.4 Set Permissions
```bash
chmod 660 config.yaml
chmod 755 main.py proxmox.py alerts.py telegram.py
```

### Phase 4: Environment Setup (10 minutes)

#### 4.1 Install uv Package Manager
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

#### 4.2 Create Python Environment
```bash
cd /opt/proxmox-monitor
uv venv
source .venv/bin/activate
uv add python-telegram-bot pyyaml psutil
```

#### 4.3 Verify Installation
```bash
python3 health_check.py
```

Expected output:
```
✓ Python modules
✓ System commands
✓ Proxmox access
✓ All checks passed!
```

### Phase 5: systemd Setup (10 minutes)

#### 5.1 Install systemd Units
```bash
# Copy service files
sudo cp systemd/proxmox-monitor.service /etc/systemd/system/
sudo cp systemd/proxmox-monitor.timer /etc/systemd/system/

# Set permissions
sudo chmod 644 /etc/systemd/system/proxmox-monitor.*

# Update paths in service file
sudo sed -i "s|WorkingDirectory=.*|WorkingDirectory=/opt/proxmox-monitor|g" /etc/systemd/system/proxmox-monitor.service
sudo sed -i "s|ExecStart=.*|ExecStart=/opt/proxmox-monitor/.venv/bin/python3 main.py|g" /etc/systemd/system/proxmox-monitor.service
```

#### 5.2 Reload and Enable
```bash
sudo systemctl daemon-reload
sudo systemctl enable proxmox-monitor.service
sudo systemctl enable proxmox-monitor.timer
```

#### 5.3 Start Services
```bash
sudo systemctl start proxmox-monitor.service
sudo systemctl start proxmox-monitor.timer
```

### Phase 6: Verification (5 minutes)

#### 6.1 Check Service Status
```bash
sudo systemctl status proxmox-monitor.service
sudo systemctl status proxmox-monitor.timer
```

Expected: `active (running)` and `active (waiting)`

#### 6.2 Verify Telegram Connection
```bash
# View live logs
sudo journalctl -u proxmox-monitor.service -f
```

Look for: `Telegram bot initialized` and similar messages

#### 6.3 Test Bot Commands
Open Telegram and send to your bot:
- `/start` - Should see welcome message
- `/id` - Should see your user ID
- `/status` - Should see host metrics
- `/vms` - Should see container list

#### 6.4 Wait for First Summary
Summaries are sent every 5 minutes (configurable).
Check `/alerts` command to see if any issues were detected.

### Phase 7: Post-Deployment (5 minutes)

#### 7.1 Monitor Initial Operation
```bash
# Watch logs for 2-3 cycles
sudo journalctl -u proxmox-monitor.service -n 50 -f
```

#### 7.2 Customize Thresholds
Edit `/opt/proxmox-monitor/config.yaml`:
- Adjust alert thresholds for your environment
- Set summary frequency
- Add additional CTs/VMs to monitor

#### 7.3 Restart After Changes
```bash
sudo systemctl restart proxmox-monitor.service
```

#### 7.4 Schedule Log Rotation
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/proxmox-monitor
```

Add:
```
/var/log/proxmox-monitor.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload proxmox-monitor.service > /dev/null 2>&1 || true
    endscript
}
```

## Automated Installation Script

For faster deployment, use the provided installation script:

```bash
cd /opt/proxmox-monitor
sudo bash install.sh
```

This automates:
- Python environment setup
- uv installation
- systemd configuration
- Service startup
- Health verification

## Deployment Troubleshooting

### Service Won't Start

**Check logs:**
```bash
journalctl -u proxmox-monitor.service -n 100
```

**Common issues:**
- Python not found: Check shebang in main.py
- Module not found: Run `uv sync` again
- Permission denied: Check file permissions

### Bot Not Receiving Messages

**Verify token:**
```bash
curl -s "https://api.telegram.org/botTOKEN/getMe" | grep ok
# Should return: "ok":true
```

**Check chat ID:**
```bash
curl -s "https://api.telegram.org/botTOKEN/getUpdates"
```

**Verify config:**
```bash
grep -A 5 "telegram:" config.yaml
```

### Metrics Not Collecting

**Test commands manually:**
```bash
pvesh get /nodes
pct list
qm list
free -m
df -h /
```

**Check permissions:**
```bash
id
# Should show: uid=0(root)
```

### Service Crashes

**Increase verbosity:**
```bash
# Edit main.py logging level from INFO to DEBUG
sed -i 's/logging.INFO/logging.DEBUG/' main.py
systemctl restart proxmox-monitor.service
```

**Check resource usage:**
```bash
ps aux | grep main.py
top -p $(pgrep -f main.py)
```

## Rollback Procedure

If issues occur, rollback is simple:

```bash
# Stop services
sudo systemctl stop proxmox-monitor.service
sudo systemctl stop proxmox-monitor.timer
sudo systemctl disable proxmox-monitor.service
sudo systemctl disable proxmox-monitor.timer

# Remove (or backup)
sudo rm -rf /opt/proxmox-monitor
# or:
# sudo mv /opt/proxmox-monitor /opt/proxmox-monitor.backup

# Remove systemd units
sudo rm /etc/systemd/system/proxmox-monitor.*
sudo systemctl daemon-reload
```

## Production Recommendations

### 1. Set Up Backups
```bash
# Backup configuration daily
sudo cp /opt/proxmox-monitor/config.yaml \
        /opt/proxmox-monitor/config.yaml.backup.$(date +%Y%m%d)
```

### 2. Monitor the Monitor
Set up monitoring for the monitor service itself:
```bash
# Create alert if service stops
systemctl status proxmox-monitor.service || systemctl start proxmox-monitor.service
```

### 3. Optimize Performance
- Adjust `summary_interval` based on needs
- Increase `alert_repeat` to reduce spam
- Monitor memory/CPU usage

### 4. Security Hardening
- Restrict SSH access to trusted IPs
- Use SSH keys instead of passwords
- Enable firewall rules
- Regular security updates

### 5. Redundancy
- Set up second monitor instance on different host
- Share same chat ID for unified notifications
- Test failover procedures

## Update Procedure

To update to newer versions:

```bash
# Backup current version
sudo cp -r /opt/proxmox-monitor /opt/proxmox-monitor.v1

# Download new version
cd /tmp
git clone https://github.com/yourusername/proxmox-monitor.git new-monitor

# Copy updated files (keeping config.yaml)
sudo cp new-monitor/*.py /opt/proxmox-monitor/
sudo cp new-monitor/systemd/* /etc/systemd/system/

# Update dependencies
cd /opt/proxmox-monitor
uv sync

# Restart
sudo systemctl daemon-reload
sudo systemctl restart proxmox-monitor.service

# Verify
sudo systemctl status proxmox-monitor.service
```

## Monitoring After Deployment

### Weekly Checks
- [ ] Verify bot is responsive
- [ ] Check for any warnings in logs
- [ ] Review alert accuracy

### Monthly Tasks
- [ ] Audit access logs
- [ ] Update thresholds if needed
- [ ] Backup configuration

### Quarterly
- [ ] Performance review
- [ ] Update Python packages
- [ ] Test disaster recovery

## Support & Documentation

- Full docs: [README.md](README.md)
- Configuration: [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)
- Quick setup: [QUICKSTART.md](QUICKSTART.md)
- Troubleshooting: See README section
