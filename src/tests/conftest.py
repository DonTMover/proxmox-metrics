"""Pytest configuration and fixtures"""
import pytest
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_config_file():
    """Create temporary config file for testing"""
    config = {
        "telegram": {
            "token": "test_token_123",
            "allowed_user_ids": [123456789],
            "chat_id": 987654321
        },
        "proxmox": {
            "node": "pve",
            "required_cts": [100, 101],
            "required_vms": [200, 201]
        },
        "thresholds": {
            "cpu": [80, 95],
            "ram": [85, 95],
            "swap": [50, 80],
            "disk": [85, 95],
            "temperature": [60, 80]
        },
        "scheduler": {
            "check_interval": 30,
            "summary_interval": 300
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump(config, f)
        temp_path = f.name
    
    yield Path(temp_path)
    
    # Cleanup
    Path(temp_path).unlink()


@pytest.fixture
def temp_state_file():
    """Create temporary state file for testing"""
    state_file = Path(tempfile.gettempdir()) / "test_state.json"
    state_file.write_text("{}")
    
    yield state_file
    
    # Cleanup
    state_file.unlink(missing_ok=True)


@pytest.fixture
def temp_history_file():
    """Create temporary history file for testing"""
    history_file = Path(tempfile.gettempdir()) / "test_alerts_history.json"
    history_file.write_text("[]")
    
    yield history_file
    
    # Cleanup
    history_file.unlink(missing_ok=True)


@pytest.fixture
def mock_collector():
    """Mock ProxmoxCollector"""
    from proxmox import HostMetrics, ContainerMetrics
    
    collector = MagicMock()
    
    # Mock host metrics
    host_metrics = HostMetrics(
        cpu_percent=45.5,
        ram_used_mb=8192,
        ram_total_mb=16384,
        swap_used_mb=512,
        swap_total_mb=2048,
        uptime_seconds=86400,
        temperature=42.0,
        disks={
            "/": {"used_gb": 50, "total_gb": 100, "percent": 50},
            "/var": {"used_gb": 10, "total_gb": 50, "percent": 20}
        }
    )
    collector.get_host_metrics.return_value = host_metrics
    
    # Mock containers
    containers = [
        ContainerMetrics(vmid=100, name="web-server", status="running", mem_mb=2048),
        ContainerMetrics(vmid=101, name="db-server", status="running", mem_mb=4096),
        ContainerMetrics(vmid=200, name="vm-test", status="stopped", mem_mb=0)
    ]
    collector.get_all_containers_and_vms.return_value = containers
    
    return collector


@pytest.fixture
def mock_telegram_bot():
    """Mock TelegramBot"""
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=True)
    bot.send_alert = AsyncMock(return_value=True)
    bot.initialize = AsyncMock(return_value=True)
    bot.start = AsyncMock()
    
    return bot


@pytest.fixture
def sample_alert_data():
    """Sample alert data for testing"""
    return {
        "alert_type": "cpu",
        "level": "warning",
        "message": "CPU usage is high",
        "metric_value": 85.5,
        "threshold": 80.0,
        "container_id": None,
        "container_name": None
    }
