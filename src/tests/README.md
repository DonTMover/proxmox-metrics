# Test Suite

## Overview

Comprehensive test suite for Proxmox Monitor with unit tests, integration tests, and fixtures for all modules.

## Structure

```
src/tests/
├── __init__.py              # Test package marker
├── conftest.py              # Shared fixtures and configuration
├── test_proxmox.py          # ProxmoxCollector tests
├── test_alerts.py           # AlertGenerator and state management tests
├── test_alerts_history.py   # AlertsHistory storage tests
├── test_telegram_bot.py     # TelegramBot and MessageFormatter tests
├── test_integration.py      # Integration tests across modules
└── README.md                # This file
```

## Installation

Install test dependencies:

```bash
uv sync --all-extras
```

Or install just dev dependencies:

```bash
uv pip install pytest pytest-asyncio pytest-cov pytest-mock
```

## Running Tests

### Run all tests
```bash
pytest src/tests/
```

### Run with coverage report
```bash
pytest src/tests/ --cov=src --cov-report=html
```

### Run specific test file
```bash
pytest src/tests/test_proxmox.py
```

### Run specific test class
```bash
pytest src/tests/test_alerts.py::TestAlertGenerator
```

### Run specific test
```bash
pytest src/tests/test_alerts.py::TestAlertGenerator::test_check_host_metrics_no_alerts
```

### Run with verbose output
```bash
pytest src/tests/ -v
```

### Run with print statements visible
```bash
pytest src/tests/ -s
```

## Test Modules

### conftest.py
Shared pytest fixtures used across all tests:
- `temp_config_file` - Temporary YAML config file
- `temp_state_file` - Temporary JSON state file  
- `temp_history_file` - Temporary JSON history file
- `mock_collector` - Mock ProxmoxCollector
- `mock_telegram_bot` - Mock TelegramBot
- `sample_alert_data` - Sample alert dictionary

### test_proxmox.py
Tests for metrics collection from Proxmox hosts:
- HostMetrics dataclass creation and calculations
- ContainerMetrics dataclass for containers/VMs
- ProxmoxCollector initialization and metric retrieval
- CPU, memory, disk, temperature, and uptime collection

### test_alerts.py
Tests for alert generation and state management:
- AlertLevel enum values
- Alert dataclass creation
- StateManager state persistence and deduplication
- ThresholdChecker for all metric types
- AlertGenerator workflow and recovery detection
- Container status checking

### test_alerts_history.py
Tests for historical alert storage and retrieval:
- HistoricalAlert dataclass
- AlertsHistory initialization and persistence
- Adding alerts to history
- Retrieving recent alerts
- Filtering by type and date
- Statistics calculation
- History clearing and size limits

### test_telegram_bot.py
Tests for Telegram bot interface:
- MessageFormatter for all message types
- Host status formatting
- Container/VM list formatting
- Alert summary and history formatting
- Statistics summary formatting
- TelegramBot initialization and user whitelist

### test_integration.py
Integration tests verifying entire workflows:
- Module imports and dependencies
- Metrics collection → alert generation
- Alert generation → history storage
- Message formatting with real data
- Threshold detection workflow
- Container status workflow
- State persistence across instances
- Alert deduplication system
- Recovery detection
- Error handling for various failure modes

## Coverage

Current test coverage includes:

| Module | Covered |
|--------|---------|
| proxmox.py | ✅ Metrics collection, dataclasses |
| alerts.py | ✅ Alert generation, thresholds, state |
| alerts_history.py | ✅ Storage, retrieval, statistics |
| telegram_bot.py | ✅ Formatting, commands, user checks |
| main.py | ⚠️ Partial (orchestration logic) |

## Writing New Tests

### Pattern for unit tests
```python
def test_feature_description(self):
    """Test specific feature"""
    # Arrange
    input_data = ...
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected
```

### Pattern for async tests
```python
@pytest.mark.asyncio
async def test_async_feature(self):
    """Test async feature"""
    result = await async_function()
    assert result is not None
```

### Using fixtures
```python
def test_with_fixture(self, temp_history_file):
    """Test using fixture"""
    history = AlertsHistory(temp_history_file)
    history.add_alert({"alert_type": "test"})
    # ... assertions
```

## Continuous Integration

These tests can be integrated into CI/CD:

```yaml
# Example GitHub Actions
- name: Run tests
  run: pytest src/tests/ --cov=src

- name: Generate coverage report
  run: pytest src/tests/ --cov=src --cov-report=xml
```

## Known Limitations

1. **Telegram Bot Tests** - Mocked due to external API dependency
2. **Proxmox Collector** - Tests use real system calls; may vary by OS
3. **Async Tests** - Require pytest-asyncio plugin
4. **File Operations** - Use temporary files; may have OS-specific behavior

## Troubleshooting

### "No module named 'src'"
Ensure you're running pytest from the project root:
```bash
cd /path/to/proxmox-metrics
pytest src/tests/
```

### "EventLoop already running"
Make sure pytest-asyncio is installed and asyncio_mode is set correctly in pyproject.toml

### "Fixture not found"
Fixtures are defined in conftest.py. Ensure it's in the tests directory and named correctly.

### ImportError for project modules
Add src/ to PYTHONPATH:
```bash
export PYTHONPATH=/path/to/proxmox-metrics/src:$PYTHONPATH
pytest
```

Or use:
```bash
uv run pytest src/tests/
```
