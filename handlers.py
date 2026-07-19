"""
Bot message handlers
"""

import asyncio
import time
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from logger import setup_logger
from regex_parser import parser
from cache import user_request_cache
from utils import format_conversion_result, format_rate_info

logger = setup_logger(__name__)

router = Router()


class MessageHandler:
    """Handle all messages and commands"""
    
    def __init__(self, rate_fetcher):
        self.rate_fetcher = rate_fetcher
        logger.info("✅ MessageHandler initialized")
    
    async def check_user_cooldown(self, user_id: int) -> bool:
        """Check user cooldown"""
        cache_key = f"user_{user_id}"
        last_request = await user_request_cache.get(cache_key)
        
        if last_request:
            return True
        
        await user_request_cache.set(cache_key, datetime.now())
        return False
    
    async def handle_currency_conversion(self, message: Message) -> None:
        """Process currency conversion"""
        start_time = time.time()
        
        try:
            parsed = parser.parse(message.text)
            
            if not parsed:
                return
            
            amount, currency = parsed
            
            # Check cooldown
            if await self.check_user_cooldown(message.from_user.id):
                logger.info(f"Rate limited user {message.from_user.id}")
                return
            
            logger.info(f"Converting {amount} {currency}")
            
            # Get rates
            rates = await self.rate_fetcher.get_all_rates()
            
            if not rates:
                await message.reply(
                    "⚠️ Unable to fetch exchange rates.\n"
                    "Please try again in a few seconds."
                )
                return
            
            # Convert
            conversions = await self.rate_fetcher.convert(amount, currency, rates)
            
            if not conversions:
                await message.reply("⚠️ Conversion failed.\nPlease try again.")
                return
            
            # Format result
            result_text = format_conversion_result(currency, amount, conversions)
            
            response_time = (time.time() - start_time) * 1000
            logger.info(f"✅ Response in {response_time:.2f}ms")
            
            await message.reply(result_text)
            
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            await message.reply("⚠️ An error occurred. Please try again.")
    
    async def handle_start(self, message: Message) -> None:
        """Handle /start"""
        welcome_text = (
            "👋 **Welcome to Currency Converter Bot!**\n\n"
            "I can convert between multiple currencies instantly.\n\n"
            "**Supported currencies:**\n"
            "💎 TON\n"
            "💵 USDT\n"
            "🇺🇸 USD\n"
            "🇮🇳 INR\n"
            "🇷🇺 RUB\n"
            "🇪🇺 EUR\n"
            "⭐ Telegram Stars\n\n"
            "**How to use:**\n"
            "Just type any amount:\n"
            "• `1t` or `1 ton`\n"
            "• `100 usdt`\n"
            "• `500 inr`\n"
            "• `50 stars`\n\n"
            "**Commands:**\n"
            "/start - This message\n"
            "/help - Get help\n"
            "/rate - Current rates\n"
            "/ping - Check latency\n\n"
            "@cyber_amit"
        )
        
        await message.reply(welcome_text)
    
    async def handle_help(self, message: Message) -> None:
        """Handle /help"""
        help_text = (
            "ℹ️ **Currency Converter Help**\n\n"
            "**Supported Formats:**\n"
            "• `1t`, `1 ton`, `1TON`\n"
            "• `100 usdt`, `100USDT`\n"
            "• `500 inr`, `500INR`\n"
            "• `2.5 ton` (decimals work)\n"
            "• `50 stars`, `100star`\n\n"
            "**Examples:**\n"
            "• Type `1t` → convert 1 TON\n"
            "• Type `100 usdt` → convert 100 USDT\n"
            "• Type `500 inr` → convert 500 INR\n\n"
            "**Features:**\n"
            "✅ Instant conversions\n"
            "✅ Real-time rates\n"
            "✅ Multiple currencies\n"
            "✅ Works in groups\n"
            "✅ Auto-detection\n\n"
            "@cyber_amit"
        )
        
        await message.reply(help_text)
    
    async def handle_rate(self, message: Message) -> None:
        """Handle /rate"""
        try:
            rates = await self.rate_fetcher.get_all_rates()
            
            if not rates:
                await message.reply("⚠️ Unable to fetch rates.")
                return
            
            result_text = format_rate_info(rates)
            await message.reply(result_text)
            
        except Exception as e:
            logger.error(f"Error in /rate: {e}")
            await message.reply("⚠️ An error occurred.")
    
    async def handle_ping(self, message: Message) -> None:
        """Handle /ping"""
        start_time = time.time()
        
        try:
            sent_message = await message.reply("🏓 Pong!")
            latency = (time.time() - start_time) * 1000
            
            await sent_message.edit_text(
                f"🏓 **Pong!**\n\n"
                f"⚡ Latency: `{latency:.2f}ms`\n"
                f"✅ Bot is online\n\n"
                f"@cyber_amit"
            )
            
        except Exception as e:
            logger.error(f"Error in /ping: {e}")


def setup_handlers(rate_fetcher) -> Router:
    """Register all handlers"""
    handler = MessageHandler(rate_fetcher)
    
    @router.message(Command("start"))
    async def cmd_start(message: Message):
        await handler.handle_start(message)
    
    @router.message(Command("help"))
    async def cmd_help(message: Message):
        await handler.handle_help(message)
    
    @router.message(Command("rate"))
    async def cmd_rate(message: Message):
        await handler.handle_rate(message)
    
    @router.message(Command("ping"))
    async def cmd_ping(message: Message):
        await handler.handle_ping(message)
    
    @router.message(F.text)
    async def handle_text(message: Message):
        if message.chat.type in ["group", "supergroup"]:
            if parser.is_currency_message(message.text):
                await handler.handle_currency_conversion(message)
        elif parser.is_currency_message(message.text):
            await handler.handle_currency_conversion(message)
    
    logger.info("✅ Handlers registered")
    return router