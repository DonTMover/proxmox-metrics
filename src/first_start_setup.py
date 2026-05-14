#!/usr/bin/env python3
"""
First-start setup module for Proxmox Monitor
Handles initial configuration via Telegram bot with inline buttons
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

logger = logging.getLogger(__name__)


class FirstStartSetup:
    """Handles first-start configuration via Telegram"""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.setup_state: Dict[int, Dict[str, Any]] = {}  # Track setup state per user
        self.router = Router()
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup first-start handlers"""

        @self.router.message(Command("setup"))
        async def handle_setup(message: Message):
            """Start first-start setup"""
            user_id = message.from_user.id
            
            # Check if setup password is required
            if self._needs_password():
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔐 Enter Password", callback_data="setup_password")]
                ])
                await message.reply(
                    "🔧 **Proxmox Monitor Setup**\n\n"
                    "This system requires a setup password.\n"
                    "Click below to enter the password:",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                await self._start_setup(message)

        @self.router.callback_query(F.data == "setup_password")
        async def callback_setup_password(callback: CallbackQuery):
            """Password entry callback"""
            user_id = callback.from_user.id
            self.setup_state[user_id] = {"step": "password"}
            await callback.message.reply(
                "🔐 Please enter the setup password:"
            )

        @self.router.message()
        async def handle_setup_input(message: Message):
            """Handle setup input"""
            user_id = message.from_user.id
            
            if user_id not in self.setup_state:
                return

            state = self.setup_state[user_id]
            
            if state.get("step") == "password":
                if not self._verify_password(message.text):
                    await message.reply("❌ Incorrect password. Setup cancelled.")
                    del self.setup_state[user_id]
                    return
                
                await message.reply("✅ Password correct! Starting setup...")
                state["step"] = "bot_token"
                await message.reply(
                    "📝 **Step 1: Telegram Bot Token**\n\n"
                    "Get your bot token from @BotFather on Telegram.\n"
                    "Send the token now:"
                )
            
            elif state.get("step") == "bot_token":
                state["bot_token"] = message.text
                state["step"] = "chat_id"
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📌 Use My ID", callback_data="setup_use_my_id")],
                    [InlineKeyboardButton(text="📝 Enter Custom ID", callback_data="setup_custom_id")]
                ])
                
                await message.reply(
                    "✅ Bot token saved!\n\n"
                    "📍 **Step 2: Chat ID**\n\n"
                    "Where should alerts be sent?",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )

        @self.router.callback_query(F.data == "setup_use_my_id")
        async def callback_use_my_id(callback: CallbackQuery):
            """Use user's own ID as chat ID"""
            user_id = callback.from_user.id
            
            if user_id not in self.setup_state:
                await callback.answer("❌ Setup session expired", show_alert=True)
                return
            
            state = self.setup_state[user_id]
            state["chat_id"] = user_id
            state["step"] = "add_user"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Add Me", callback_data="setup_add_user")],
                [InlineKeyboardButton(text="➕ Add More Users", callback_data="setup_more_users")]
            ])
            
            await callback.message.edit_text(
                f"✅ Chat ID set to: `{user_id}`\n\n"
                "👥 **Step 3: Allowed Users**\n\n"
                "Add users to allowed_user_ids list:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )

        @self.router.callback_query(F.data == "setup_custom_id")
        async def callback_custom_id(callback: CallbackQuery):
            """Enter custom chat ID"""
            user_id = callback.from_user.id
            
            if user_id not in self.setup_state:
                await callback.answer("❌ Setup session expired", show_alert=True)
                return
            
            self.setup_state[user_id]["step"] = "chat_id_input"
            await callback.message.reply(
                "📝 Please enter the chat ID (can be negative for groups):"
            )

        @self.router.callback_query(F.data == "setup_add_user")
        async def callback_add_user(callback: CallbackQuery):
            """Add current user to allowed users"""
            user_id = callback.from_user.id
            
            if user_id not in self.setup_state:
                await callback.answer("❌ Setup session expired", show_alert=True)
                return
            
            state = self.setup_state[user_id]
            if "allowed_users" not in state:
                state["allowed_users"] = []
            
            state["allowed_users"].append(user_id)
            await callback.message.edit_text(
                f"✅ Added user {user_id}\n\n"
                "📍 **Step 4: Proxmox Node**\n\n"
                f"Current node: `pve`\n\n"
                "Send the node name (or /skip to keep default):",
                parse_mode="Markdown"
            )

        @self.router.callback_query(F.data == "setup_more_users")
        async def callback_more_users(callback: CallbackQuery):
            """Add more users"""
            user_id = callback.from_user.id
            
            if user_id not in self.setup_state:
                await callback.answer("❌ Setup session expired", show_alert=True)
                return
            
            state = self.setup_state[user_id]
            state["step"] = "add_more_users"
            state["allowed_users"] = [user_id]  # Add current user first
            
            await callback.message.reply(
                "👥 **Add More Users**\n\n"
                "Send user IDs (one per message, or send /done when finished)"
            )

    async def _start_setup(self, message: Message):
        """Start setup process"""
        user_id = message.from_user.id
        self.setup_state[user_id] = {"step": "bot_token"}
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Enter Token", callback_data="setup_enter_token")]
        ])
        
        await message.reply(
            "🔧 **Proxmox Monitor First-Start Setup**\n\n"
            "I'll guide you through the configuration.\n\n"
            "**Step 1: Get Telegram Bot Token**\n"
            "• Message @BotFather on Telegram\n"
            "• Create a new bot\n"
            "• Copy the token\n\n"
            "Then click below:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    def _needs_password(self) -> bool:
        """Check if setup password is configured"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return bool(config.get("setup_password"))
        except Exception:
            return False

    def _verify_password(self, password: str) -> bool:
        """Verify setup password"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return password == config.get("setup_password", "")
        except Exception:
            return False

    def is_first_start(self) -> bool:
        """Check if this is first start"""
        try:
            if not self.config_path.exists():
                return True
            
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check if required fields are empty
            return (
                not config.get("telegram", {}).get("token") or
                not config.get("telegram", {}).get("allowed_user_ids") or
                not config.get("telegram", {}).get("chat_id")
            )
        except Exception:
            return True

    def save_config(self, state: Dict[str, Any]) -> bool:
        """Save configuration from setup state"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update config with setup state
            config["telegram"]["token"] = state.get("bot_token", "")
            config["telegram"]["chat_id"] = state.get("chat_id")
            config["telegram"]["allowed_user_ids"] = state.get("allowed_users", [])
            config["proxmox"]["node"] = state.get("node", "pve")
            config["first_start"] = False
            
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
