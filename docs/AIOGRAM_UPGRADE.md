# Upgrade to aiogram - What's Changed

## 🎉 Major Update: migrated from python-telegram-bot to aiogram

### What's New

#### 1. ✨ Public `/id` Command
- **Any user** can now run `/id` to get their Telegram user ID
- No authentication required!
- Makes it easy to onboard new users without admin intervention

**Before:** Only authenticated users could see IDs
**Now:** Anyone can discover their UUID in 1 command

#### 2. 🚀 Migrated to aiogram 3.x
- More modern, lightweight bot framework
- Better performance and resource efficiency
- Cleaner architecture with Router-based handlers
- Full async/await support

### How to Use the New `/id` Command

1. **Any Telegram user** sends `/id` to the bot
2. Bot responds with:
   ```
   🔑 Your Telegram ID (UUID): `123456789`
   
   Add this ID to `allowed_user_ids` in config.yaml to get access.
   ```
3. Admin adds the ID to `allowed_user_ids` in `config/config.yaml`:
   ```yaml
   telegram:
     token: "YOUR_TOKEN"
     allowed_user_ids:
       - 123456789  # ← New user's ID from /id command
       - 987654321  # ← Existing users
   ```
4. Restart the service:
   ```bash
   sudo systemctl restart proxmox-monitor.service
   ```
5. New user now has access to all commands!

### Technical Changes

#### Dependencies
- ✅ **Added**: `aiogram>=3.0.0` 
- ❌ **Removed**: `python-telegram-bot>=20.7`

#### Code Changes
- `src/telegram_bot.py` completely rewritten for aiogram
- Uses `Router` and `CommandHandler` instead of `Application`
- Async message handling improved
- Better error handling and logging

#### Compatibility
- ✅ All existing commands still work
- ✅ Same configuration format (no changes needed)
- ✅ Same message formatting
- ✅ Same alert system

### Installation

#### If you're upgrading:

```bash
# Navigate to project directory
cd /opt/proxmox-monitor

# Update dependencies
uv sync

# Restart the service
sudo systemctl restart proxmox-monitor.service

# Verify it works
sudo systemctl status proxmox-monitor.service
```

#### If this is a fresh install:

Follow the normal [QUICKSTART.md](QUICKSTART.md) - aiogram is already in dependencies!

### Available Commands

| Command | Auth Required | Purpose |
|---------|---------------|---------|
| `/id` | ❌ **NO** | Get your Telegram user ID (anyone can use!) |
| `/start` | ✅ Yes | Welcome message |
| `/status` | ✅ Yes | Show host metrics |
| `/vms` | ✅ Yes | List containers/VMs |
| `/alerts` | ✅ Yes | Show active alerts |
| `/help` | ✅ Yes | Show commands |

### Why aiogram?

✅ **Lighter weight** - Fewer dependencies
✅ **Better performance** - Optimized async
✅ **More active** - Modern maintenance
✅ **Cleaner code** - Router-based architecture
✅ **Better typing** - Full type hints

### Troubleshooting

#### Bot not responding?
```bash
# Check logs
sudo journalctl -u proxmox-monitor.service -f

# Restart
sudo systemctl restart proxmox-monitor.service
```

#### User can't access commands?
1. User runs `/id` to get their ID
2. You add ID to `config/config.yaml`
3. You restart service: `sudo systemctl restart proxmox-monitor.service`
4. User tries again

#### Command not found?
- Make sure bot token is valid
- Make sure service is running: `sudo systemctl status proxmox-monitor.service`

### Questions?

See [docs/README.md](README.md) for full documentation.

---

**Version**: 1.0.1 | **Updated**: May 2026 | **Framework**: aiogram 3.x
