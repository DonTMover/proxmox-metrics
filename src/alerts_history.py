#!/usr/bin/env python3
"""
Alert history manager - stores and retrieves historical alert data
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class HistoricalAlert:
    """Historical alert record"""
    timestamp: str  # ISO format
    alert_type: str  # cpu, ram, disk, etc.
    level: str  # critical, warning, recovery
    message: str
    container_id: Optional[int] = None
    container_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None


class AlertsHistory:
    """Manages alert history storage"""

    def __init__(self, history_file: Path = Path("alerts_history.json")):
        self.history_file = history_file
        self.max_records = 1000  # Limit to prevent huge files

    def add_alert(self, alert: Dict[str, Any]) -> bool:
        """Add alert to history"""
        try:
            historical_alert = HistoricalAlert(
                timestamp=datetime.now().isoformat(),
                alert_type=alert.get("alert_type", "unknown"),
                level=alert.get("level", "info"),
                message=alert.get("message", ""),
                container_id=alert.get("container_id"),
                container_name=alert.get("container_name"),
                metric_value=alert.get("metric_value"),
                threshold=alert.get("threshold")
            )

            history = self._load_history()
            history.append(asdict(historical_alert))

            # Keep only latest records
            if len(history) > self.max_records:
                history = history[-self.max_records:]

            self._save_history(history)
            return True
        except Exception as e:
            logger.error(f"Failed to add alert to history: {e}")
            return False

    def get_recent_alerts(self, count: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        try:
            history = self._load_history()
            return history[-count:] if history else []
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {e}")
            return []

    def get_alerts_by_type(self, alert_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alerts of specific type from last N hours"""
        try:
            history = self._load_history()
            cutoff_time = datetime.now().timestamp() - (hours * 3600)

            filtered = [
                a for a in history
                if a.get("alert_type") == alert_type
                and datetime.fromisoformat(a.get("timestamp", "")).timestamp() > cutoff_time
            ]
            return filtered
        except Exception as e:
            logger.error(f"Failed to get alerts by type: {e}")
            return []

    def get_critical_alerts_today(self) -> List[Dict[str, Any]]:
        """Get all critical alerts from today"""
        try:
            history = self._load_history()
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            critical = [
                a for a in history
                if a.get("level") == "critical"
                and datetime.fromisoformat(a.get("timestamp", "")) >= today_start
            ]
            return critical
        except Exception as e:
            logger.error(f"Failed to get critical alerts: {e}")
            return []

    def get_recovery_count_today(self) -> int:
        """Count recovery events today"""
        try:
            history = self._load_history()
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            recoveries = [
                a for a in history
                if a.get("level") == "recovery"
                and datetime.fromisoformat(a.get("timestamp", "")) >= today_start
            ]
            return len(recoveries)
        except Exception as e:
            logger.error(f"Failed to count recoveries: {e}")
            return 0

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        try:
            history = self._load_history()
            if not history:
                return {
                    "total": 0,
                    "critical": 0,
                    "warning": 0,
                    "recovery": 0
                }

            return {
                "total": len(history),
                "critical": sum(1 for a in history if a.get("level") == "critical"),
                "warning": sum(1 for a in history if a.get("level") == "warning"),
                "recovery": sum(1 for a in history if a.get("level") == "recovery")
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def clear_history(self) -> bool:
        """Clear all history"""
        try:
            self._save_history([])
            logger.info("Alert history cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load history from file"""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []

    def _save_history(self, history: List[Dict[str, Any]]) -> bool:
        """Save history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            return False
