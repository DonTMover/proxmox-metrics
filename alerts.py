#!/usr/bin/env python3
"""
Alert management - tracks alert states, deduplication, and thresholds
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    RECOVERY = "recovery"


@dataclass
class Alert:
    """Alert data structure"""
    alert_type: str  # "cpu", "ram", "disk", "ct_stopped", etc.
    level: str  # AlertLevel value
    message: str
    timestamp: float = None
    container_id: int = None
    metric_value: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class StateManager:
    """Manages persistent alert state to prevent spam"""

    def __init__(self, state_file: Path = Path("state.json")):
        self.state_file = state_file
        self.state: Dict = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from JSON file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading state file: {e}")
        return {"alerts": {}, "last_summary": 0}

    def _save_state(self):
        """Save state to JSON file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving state file: {e}")

    def get_last_alert_time(self, alert_key: str) -> float:
        """Get last time alert was sent"""
        return self.state.get("alerts", {}).get(alert_key, {}).get("last_sent", 0)

    def set_last_alert_time(self, alert_key: str, timestamp: float = None):
        """Update last alert send time"""
        if timestamp is None:
            timestamp = time.time()
        if "alerts" not in self.state:
            self.state["alerts"] = {}
        if alert_key not in self.state["alerts"]:
            self.state["alerts"][alert_key] = {}
        self.state["alerts"][alert_key]["last_sent"] = timestamp
        self.state["alerts"][alert_key]["level"] = None
        self._save_state()

    def get_last_alert_level(self, alert_key: str) -> Optional[str]:
        """Get the level of last alert (for recovery detection)"""
        return self.state.get("alerts", {}).get(alert_key, {}).get("level")

    def set_alert_level(self, alert_key: str, level: str):
        """Store current alert level"""
        if "alerts" not in self.state:
            self.state["alerts"] = {}
        if alert_key not in self.state["alerts"]:
            self.state["alerts"][alert_key] = {}
        self.state["alerts"][alert_key]["level"] = level
        self._save_state()

    def get_last_summary_time(self) -> float:
        """Get last summary send time"""
        return self.state.get("last_summary", 0)

    def set_last_summary_time(self, timestamp: float = None):
        """Update last summary send time"""
        if timestamp is None:
            timestamp = time.time()
        self.state["last_summary"] = timestamp
        self._save_state()


class ThresholdChecker:
    """Checks metrics against thresholds"""

    def __init__(self, thresholds: Dict):
        self.thresholds = thresholds

    def check_cpu(self, percent: float) -> Optional[AlertLevel]:
        """Check CPU threshold"""
        cpu_config = self.thresholds.get("cpu", {})
        if percent >= cpu_config.get("critical", 95):
            return AlertLevel.CRITICAL
        elif percent >= cpu_config.get("warning", 80):
            return AlertLevel.WARNING
        return None

    def check_ram(self, percent: float) -> Optional[AlertLevel]:
        """Check RAM threshold"""
        ram_config = self.thresholds.get("ram", {})
        if percent >= ram_config.get("critical", 95):
            return AlertLevel.CRITICAL
        elif percent >= ram_config.get("warning", 85):
            return AlertLevel.WARNING
        return None

    def check_swap(self, percent: float) -> Optional[AlertLevel]:
        """Check Swap threshold"""
        swap_config = self.thresholds.get("swap", {})
        if percent >= swap_config.get("critical", 80):
            return AlertLevel.CRITICAL
        elif percent >= swap_config.get("warning", 50):
            return AlertLevel.WARNING
        return None

    def check_disk(self, percent: float) -> Optional[AlertLevel]:
        """Check Disk threshold"""
        disk_config = self.thresholds.get("disk", {})
        if percent >= disk_config.get("critical", 95):
            return AlertLevel.CRITICAL
        elif percent >= disk_config.get("warning", 85):
            return AlertLevel.WARNING
        return None


