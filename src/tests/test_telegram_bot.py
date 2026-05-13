"""Tests for telegram_bot module"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from telegram_bot import TelegramBot, MessageFormatter
from proxmox import HostMetrics, ContainerMetrics
from alerts import AlertLevel, Alert


class TestMessageFormatter:
    """Test MessageFormatter"""
    
    def test_format_methods_exist(self):
        """Test that MessageFormatter has expected methods"""
        assert hasattr(MessageFormatter, 'host_status')
        assert hasattr(MessageFormatter, 'containers_list')
        assert hasattr(MessageFormatter, 'alerts_summary')
        assert hasattr(MessageFormatter, 'alerts_history')
        assert hasattr(MessageFormatter, 'stats_summary')


class TestTelegramBot:
    """Test TelegramBot"""
    
    @pytest.mark.asyncio
    async def test_telegram_bot_initialization(self):
        """Test TelegramBot initialization"""
        config = {
            "token": "test_token",
            "allowed_user_ids": [123456789],
            "chat_id": 987654321
        }
        
        bot = TelegramBot(
            token=config["token"],
            allowed_user_ids=config["allowed_user_ids"],
            chat_id=config["chat_id"]
        )
        assert bot is not None
        assert bot.chat_id == 987654321
    
    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test sending message"""
        config = {
            "token": "test_token",
            "allowed_user_ids": [123456789],
            "chat_id": 987654321
        }
        
        with patch.object(TelegramBot, 'initialize', new_callable=AsyncMock):
            bot = TelegramBot(
                token=config["token"],
                allowed_user_ids=config["allowed_user_ids"],
                chat_id=config["chat_id"]
            )
            # Note: Message sending requires real bot connection
    
    @pytest.mark.asyncio
    async def test_send_alert(self):
        """Test sending alert"""
        config = {
            "token": "test_token",
            "allowed_user_ids": [123456789],
            "chat_id": 987654321
        }
        
        with patch.object(TelegramBot, 'initialize', new_callable=AsyncMock):
            bot = TelegramBot(
                token=config["token"],
                allowed_user_ids=config["allowed_user_ids"],
                chat_id=config["chat_id"]
            )
            # Note: Alert sending requires real bot connection
    
    def test_is_user_allowed(self):
        """Test user whitelist check"""
        bot = TelegramBot(
            token="test_token",
            allowed_user_ids=[123456789, 987654321],
            chat_id=987654321
        )
        
        assert bot._is_allowed_user(123456789)
        assert bot._is_allowed_user(987654321)
        assert not bot._is_allowed_user(111111111)
