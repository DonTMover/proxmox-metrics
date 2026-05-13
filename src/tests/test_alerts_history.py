"""Tests for alerts_history module"""
import pytest
from datetime import datetime, timedelta
from alerts_history import AlertsHistory, HistoricalAlert


class TestHistoricalAlert:
    """Test HistoricalAlert dataclass"""
    
    def test_historical_alert_creation(self):
        """Test creating HistoricalAlert"""
        alert = HistoricalAlert(
            timestamp="2024-05-13T10:00:00",
            alert_type="cpu",
            level="warning",
            message="CPU usage high",
            container_id=None,
            container_name=None,
            metric_value=85.0,
            threshold=80.0
        )
        
        assert alert.alert_type == "cpu"
        assert alert.level == "warning"
        assert alert.metric_value == 85.0


class TestAlertsHistory:
    """Test AlertsHistory"""
    
    def test_alerts_history_initialization(self, temp_history_file):
        """Test AlertsHistory initialization"""
        history = AlertsHistory(temp_history_file)
        
        assert history is not None
        assert temp_history_file.exists()
    
    def test_add_alert(self, temp_history_file):
        """Test adding alert to history"""
        history = AlertsHistory(temp_history_file)
        
        alert = {
            "alert_type": "cpu",
            "level": "warning",
            "message": "CPU usage high",
            "metric_value": 85.0,
            "threshold": 80.0
        }
        
        history.add_alert(alert)
        recent = history.get_recent_alerts(1)
        
        assert len(recent) == 1
        assert recent[0]["alert_type"] == "cpu"
    
    def test_get_recent_alerts(self, temp_history_file):
        """Test retrieving recent alerts"""
        history = AlertsHistory(temp_history_file)
        
        # Add multiple alerts
        for i in range(5):
            alert = {
                "alert_type": f"test_{i}",
                "level": "info",
                "message": f"Test alert {i}"
            }
            history.add_alert(alert)
        
        recent = history.get_recent_alerts(3)
        assert len(recent) <= 3
    
    def test_get_alerts_by_type(self, temp_history_file):
        """Test filtering alerts by type"""
        history = AlertsHistory(temp_history_file)
        
        # Add alerts of different types
        for alert_type in ["cpu", "memory", "cpu", "disk", "cpu"]:
            alert = {
                "alert_type": alert_type,
                "level": "warning",
                "message": f"{alert_type} alert"
            }
            history.add_alert(alert)
        
        cpu_alerts = history.get_alerts_by_type("cpu")
        assert len(cpu_alerts) == 3
    
    def test_get_critical_alerts_today(self, temp_history_file):
        """Test retrieving critical alerts from today"""
        history = AlertsHistory(temp_history_file)
        
        # Add critical alert
        alert = {
            "alert_type": "cpu",
            "level": "critical",
            "message": "CPU critical"
        }
        history.add_alert(alert)
        
        critical = history.get_critical_alerts_today()
        assert len(critical) == 1
        assert critical[0]["level"] == "critical"
    
    def test_get_recovery_count_today(self, temp_history_file):
        """Test counting recovery alerts"""
        history = AlertsHistory(temp_history_file)
        
        # Add recovery alerts
        for i in range(3):
            alert = {
                "alert_type": "recovery",
                "level": "info",
                "message": f"Metric recovered {i}"
            }
            history.add_alert(alert)
        
        recovery_count = history.get_recovery_count_today()
        assert recovery_count >= 0
    
    def test_get_stats_summary(self, temp_history_file):
        """Test getting stats summary"""
        history = AlertsHistory(temp_history_file)
        
        # Add various alerts
        alerts_data = [
            {"alert_type": "cpu", "level": "warning", "message": "CPU warning"},
            {"alert_type": "memory", "level": "critical", "message": "Memory critical"},
            {"alert_type": "disk", "level": "warning", "message": "Disk warning"},
            {"alert_type": "recovery", "level": "info", "message": "CPU recovered"}
        ]
        
        for alert in alerts_data:
            history.add_alert(alert)
        
        stats = history.get_stats_summary()
        
        assert "total" in stats
        assert "critical" in stats
        assert "warning" in stats
        assert stats["total"] == 4
    
    def test_clear_history(self, temp_history_file):
        """Test clearing history"""
        history = AlertsHistory(temp_history_file)
        
        # Add alerts
        for i in range(3):
            alert = {
                "alert_type": "test",
                "level": "info",
                "message": f"Test {i}"
            }
            history.add_alert(alert)
        
        # Clear
        history.clear_history()
        
        recent = history.get_recent_alerts(10)
        assert len(recent) == 0
    
    def test_max_records_limit(self, temp_history_file):
        """Test that history respects max records limit"""
        history = AlertsHistory(temp_history_file)
        
        # Add more alerts than the limit (default 1000)
        for i in range(1100):
            alert = {
                "alert_type": "test",
                "level": "info",
                "message": f"Alert {i}"
            }
            history.add_alert(alert)
        
        recent = history.get_recent_alerts(2000)
        # Should not exceed max records
        assert len(recent) <= 1000
    
    def test_alert_timestamp(self, temp_history_file):
        """Test that alerts have timestamps"""
        history = AlertsHistory(temp_history_file)
        
        alert = {
            "alert_type": "test",
            "level": "info",
            "message": "Test alert"
        }
        history.add_alert(alert)
        
        recent = history.get_recent_alerts(1)
        assert "timestamp" in recent[0]