class AlertGenerator:
    """Generates alerts based on metrics and state"""

    def __init__(self, thresholds: Dict, state_manager: StateManager, alert_repeat_sec: int = 1800):
        self.thresholds = thresholds
        self.state = state_manager
        self.checker = ThresholdChecker(thresholds)
        self.alert_repeat_sec = alert_repeat_sec

    def should_send_alert(self, alert_key: str, level: AlertLevel) -> bool:
        """Check if alert should be sent (respecting repeat interval)"""
        last_sent = self.state.get_last_alert_time(alert_key)
        current_time = time.time()

        # Always send critical alerts after repeat interval
        if level == AlertLevel.CRITICAL:
            return (current_time - last_sent) >= self.alert_repeat_sec

        # Send recovery or new alert level changes
        last_level = self.state.get_last_alert_level(alert_key)
        if level != last_level and last_level is not None:
            return True

        # Don't spam same level
        return (current_time - last_sent) >= self.alert_repeat_sec

    def check_host_metrics(self, metrics) -> List[Alert]:
        """Check host metrics and generate alerts"""
        alerts = []

        # Check CPU
        cpu_level = self.checker.check_cpu(metrics.cpu_percent)
        if cpu_level and self.should_send_alert("cpu", cpu_level):
            alerts.append(Alert(
                alert_type="cpu",
                level=cpu_level.value,
                message=f"CPU usage {metrics.cpu_percent:.1f}%"
            ))
            self.state.set_last_alert_time("cpu")
            self.state.set_alert_level("cpu", cpu_level.value)

        # Check RAM
        ram_percent = (metrics.ram_used_mb / metrics.ram_total_mb * 100) if metrics.ram_total_mb > 0 else 0
        ram_level = self.checker.check_ram(ram_percent)
        if ram_level and self.should_send_alert("ram", ram_level):
            alerts.append(Alert(
                alert_type="ram",
                level=ram_level.value,
                message=f"RAM usage {ram_percent:.1f}% ({metrics.ram_used_mb:.1f}/{metrics.ram_total_mb:.1f} MB)"
            ))
            self.state.set_last_alert_time("ram")
            self.state.set_alert_level("ram", ram_level.value)

        # Check Swap
        if metrics.swap_total_mb > 0:
            swap_percent = (metrics.swap_used_mb / metrics.swap_total_mb * 100)
            swap_level = self.checker.check_swap(swap_percent)
            if swap_level and self.should_send_alert("swap", swap_level):
                alerts.append(Alert(
                    alert_type="swap",
                    level=swap_level.value,
                    message=f"Swap usage {swap_percent:.1f}% ({metrics.swap_used_mb:.1f}/{metrics.swap_total_mb:.1f} MB)"
                ))
                self.state.set_last_alert_time("swap")
                self.state.set_alert_level("swap", swap_level.value)

        # Check Disks
        for disk_path, disk_info in metrics.disks.items():
            disk_percent = disk_info["percent"]
            disk_level = self.checker.check_disk(disk_percent)
            alert_key = f"disk_{disk_path}"
            if disk_level and self.should_send_alert(alert_key, disk_level):
                alerts.append(Alert(
                    alert_type="disk",
                    level=disk_level.value,
                    message=f"Disk {disk_path} usage {disk_percent:.1f}% ({disk_info['used']:.1f}/{disk_info['total']:.1f} GB)"
                ))
                self.state.set_last_alert_time(alert_key)
                self.state.set_alert_level(alert_key, disk_level.value)

        return alerts

    def check_container_status(self, containers: List, required_ids: List[int]) -> List[Alert]:
        """Check if required containers are running"""
        alerts = []

        for container_id in required_ids:
            container = next((c for c in containers if c.vmid == container_id), None)
            alert_key = f"container_{container_id}"

            if container is None or container.status != "running":
                status_display = container.status if container else "unknown"
                if self.should_send_alert(alert_key, AlertLevel.CRITICAL):
                    alerts.append(Alert(
                        alert_type="container_stopped",
                        level=AlertLevel.CRITICAL.value,
                        message=f"Container {container_id} ({container.name if container else 'unknown'}) is {status_display}",
                        container_id=container_id
                    ))
                    self.state.set_last_alert_time(alert_key)
                    self.state.set_alert_level(alert_key, AlertLevel.CRITICAL.value)
            else:
                # Container is running - check for recovery
                last_level = self.state.get_last_alert_level(alert_key)
                if last_level == AlertLevel.CRITICAL.value:
                    alerts.append(Alert(
                        alert_type="container_recovery",
                        level=AlertLevel.RECOVERY.value,
                        message=f"Container {container_id} ({container.name}) is back online",
                        container_id=container_id
                    ))
                    self.state.set_alert_level(alert_key, AlertLevel.RECOVERY.value)

        return alerts

    def check_recovery(self) -> List[Alert]:
        """Check for recovery alerts from previous critical states"""
        alerts = []
        # This is handled per-metric in other check functions
        return alerts
