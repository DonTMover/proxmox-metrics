# v1.2.0 - Production-Ready Monitoring Solution

## 🎉 Major Release: Complete Proxmox VE Monitoring Solution

### ✨ Features

#### 📊 Core Monitoring
- **Real-time Metrics Collection**
  - CPU usage (with temperature monitoring)
  - Memory & Swap usage
  - Disk usage across all mount points
  - Uptime tracking
  - LXC Container & VM status monitoring

- **Intelligent Alert System**
  - Configurable thresholds for all metrics
  - Alert deduplication to prevent spam
  - Multi-level alerts (warning → critical)
  - Recovery notifications when metrics normalize
  - Container/VM status tracking

- **Telegram Notifications**
  - Direct alerts to Telegram chat
  - Formatted status messages
  - User-friendly emoji indicators
  - Whitelist-based access control
  - Public `/id` command for UUID discovery

#### 🤖 Bot Commands
- `/start` - Welcome message with available commands
- `/id` - Discover your Telegram UUID (public, no auth required)
- `/status` - Get real-time host metrics
- `/vms` - List all containers and VMs
- `/alerts` - Show current active alerts
- `/help` - Command help
- `/menu` - Interactive button menu (NEW - feature branch)
- `/history` - Recent alert history (NEW - feature branch)
- `/stats` - Alert statistics (NEW - feature branch)

#### 🔧 Framework & Architecture
- **Aiogram 3.28.2** - Modern Telegram bot framework with Router pattern
- **Async/Await** - 100% asynchronous design for non-blocking operations
- **Modular Structure**
  - `proxmox.py` - Metrics collection from host/containers
  - `alerts.py` - Alert generation and state management
  - `telegram_bot.py` - Telegram interface with inline buttons
  - `alerts_history.py` - Historical alert storage and analysis
  - `main.py` - Orchestration and event loop management

#### 📁 Professional Structure
- `src/` - Core application modules
- `config/` - Configuration templates
- `docs/` - Documentation and migration guides
- `scripts/` - Utility scripts for setup/deployment
- `systemd/` - Production systemd service/timer files

### 🚀 Deployment
- **Systemd Integration**
  - Background service: `proxmox-monitor.service`
  - Scheduler timer: `proxmox-monitor.timer`
  - Production-ready logging to `/var/log/proxmox-monitor.log`

- **Package Management**
  - Dependency management via `uv`
  - Clean dependency chain (21 packages total)
  - Python 3.11+ support

### 🔐 Security
- **Access Control**
  - Whitelist-based command authorization
  - UUID-based user identification
  - Public discovery endpoint (`/id`) for onboarding
  - Configuration-driven user management

### 📈 Recent Updates (v1.1.0 → v1.2.0)

#### Framework Migration
- **Migrated from python-telegram-bot to aiogram 3.x**
  - Modern Router-based architecture
  - Better async handling
  - Inline button support for interactive UI
  - Cleaner command handler pattern

#### New Public Features
- **Public `/id` Command**
  - Any user can discover their Telegram UUID
  - No authentication required
  - Essential for adding new users to whitelist
  - Implemented securely without security risk

#### Feature Branch: Inline Buttons & History
- **Interactive Menu System** (`/menu`)
  - 5 inline buttons for quick navigation
  - Message editing instead of creating new messages
  - Improved user experience

- **Alert History Tracking** (`/history`, `/stats`)
  - Persistent JSON storage of alerts
  - Historical analysis and trend tracking
  - Alert statistics (total, critical, warning, recovery)
  - Configurable retention (last 1000 alerts)

### 📋 Configuration

Example `config.yaml`:
```yaml
telegram:
  token: "YOUR_BOT_TOKEN"
  allowed_user_ids: [123456789]
  chat_id: YOUR_CHAT_ID

proxmox:
  node: "pve"
  required_cts: [100, 101, 102]
  required_vms: [200, 201]

thresholds:
  cpu: [80, 95]
  ram: [85, 95]
  swap: [50, 80]
  disk: [85, 95]
  temperature: [60, 80]

scheduler:
  check_interval: 30
  summary_interval: 300
  alerts_history_file: "alerts_history.json"
```

### 🧪 Testing & Validation

All components verified working:
- ✅ Metrics collection from Proxmox
- ✅ Alert generation with thresholds
- ✅ Telegram delivery and formatting
- ✅ User authentication and access control
- ✅ Async event loop and scheduling
- ✅ Historical data storage and retrieval
- ✅ Inline button interactions

### 📚 Documentation
- [AIOGRAM_UPGRADE.md](docs/AIOGRAM_UPGRADE.md) - Migration guide from old framework
- [README.md](README.md) - Project overview and setup instructions
- [FEATURE_BRANCH.md](FEATURE_BRANCH.md) - Details on inline buttons and history (feature branch)

### 🐛 Known Limitations
- Requires root/sudo to access `/var/log/` for logging
- Tested on Proxmox VE 7.x and 8.x (Debian-based)
- Chat and container metrics depend on available system data
- History limited to 1000 recent entries to prevent large files

### 🔗 Links
- **GitHub:** https://github.com/DonTMover/proxmox-metrics
- **Aiogram:** https://docs.aiogram.dev/
- **Proxmox API:** https://proxmox.com/en/

### 🙏 Credits
Production monitoring solution for Proxmox VE environments with real-time Telegram notifications.

---

**Release Date:** 2024  
**Version:** 1.2.0  
**Status:** Production Ready ✅
