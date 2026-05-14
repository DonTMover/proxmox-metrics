# Release History

## v1.2.2.0 - Bug Fixes & Docker Improvements

**Release Date:** 2026-05-14  
**Status:** Latest ✅  
**Compatibility:** Docker Compose v2, Python 3.11+, Proxmox 7.x+

### 🎯 Highlights
- ✅ **Fixed Docker Module Import** - PYTHONPATH configuration for container deployments
- ✅ **Fixed Container/VM Type Separation** - Uses vm_type field instead of vmid ranges
- ✅ **Improved Reliability** - All 68 tests passing
- ✅ **Production Ready** - Tested with docker-compose

### 🐛 Bug Fixes
- **Docker Import Error** - Fixed ModuleNotFoundError in container by setting PYTHONPATH
- **Container/VM Separation** - Fixed logic that incorrectly relied on vmid ranges
  - Old: Assumed vmid < 100 = container, >= 100 = VM
  - New: Uses explicit vm_type field set by collection methods
  - Note: vmid can be 0, 1, 91, 111 for either type

### 📋 Changes
- Set PYTHONPATH=/app/src in Dockerfile ENV
- Added PYTHONPATH export to entrypoint.sh
- Updated container/VM collection methods to populate vm_type field
- Fixed check_container_vm_count() to use vm_type field
- Updated all test fixtures to include vm_type values
- Version bumped to 1.2.2.0

### 🧪 Testing
- Total Tests: **68 passed** ✅
- Docker build: ✅ Successful
- Docker run: ✅ No import errors

### 📚 Documentation
- Updated: RELEASE_NOTES.md with proper vm_type separation explanation
- Updated: pyproject.toml version to 1.2.2.0

### 🔄 Migration from v1.2.1.0
- ✅ No breaking changes
- ✅ No configuration changes required
- ✅ Fixes Docker deployment issues
- ✅ Improves reliability for container/VM detection
- ✅ Fully backward compatible

---

## v1.2.1.0 - Container/VM Monitoring & Security Updates

**Release Date:** 2026-05-14  
**Status:** Stable ✅  
**Compatibility:** Docker Compose v2, Python 3.11+, Proxmox 7.x+

### 🎯 Highlights
- ✅ **Container/VM Count Monitoring** - Periodic alerts on infrastructure changes
- ✅ **Auto-Generated Password** - Secure first-start setup with cryptographic randomness
- ✅ **Docker Compose v2 Support** - Compatible with modern Docker installations
- ✅ **68 Comprehensive Tests** - 100% test coverage for new features
- ✅ **Full Backward Compatibility** - Works with existing installations

### 📊 New Features

#### Container/VM Count Monitoring
- Monitors container and VM count every monitoring cycle (30 seconds)
- Generates informational alerts when counts change
- Separates containers and VMs using explicit type field
- Persists state across restarts in `state.json`
- Examples: "2 container(s) added (now 5 total)"

#### First-Start Password Security
- Random 12-character password generated on first startup
- Cryptographically secure using Python's `secrets` module
- Session-specific (new password on each restart)
- Admin must enter password to proceed with setup
- Password displayed prominently in console logs
- No persistence (not saved to config)

#### Docker Compose v2 Compatibility
- Fully compatible with docker compose CLI (v2+)
- Backward compatible with docker-compose (v1)
- Uses version 3.8 compose format
- Both commands work identically:
  - `docker-compose up` (v1)
  - `docker compose up` (v2)

### 📋 Changes
- Added `StateManager.get/set_container_vm_count()` methods
- Added `AlertGenerator.check_container_vm_count()` method
- Integrated count check into main monitoring loop
- Added 6 container/VM monitoring tests
- Updated 2 telegram bot tests for first-start setup
- Created 18 password generation/verification tests
- Updated version from 1.0.0 to 1.2.1.0

### 📈 Commits
```
2f4ac67 - docs: update README to mention container/VM count monitoring
4ed525f - docs: add container/VM count monitoring feature documentation
60ae25f - feat: add periodic container/VM count monitoring
08248da - docs: add comprehensive password implementation guide
ee09bc2 - test: add comprehensive tests for password generation
5fecded - feat: add auto-generated password for first-start setup
```

### 🧪 Testing
- Total Tests: **68 passed** ✅
  - Password tests: 18
  - Container/VM monitoring tests: 6
  - Integration tests: 18
  - Alert tests: 13
  - Others: 13

### 📚 Documentation
- New: `docs/updates/update-2026-05-14-container-vm-monitoring.md`
- New: `docs/updates/update-2026-05-14-auto-password.md`
- New: `docs/PASSWORD_IMPLEMENTATION.md`
- Updated: README.md

### 🔄 Migration from v1.2.1.0
- ✅ No breaking changes
- ✅ No configuration changes required
- ✅ Works with existing configs
- ✅ New features enabled automatically
- ✅ Fully backward compatible

### 🚀 Installation
```bash
# Using docker compose v2 (recommended)
docker compose up --build

# Or using docker-compose v1
docker-compose up --build

# Check logs for generated password
docker compose logs app | grep "SETUP PASSWORD"
```

---

## v1.2.0 - Production-Ready Monitoring Solution

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
