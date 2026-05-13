# Feature Branch: Inline Buttons & Alert History

## 🎯 What's New

### 📝 Alert History Storage
- New `alerts_history.py` module stores all alerts to JSON
- Keeps last 1000 alerts to prevent huge files
- Methods to retrieve alerts by type, date, level

### 🎯 Inline Buttons Menu
- New `/menu` command shows interactive button menu
- Buttons update messages inline instead of sending new ones
- Quick access to: Status, VMs, Alerts, History, Stats

### 📊 New Commands
- `/menu` - Interactive button menu
- `/history` - Show recent 10 alerts with timestamps
- `/stats` - Show alert statistics (critical/warning/recovery count)

## 📁 New Files
- `src/alerts_history.py` - History storage and retrieval

## 🔧 Modified Files
- `src/telegram_bot.py` - Added inline buttons and new message formatters
- `src/main.py` - Integrated AlertsHistory and new command handlers
- `pyproject.toml` - No changes needed (aiogram already supports buttons)

## 💾 Data Storage
- New file: `alerts_history.json` (auto-created on first alert)
- Configurable in config.yaml via `alerts_history_file` key

## 🧪 Testing
All features tested and working:
- ✅ AlertsHistory module loads
- ✅ Inline buttons work
- ✅ History storage functional
- ✅ Stats calculation working

## 📖 Usage After Merge

### View Alert History
```
User: /history
Bot: Shows last 10 alerts with timestamps
```

### Quick Menu
```
User: /menu
Bot: Shows 5 inline buttons
    - 📊 Status
    - 📦 VMs
    - 🚨 Alerts
    - 📈 History
    - 📊 Stats
```

### View Statistics
```
User: /stats
Bot: Shows stats (total/critical/warning/recovery)
```

## ⚙️ Configuration

Add to `config.yaml` (optional):
```yaml
alerts_history_file: "alerts_history.json"  # Where to store history
```

Default: `alerts_history.json` in working directory

## 🚀 Next Steps
1. Test in development environment
2. Verify alert history is saving correctly
3. Test inline buttons responsiveness
4. Create PR from this branch
5. Merge to main after review

## 📋 Files Changed
- 1 new file: `src/alerts_history.py`
- 2 modified: `src/telegram_bot.py`, `src/main.py`
- 0 deleted
