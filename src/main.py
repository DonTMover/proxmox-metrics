#!/usr/bin/env python3
"""
Proxmox VE Telegram Monitor - Main entry point
Monitors Proxmox host and sends alerts via Telegram
"""

import asyncio
import logging
import signal
import sys
import yaml
import time
from pathlib import Path
from typing import Dict, Any

from proxmox import ProxmoxCollector, ContainerMetrics
from alerts import AlertGenerator, StateManager, Alert, AlertLevel
from alerts_history import AlertsHistory
from telegram_bot import TelegramBot, MessageFormatter

# Setup logging - only if we can write to log file
logging_handlers = [logging.StreamHandler()]  # Always include console
try:
    logging_handlers.append(logging.FileHandler('/var/log/proxmox-monitor.log'))
except (PermissionError, FileNotFoundError):
    # Fall back to console only if /var/log isn't writable (e.g., during development)
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=logging_handlers
)
logger = logging.getLogger(__name__)


class ProxmoxMonitor:
    """Main monitor application"""

    def __init__(self, config_path: Path = Path("config.yaml")):
        self.config_path = config_path
        self.config = self._load_config()
        self.running = True

        # Initialize components
        self.collector = ProxmoxCollector(
            node=self.config["proxmox"].get("node", "pve")
        )
        self.state_manager = StateManager(Path(self.config.get("state_file", "state.json")))
        self.alert_history = AlertsHistory(Path(self.config.get("alerts_history_file", "alerts_history.json")))
        self.alert_generator = AlertGenerator(
            thresholds=self.config["thresholds"],
            state_manager=self.state_manager,
            alert_repeat_sec=self.config["scheduler"].get("alert_repeat", 1800)
        )
        self.bot = TelegramBot(
            token=self.config["telegram"]["token"],
            allowed_user_ids=self.config["telegram"].get("allowed_user_ids", []),
            chat_id=self.config["telegram"].get("chat_id")
        )

        # Register command handlers
        self.bot.register_command("status", self._cmd_status)
        self.bot.register_command("vms", self._cmd_vms)
        self.bot.register_command("alerts", self._cmd_alerts)
        self.bot.register_command("history", self._cmd_history)
        self.bot.register_command("stats", self._cmd_stats)

        # State for alerts
        self.last_alerts_sent: Dict[str, Alert] = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"YAML error in config: {e}")
            sys.exit(1)

    def _format_summary(self) -> str:
        """Format and collect current system summary"""
        metrics = self.collector.get_host_metrics()
        containers = self.collector.get_all_containers_and_vms()

        # Format host status
        summary_lines = []
        ram_percent = (metrics.ram_used_mb / metrics.ram_total_mb * 100) if metrics.ram_total_mb > 0 else 0
        swap_percent = (metrics.swap_used_mb / metrics.swap_total_mb * 100) if metrics.swap_total_mb > 0 else 0

        # Determine status emojis
        cpu_emoji = "✅" if metrics.cpu_percent < 80 else "⚠️" if metrics.cpu_percent < 95 else "🔴"
        ram_emoji = "✅" if ram_percent < 85 else "⚠️" if ram_percent < 95 else "🔴"
        swap_emoji = "✅" if swap_percent < 50 else "⚠️" if swap_percent < 80 else "🔴"

        summary_lines.append(f"🖥 Proxmox pve | {time.strftime('%H:%M')}\n")
        summary_lines.append(f"CPU: {metrics.cpu_percent:.0f}% {cpu_emoji}\n")
        summary_lines.append(f"RAM: {metrics.ram_used_mb:.0f}/{metrics.ram_total_mb:.0f}GB ({ram_percent:.0f}%) {ram_emoji}\n")
        summary_lines.append(f"Swap: {metrics.swap_used_mb:.1f}/{metrics.swap_total_mb:.1f}GB ({swap_percent:.0f}%) {swap_emoji}\n")

        # Disk summary
        disk_lines = []
        for disk_path, disk_info in metrics.disks.items():
            percent = disk_info["percent"]
            emoji = "✅" if percent < 85 else "⚠️" if percent < 95 else "🔴"
            disk_lines.append(f"{disk_path}: {percent:.0f}% {emoji}")

        summary_lines.append(f"Disk: {' | '.join(disk_lines)}\n")

        # Container summary
        running = sum(1 for c in containers if c.status == "running")
        total = len(containers)
        summary_lines.append(f"CT/VM: {running}/{total} running\n")

        # Show stopped containers
        stopped = [c for c in containers if c.status != "running"]
        if stopped:
            summary_lines.append("\n")
            for container in stopped:
                summary_lines.append(f"🔴 {container.name} (ID: {container.vmid}) stopped\n")

        return "".join(summary_lines)

    async def _cmd_status(self) -> str:
        """Command: /status"""
        try:
            metrics = self.collector.get_host_metrics()
            return MessageFormatter.host_status(metrics)
        except Exception as e:
            logger.error(f"Error in /status command: {e}")
            return "❌ Error fetching status"

    async def _cmd_vms(self) -> str:
        """Command: /vms"""
        try:
            containers = self.collector.get_all_containers_and_vms()
            return MessageFormatter.containers_list(containers)
        except Exception as e:
            logger.error(f"Error in /vms command: {e}")
            return "❌ Error fetching VMs"

    async def _cmd_alerts(self) -> str:
        """Command: /alerts"""
        try:
            alert_list = []
            for key, alert in self.last_alerts_sent.items():
                alert_list.append({
                    "message": alert.message,
                    "level": alert.level
                })
            return MessageFormatter.alerts_summary(alert_list)
        except Exception as e:
            logger.error(f"Error in /alerts command: {e}")
            return "❌ Error fetching alerts"

    async def _cmd_history(self) -> str:
        """Command: /history - Show recent alerts from history"""
        try:
            history = self.alert_history.get_recent_alerts(count=10)
            return MessageFormatter.alerts_history(history)
        except Exception as e:
            logger.error(f"Error in /history command: {e}")
            return "❌ Error fetching history"

    async def _cmd_stats(self) -> str:
        """Command: /stats - Show alert statistics"""
        try:
            stats = self.alert_history.get_stats_summary()
            return MessageFormatter.stats_summary(stats)
        except Exception as e:
            logger.error(f"Error in /stats command: {e}")
            return "❌ Error fetching stats"

    async def _check_and_send_alerts(self):
        """Check metrics and send alerts"""
        try:
            metrics = self.collector.get_host_metrics()
            containers = self.collector.get_all_containers_and_vms()

            # Generate alerts
            alerts = []
            alerts.extend(self.alert_generator.check_host_metrics(metrics))
            alerts.extend(self.alert_generator.check_container_status(
                containers,
                self.config["proxmox"].get("required_cts", []) +
                self.config["proxmox"].get("required_vms", [])
            ))

            # Send alerts and store in history
            for alert in alerts:
                try:
                    await self.bot.send_alert(
                        title=alert.alert_type.upper(),
                        content=alert.message,
                        level=alert.level
                    )
                    logger.info(f"Alert sent: {alert.alert_type} - {alert.level}")
                    self.last_alerts_sent[f"{alert.alert_type}_{alert.container_id or ''}"] = alert
                    
                    # Store in history
                    self.alert_history.add_alert({
                        "alert_type": alert.alert_type,
                        "level": alert.level,
                        "message": alert.message,
                        "container_id": alert.container_id,
                        "container_name": getattr(alert, 'container_name', None)
                    })
                except Exception as e:
                    logger.error(f"Failed to send alert: {e}")

        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

    async def _send_periodic_summary(self):
        """Send periodic status summary"""
        try:
            last_summary = self.state_manager.get_last_summary_time()
            current_time = time.time()
            summary_interval = self.config["scheduler"].get("summary_interval", 300)

            if (current_time - last_summary) >= summary_interval:
                summary = self._format_summary()
                if await self.bot.send_message(summary):
                    self.state_manager.set_last_summary_time()
                    logger.info("Summary sent")
        except Exception as e:
            logger.error(f"Error sending summary: {e}")

    async def run(self):
        """Main run loop"""
        logger.info("Proxmox monitor starting...")

        # Initialize bot
        if not await self.bot.initialize():
            logger.error("Failed to initialize Telegram bot")
            return

        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Main monitoring loop
        try:
            while self.running:
                # Check and send alerts
                await self._check_and_send_alerts()

                # Send periodic summary
                await self._send_periodic_summary()

                # Sleep before next check
                await asyncio.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.bot.stop()
            logger.info("Monitor stopped")

    async def run_with_polling(self):
        """Run monitor with Telegram polling"""
        logger.info("Proxmox monitor starting with polling...")

        # Initialize bot
        if not await self.bot.initialize():
            logger.error("Failed to initialize Telegram bot")
            return

        # Setup signal handlers
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start polling task and monitor task concurrently
        try:
            polling_task = asyncio.create_task(self.bot.start_polling())
            monitor_task = asyncio.create_task(self._monitor_loop())

            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [polling_task, monitor_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel pending tasks
            for task in pending:
                task.cancel()

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.bot.stop()
            logger.info("Monitor stopped")

    async def _monitor_loop(self):
        """Monitor loop for non-polling mode"""
        while self.running:
            try:
                await self._check_and_send_alerts()
                await self._send_periodic_summary()
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(30)


async def main():
    """Entry point"""
    # Try to load config from multiple locations
    config_paths = [
        Path("config.yaml"),
        Path("/opt/proxmox-monitor/config.yaml"),
        Path("/etc/proxmox-monitor/config.yaml")
    ]

    config_file = None
    for path in config_paths:
        if path.exists():
            config_file = path
            break

    if not config_file:
        logger.error("Config file not found in any standard location")
        sys.exit(1)

    monitor = ProxmoxMonitor(config_file)
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
