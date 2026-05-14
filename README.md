# Proxmox VE Telegram Monitor

**Production-ready Python monitoring solution** for Proxmox VE hosts with:
- 📊 Real-time system metrics (CPU, RAM, Disk, Uptime, Temperature)
- 🤖 Telegram bot with interactive commands
- 🚨 Intelligent alert system with deduplication
- 📨 Periodic status summaries
- 🔐 Whitelist-based access control

## Quick Start

```bash
# 1. Configure
nano config/config.yaml

# 2. Install
sudo bash scripts/install.sh

# 3. Start
sudo systemctl start proxmox-monitor.service
```

## Documentation

📚 **Full Documentation** → [`docs/README.md`](docs/README.md)

Quick navigation:
- **5-minute setup** → [`docs/QUICKSTART.md`](docs/QUICKSTART.md)
- **Project structure** → [`docs/STRUCTURE.md`](docs/STRUCTURE.md)
- **Configuration options** → [`docs/CONFIG_REFERENCE.md`](docs/CONFIG_REFERENCE.md)
- **Production deployment** → [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)
- **Tech architecture** → [`docs/PROJECT_SUMMARY.md`](docs/PROJECT_SUMMARY.md)
- **Doc index** → [`docs/INDEX.md`](docs/INDEX.md)

## Directory Structure

```
proxmox-metrics/
├── 📁 src/              # Python source code
├── 📁 docs/             # All documentation (8 files)
├── 📁 config/           # Configuration files
├── 📁 scripts/          # Utility scripts
├── 📁 systemd/          # Systemd units
├── main.py              # Entry point
└── pyproject.toml       # Dependencies
```

For detailed structure → see [`docs/STRUCTURE.md`](docs/STRUCTURE.md)

## Features

### Monitoring
- ✅ CPU, RAM, Swap, Disk usage
- ✅ Container/VM status
- ✅ Container/VM count tracking (alerts on changes)
- ✅ System uptime & temperature
- ✅ Custom alert thresholds

### Notifications
- 📨 Periodic summaries
- 🚨 Smart alerts (no spam!)
- ✅ Recovery notifications
- 🔔 Alert deduplication

### Telegram Commands
- `/status` - System status
- `/vms` - Container/VM list
- `/alerts` - Active alerts
- `/id` - Your user ID
- `/help` - Help

## Requirements

- Proxmox VE 7.x+ (Debian-based)
- Python 3.11+
- `uv` package manager
- Root access (for metrics)

## Installation

### Option 1: Automated (Recommended)
```bash
cd /opt/proxmox-monitor
sudo bash scripts/install.sh
```

### Option 2: Manual
See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

## Configuration

Edit config file:
```bash
nano config/config.yaml
```

Key sections:
- `telegram` - Bot token & user IDs
- `proxmox` - Host node name
- `thresholds` - Alert levels
- `scheduler` - Timing

Full reference → [`docs/CONFIG_REFERENCE.md`](docs/CONFIG_REFERENCE.md)

## Running

```bash
# Test run
python3 main.py

# As systemd service
sudo systemctl start proxmox-monitor.service
sudo systemctl status proxmox-monitor.service

# View logs
sudo journalctl -u proxmox-monitor.service -f
```

## Health Check

Before deployment:
```bash
python3 scripts/health_check.py
```

## Troubleshooting

Common issues:
- **Bot not responding** → Check `config.yaml` token & user IDs
- **No metrics** → Run as root, check Proxmox access
- **Telegram errors** → Verify internet, bot token validity

Full troubleshooting → [`docs/README.md#troubleshooting`](docs/README.md#troubleshooting)

## Architecture

**Components:**
- `src/proxmox.py` - Metrics collection
- `src/alerts.py` - Alert logic & deduplication
- `src/telegram.py` - Telegram bot interface
- `src/main.py` - Orchestrator & event loop

See [`docs/PROJECT_SUMMARY.md`](docs/PROJECT_SUMMARY.md) for details

## Performance

- **Memory:** ~50MB base
- **CPU:** <1% idle
- **Metrics collection:** ~2-3 seconds
- **Alert check:** ~1 second
- **Network:** Minimal (only Telegram)

## Security

- 🔐 Whitelist-based access (allowed_user_ids)
- 🔒 Config file permissions (mode 660)
- 🛡️ No sensitive data in logs
- 🔑 Token stored only locally

## License

Built for production use on Proxmox VE

## Support

- **Docs:** Start with [`docs/README.md`](docs/README.md)
- **FAQ:** See [`docs/README.md#troubleshooting`](docs/README.md#troubleshooting)
- **Setup Help:** [`docs/QUICKSTART.md`](docs/QUICKSTART.md)

---

**Version:** 1.0.0 | **Python:** 3.11+ | **Status:** Production Ready ✅
