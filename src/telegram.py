#!/usr/bin/env python3
"""
Telegram bot interface - handles commands and sends messages
"""

import logging
from typing import List, Optional, Callable, Dict, Any
# Use absolute imports to avoid circular import with module name 'telegram'
from telegram.update import Update
from telegram.chat import Chat
from telegram.replykeyboardmarkup import InlineKeyboardMarkup
from telegram.keyboardbutton import InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, filters
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for Proxmox monitoring"""

    def __init__(self, token: str, allowed_user_ids: List[int], chat_id: int | str):
        self.token = token
        self.allowed_user_ids = allowed_user_ids
        self.chat_id = chat_id
        self.app: Optional[Application] = None

        # Callback storage
        self.command_handlers: Dict[str, Callable] = {}

    def _is_allowed_user(self, user_id: int) -> bool:
        """Check if user is in whitelist"""
        return user_id in self.allowed_user_ids

    async def initialize(self):
        """Initialize Telegram bot"""
        try:
            self.app = Application.builder().token(self.token).build()

            # Register command handlers
            self.app.add_handler(CommandHandler("start", self._handle_start))
            self.app.add_handler(CommandHandler("id", self._handle_id))
            self.app.add_handler(CommandHandler("status", self._handle_status))
            self.app.add_handler(CommandHandler("vms", self._handle_vms))
            self.app.add_handler(CommandHandler("alerts", self._handle_alerts))
            self.app.add_handler(CommandHandler("help", self._handle_help))

            await self.app.initialize()
            logger.info("Telegram bot initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            return False

    def register_command(self, command: str, handler: Callable):
        """Register a custom command handler"""
        self.command_handlers[command] = handler

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self._is_allowed_user(update.effective_user.id):
            await update.message.reply_text("❌ Access denied")
            logger.warning(f"Unauthorized /start from user {update.effective_user.id}")
            return

        await update.message.reply_text(
            "🖥 **Proxmox Monitor Bot**\n\n"
            "Welcome! I'm monitoring your Proxmox VE host.\n\n"
            "Use /help to see available commands.",
            parse_mode="Markdown"
        )

    async def _handle_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /id command - return user's Telegram ID"""
        if not self._is_allowed_user(update.effective_user.id):
            await update.message.reply_text("❌ Access denied")
            return

        await update.message.reply_text(
            f"Your Telegram ID: `{update.effective_user.id}`",
            parse_mode="Markdown"
        )

    async def _handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self._is_allowed_user(update.effective_user.id):
            await update.message.reply_text("❌ Access denied")
            return

        if "status" in self.command_handlers:
            text = await self.command_handlers["status"]()
            await update.message.reply_text(text, parse_mode="Markdown")

    async def _handle_vms(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /vms command"""
        if not self._is_allowed_user(update.effective_user.id):
            await update.message.reply_text("❌ Access denied")
            return

        if "vms" in self.command_handlers:
            text = await self.command_handlers["vms"]()
            await update.message.reply_text(text, parse_mode="Markdown")

    async def _handle_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        if not self._is_allowed_user(update.effective_user.id):
            await update.message.reply_text("❌ Access denied")
            return

        if "alerts" in self.command_handlers:
            text = await self.command_handlers["alerts"]()
            await update.message.reply_text(text, parse_mode="Markdown")

    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self._is_allowed_user(update.effective_user.id):
            await update.message.reply_text("❌ Access denied")
            return

        help_text = """
*Available Commands:*

/start - Welcome message and bot status
/id - Get your Telegram user ID
/status - Host system status
/vms - List all CT/VM and their status
/alerts - Show active alerts
/help - This message
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def send_message(self, text: str) -> bool:
        """Send message to chat"""
        if not self.app:
            logger.warning("Bot not initialized")
            return False

        try:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode="Markdown"
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def send_alert(self, title: str, content: str, level: str = "warning") -> bool:
        """Send formatted alert message"""
        emoji = {
            "critical": "🚨",
            "warning": "⚠️",
            "recovery": "✅",
            "info": "ℹ️"
        }.get(level, "📢")

        text = f"{emoji} **{title}**\n\n{content}"
        return await self.send_message(text)

    async def send_summary(self, summary: str) -> bool:
        """Send summary report"""
        return await self.send_message(f"📊 **Status Summary**\n\n{summary}")

    async def start_polling(self):
        """Start polling for messages (blocking)"""
        if not self.app:
            logger.warning("Bot not initialized")
            return

        try:
            await self.app.start()
            logger.info("Telegram bot polling started")
            await self.app.idle()
        except Exception as e:
            logger.error(f"Error during polling: {e}")
        finally:
            await self.app.stop()

    async def stop(self):
        """Stop bot gracefully"""
        if self.app:
            await self.app.stop()
            logger.info("Telegram bot stopped")


class MessageFormatter:
    """Formats messages for Telegram"""

    @staticmethod
    def host_status(metrics) -> str:
        """Format host status message"""
        ram_percent = (metrics.ram_used_mb / metrics.ram_total_mb * 100) if metrics.ram_total_mb > 0 else 0
        swap_percent = (metrics.swap_used_mb / metrics.swap_total_mb * 100) if metrics.swap_total_mb > 0 else 0

        status_lines = [
            f"🖥 **Proxmox Host**\n",
            f"⏰ Uptime: {metrics.uptime_days}d {metrics.uptime_hours}h {metrics.uptime_minutes}m\n",
            f"⚡ CPU: {metrics.cpu_percent:.1f}% (1/5/15min: {metrics.cpu_load_1:.2f}/{metrics.cpu_load_5:.2f}/{metrics.cpu_load_15:.2f})\n",
            f"🧠 RAM: {metrics.ram_used_mb:.0f}/{metrics.ram_total_mb:.0f}MB ({ram_percent:.1f}%)\n",
            f"💾 Swap: {metrics.swap_used_mb:.0f}/{metrics.swap_total_mb:.0f}MB ({swap_percent:.1f}%)\n",
        ]

        # Disk status
        status_lines.append("💿 Disk usage:\n")
        for disk_path, disk_info in metrics.disks.items():
            percent = disk_info["percent"]
            emoji = "✅" if percent < 85 else "⚠️" if percent < 95 else "🔴"
            status_lines.append(f"  {emoji} {disk_path}: {percent:.1f}% ({disk_info['used']:.1f}/{disk_info['total']:.1f}GB)\n")

        if metrics.temperature_cpu is not None:
            status_lines.append(f"🌡 CPU Temp: {metrics.temperature_cpu:.1f}°C\n")
        if metrics.temperature_system is not None:
            status_lines.append(f"🌡 System Temp: {metrics.temperature_system:.1f}°C\n")

        return "".join(status_lines)

    @staticmethod
    def containers_list(containers: List) -> str:
        """Format containers/VMs list"""
        if not containers:
            return "No containers or VMs found"

        running = [c for c in containers if c.status == "running"]
        stopped = [c for c in containers if c.status != "running"]

        lines = [
            f"📦 **Containers and VMs** ({len(running)}/{len(containers)} running)\n\n",
            "**Running:**\n"
        ]

        for container in running:
            lines.append(f"  ✅ {container.name} (ID: {container.vmid})\n")

        if stopped:
            lines.append("\n**Stopped:**\n")
            for container in stopped:
                lines.append(f"  🔴 {container.name} (ID: {container.vmid})\n")

        return "".join(lines)

    @staticmethod
    def alerts_summary(alerts: List[Dict[str, Any]]) -> str:
        """Format alerts summary"""
        if not alerts:
            return "✅ No active alerts"

        lines = ["🚨 **Active Alerts:**\n\n"]
        for alert in alerts:
            emoji = {
                "critical": "🔴",
                "warning": "⚠️",
                "recovery": "✅"
            }.get(alert.get("level", "info"), "ℹ️")

            lines.append(f"{emoji} **{alert.get('message', 'Unknown alert')}**\n")

        return "".join(lines)
