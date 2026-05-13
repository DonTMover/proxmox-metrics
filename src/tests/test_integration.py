"""Integration tests for Proxmox Monitor"""
import pytest


class TestModuleImports:
    """Test that all modules can be imported"""
    
    def test_import_proxmox(self):
        """Test importing proxmox module"""
        from proxmox import ProxmoxCollector, HostMetrics, ContainerMetrics
        assert ProxmoxCollector is not None
    
    def test_import_alerts(self):
        """Test importing alerts module"""
        from alerts import Alert, AlertLevel, StateManager
        assert Alert is not None
        assert AlertLevel is not None
    
    def test_import_alerts_history(self):
        """Test importing alerts_history module"""
        from alerts_history import AlertsHistory
        assert AlertsHistory is not None
    
    def test_import_telegram_bot(self):
        """Test importing telegram_bot module"""
        from telegram_bot import TelegramBot, MessageFormatter
        assert TelegramBot is not None
        assert MessageFormatter is not None


class TestModuleIntegration:
    """Test module integration workflows"""
    
    def test_alert_flow(self, temp_history_file):
        """Test alert creation and storage flow"""
        from alerts import Alert
        from alerts_history import AlertsHistory
        
        # Create alert
        alert = Alert(
            alert_type="test",
            level="warning",
            message="Test alert"
        )
        
        # Store in history
        history = AlertsHistory(temp_history_file)
        history.add_alert({
            "alert_type": alert.alert_type,
            "level": alert.level,
            "message": alert.message
        })
        
        # Retrieve
        recent = history.get_recent_alerts(1)
        assert len(recent) == 1
        assert recent[0]["alert_type"] == "test"
    
    def test_state_persistence_flow(self, temp_state_file):
        """Test state persistence across components"""
        from alerts import StateManager
        
        manager1 = StateManager(temp_state_file)
        manager1.set_last_alert_time("cpu_test")
        time1 = manager1.get_last_alert_time("cpu_test")
        
        manager2 = StateManager(temp_state_file)
        time2 = manager2.get_last_alert_time("cpu_test")
        
        assert time1 == time2


class TestMessageFormatting:
    """Test message formatting integration"""
    
    def test_formatter_methods_exist(self):
        """Test that all formatter methods exist"""
        from telegram_bot import MessageFormatter
        
        assert hasattr(MessageFormatter, 'host_status')
        assert hasattr(MessageFormatter, 'containers_list')
        assert hasattr(MessageFormatter, 'alerts_summary')
        assert hasattr(MessageFormatter, 'alerts_history')
        assert hasattr(MessageFormatter, 'stats_summary')


class TestErrorHandling:
    """Test error handling in modules"""
    
    def test_state_file_creation(self, temp_state_file):
        """Test that state file is created if missing"""
        from alerts import StateManager
        
        # File should be created by StateManager
        manager = StateManager(temp_state_file)
        assert temp_state_file.exists()
    
    def test_history_file_creation(self, temp_history_file):
        """Test that history file is created if missing"""
        from alerts_history import AlertsHistory
        
        # File should be created by AlertsHistory
        history = AlertsHistory(temp_history_file)
        assert temp_history_file.exists()


class TestDataStructures:
    """Test core data structures"""
    
    def test_alert_dataclass(self):
        """Test Alert dataclass creation"""
        from alerts import Alert
        import time
        
        alert = Alert(
            alert_type="cpu",
            level="critical",
            message="High CPU"
        )
        
        assert alert.alert_type == "cpu"
        assert alert.level == "critical"
        assert alert.timestamp is not None
    
    def test_alert_level_enum(self):
        """Test AlertLevel enum values"""
        from alerts import AlertLevel
        
        levels = [
            AlertLevel.INFO,
            AlertLevel.WARNING,
            AlertLevel.CRITICAL,
            AlertLevel.RECOVERY
        ]
        
        assert len(levels) == 4
        for level in levels:
            assert isinstance(level.value, str)
    
    def test_host_metrics_structure(self):
        """Test HostMetrics dataclass structure"""
        from proxmox import HostMetrics
        
        metrics = HostMetrics(
            cpu_percent=50.0,
            cpu_load_1=2.0,
            cpu_load_5=2.0,
            cpu_load_15=2.0,
            ram_used_mb=1024,
            ram_total_mb=2048,
            swap_used_mb=256,
            swap_total_mb=1024,
            uptime_days=1,
            uptime_hours=2,
            uptime_minutes=30,
            disks={}
        )
        
        assert metrics.cpu_percent == 50.0
        assert metrics.ram_total_mb == 2048
    
    def test_container_metrics_structure(self):
        """Test ContainerMetrics dataclass structure"""
        from proxmox import ContainerMetrics
        
        container = ContainerMetrics(
            vmid=100,
            name="test-ct",
            status="running",
            cpu_percent=25.0,
            ram_mb=512,
            max_ram_mb=1024
        )
        
        assert container.vmid == 100
        assert container.status == "running"


class TestConfigManagement:
    """Test configuration management"""
    
    def test_telegram_bot_whitelist(self):
        """Test user whitelist functionality"""
        from telegram_bot import TelegramBot
        
        bot = TelegramBot(
            token="test",
            allowed_user_ids=[123, 456],
            chat_id=789
        )
        
        assert bot._is_allowed_user(123)
        assert bot._is_allowed_user(456)
        assert not bot._is_allowed_user(999)
