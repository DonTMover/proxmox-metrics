# Quick Start Guide - First-Start Setup

## 🚀 Get Started in 3 Steps

### Step 1: Start with Docker (Recommended for test)
```bash
cd /Users/dontmover/projects/proxmox-metrics
docker-compose up --build
```

### Step 2: Send /setup Command
Open your Telegram bot and send:
```
/setup
```

### Step 3: Follow the Inline Buttons
The bot will guide you through:
1. **Bot Token** - Copy from @BotFather
2. **Chat ID** - Click "Use My ID" button
3. **Allowed Users** - Click "Add Me" button
4. **Node Name** - Type your Proxmox node name

## 📋 What Was Created

### Code
- **src/first_start_setup.py** - Setup wizard with inline buttons
- **Dockerfile** - Container image for testing
- **docker-compose.yml** - One-command deployment

### Templates
- **config/config.empty.yaml** - Fresh config template
- **config/config.yaml** - Generated after setup

### Documentation
- **docs/DOCKER_SETUP.md** - Docker usage guide
- **docs/FIRST_START_IMPLEMENTATION.md** - Technical details

## 🌿 Git Branches

### Created
```
feature/first-start-setup
    ↓ (merged)
develop ← (current)
```

### All Branches
- `main` - Production branch
- `develop` - Development branch (contains features)
- `feature/first-start-setup` - Feature branch
- `feature/inline-buttons-alerts` - Future feature

## 🧪 Test Locally

### Without Docker
```bash
cd /Users/dontmover/projects/proxmox-metrics
uv run main.py
```

### With Docker
```bash
docker-compose up --build
docker-compose logs -f
```

## 🔐 Optional: Add Password Protection

Edit `config/config.empty.yaml`:
```yaml
setup_password: "your_secure_password"
```

Users must enter password before setup begins.

## 💾 Config File Locations

### During Development
```
config/config.yaml           # Generated after setup
config/config.empty.yaml     # Template
```

### In Production
```
/opt/proxmox-monitor/config/config.yaml
/etc/proxmox-monitor/config.yaml
```

## 📱 Available Commands

**After Setup:**
- `/start` - Welcome
- `/status` - System status
- `/vms` - List all VMs/CTs
- `/alerts` - Show active alerts
- `/menu` - Quick action buttons
- `/help` - Command list

**Always Available:**
- `/id` - Get your Telegram user ID
- `/setup` - Run setup (if not configured)

## 🎯 Inline Button Examples

```
Setup Flow:
┌─────────────────────────────────┐
│ [🔐 Enter Password] (optional)  │
├─────────────────────────────────┤
│ [📌 Use My ID] [📝 Custom ID]   │
├─────────────────────────────────┤
│ [✅ Add Me] [➕ Add More Users]  │
├─────────────────────────────────┤
│ Setup Complete → Auto Save      │
└─────────────────────────────────┘
```

## 📊 Monitor After Setup

The bot will:
- 📨 Send alerts when thresholds exceeded
- 📊 Provide status updates on demand
- 📈 Track alert history
- 🎯 Enable quick action menu

## ⚙️ Production Deployment

```bash
# Switch to develop branch
git checkout develop

# Deploy to server
cd /opt/proxmox-monitor
git clone -b develop .

# Run setup
docker-compose up

# Or use systemd
systemctl start proxmox-monitor.service
```

## 🐛 Troubleshooting

### Docker won't start
```bash
docker-compose down
docker system prune
docker-compose up --build
```

### Bot not responding
```bash
docker-compose logs
# Check bot token in config
```

### Config not found
```bash
docker-compose exec proxmox-monitor ls -la /app/config/
```

## 📚 More Information

- **Docker Setup**: See `docs/DOCKER_SETUP.md`
- **Implementation Details**: See `docs/FIRST_START_IMPLEMENTATION.md`
- **Project Structure**: See `docs/STRUCTURE.md`

## ✨ Key Features

✅ **No Manual Config** - Setup via Telegram UI
✅ **Inline Buttons** - Click instead of typing
✅ **Docker Ready** - One command to start
✅ **Password Protected** - Optional security
✅ **Auto-Save** - Config persists automatically
✅ **Multi-User** - Add multiple allowed users

---

**Ready to start?** Run: `docker-compose up --build` 🚀
