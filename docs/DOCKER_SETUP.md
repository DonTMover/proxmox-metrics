# Docker Setup & First-Start Configuration

This guide explains how to use Docker to test and deploy Proxmox Monitor with the new first-start setup feature.

## Quick Start with Docker Compose

### 1. Build and Run

```bash
docker-compose up --build
```

This will:
- Build the Docker image
- Create a container named `proxmox-monitor-test`
- Mount volumes for config, state, and logs
- Run the application

### 2. First-Time Setup

When running for the first time, the bot will be in setup mode. Send `/setup` command to @proxmox_monitor_bot:

```
/setup
```

The bot will guide you through:
1. **Bot Token** - Your Telegram bot token from @BotFather
2. **Chat ID** - Where to send alerts (uses your ID or custom ID)
3. **Allowed Users** - Who can access commands
4. **Proxmox Node** - The node name to monitor

### 3. Configuration Files

#### `config.empty.yaml` (Development Template)
Used when starting fresh. Contains:
- Empty telegram token
- No allowed user IDs
- No chat ID set
- All thresholds preconfigured

#### `config.yaml` (Generated During Setup)
Auto-generated after first-start setup with:
- Your bot token
- Your chat ID
- List of allowed user IDs
- Monitoring configuration

## Docker Compose Structure

```yaml
volumes:
  - ./config:/app/config           # Config files persist
  - ./state.json:/app/state.json   # Monitor state
  - ./alerts_history.json:/app/alerts_history.json  # Alert history
  - ./logs:/var/log                # Application logs
```

## Manual Docker Build

```bash
# Build image
docker build -t proxmox-monitor:latest .

# Run with config volume
docker run -it \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/state.json:/app/state.json \
  -v $(pwd)/alerts_history.json:/app/alerts_history.json \
  --name proxmox-monitor \
  proxmox-monitor:latest
```

## Setup Commands

### /setup
Start the first-time setup wizard with inline buttons:
- **Step 1**: Enter bot token
- **Step 2**: Choose chat ID (your ID or custom)
- **Step 3**: Add allowed users
- **Step 4**: Configure Proxmox node

### /id
Get your Telegram user ID (works before setup)

### /help
View available commands (after setup)

### /menu
Quick action menu with inline buttons

## Environment Variables

Set in `docker-compose.yml` or `.env` file:

```yaml
environment:
  - PYTHONUNBUFFERED=1      # Unbuffered Python output
  - LOG_LEVEL=INFO          # Logging level
  - PROXMOX_BOT_TOKEN=      # Optional: Telegram bot token
```

### Bot Token Environment Variable

**Feature:** Pass bot token directly to Docker for automated setup.

**Usage Option 1: .env file (Recommended)**
```bash
# Create .env file
echo "PROXMOX_BOT_TOKEN=123456789:ABCDefghijklmnop" > .env

# Run docker-compose
docker-compose up --build
```

**Usage Option 2: docker-compose.yml**
```yaml
environment:
  - PROXMOX_BOT_TOKEN=123456789:ABCDefghijklmnop
```

**Usage Option 3: Command line**
```bash
PROXMOX_BOT_TOKEN="123456789:ABCDefghijklmnop" docker-compose up
```

**Result:** If `PROXMOX_BOT_TOKEN` is set, config will be auto-populated with token and setup skips token entry.

## Inline Button Examples

The setup uses inline buttons for:
- ✅ Use My ID / ➕ Add More Users
- 📝 Enter Token / 🔐 Password
- 📊 Status / 📦 VMs / 🚨 Alerts

All managed via callback queries.

## Password Protection (Optional)

To add password protection to setup:

1. Edit `config/config.empty.yaml`
2. Set `setup_password: "your_secure_password"`
3. Users must enter password before setup

## Testing Workflow

1. **Start container**: `docker-compose up`
2. **Send /setup**: In Telegram bot chat
3. **Follow prompts**: Answer inline button questions
4. **Config saved**: Automatically written to `config/config.yaml`
5. **Monitor starts**: When setup completes

## Logs

View logs from container:

```bash
# Docker Compose
docker-compose logs -f

# Docker directly
docker logs -f proxmox-monitor-test
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs
```

### Config not found
Check volume mounts:
```bash
docker-compose exec proxmox-monitor ls -la /app/config/
```

### Bot token invalid
Re-run `/setup` and enter correct token from @BotFather

## Security Notes

- Container runs with dropped capabilities
- Read-only filesystem (except /tmp and /run)
- Logs mounted to host for persistence
- Sensitive config not exposed in environment

## Next Steps

1. Deploy to production server
2. Configure Proxmox API access
3. Add alert thresholds to config
4. Set up systemd service for auto-start
