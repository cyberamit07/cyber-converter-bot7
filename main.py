"""
Main entry point for Currency Converter Bot
"""

import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from logger import setup_logger
from handlers import setup_handlers
from rates import RateFetcher

logger = setup_logger(__name__)


class CurrencyBot:
    """Main bot class"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.session = None
        self.rate_fetcher = None
        logger.info("🤖 Initializing bot...")
    
    async def setup(self):
        """Setup bot components"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            logger.info("✅ HTTP session created")
            
            # Initialize rate fetcher
            self.rate_fetcher = RateFetcher(self.session)
            
            # Create bot
            self.bot = Bot(
                token=BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
            )
            logger.info("✅ Bot created")
            
            # Create dispatcher
            self.dp = Dispatcher()
            
            # Register handlers
            router = setup_handlers(self.rate_fetcher)
            self.dp.include_router(router)
            
            logger.info("✅ Setup completed")
            
        except Exception as e:
            logger.error(f"Setup failed: {e}", exc_info=True)
            await self.cleanup()
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
                logger.info("✅ Session closed")
            
            if self.bot:
                await self.bot.session.close()
                logger.info("✅ Bot closed")
                
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    async def start_polling(self):
        """Start bot polling"""
        try:
            logger.info("🚀 Starting polling...")
            
            # Pre-fetch rates
            logger.info("🔄 Pre-fetching rates...")
            await self.rate_fetcher.get_all_rates()
            
            # Start polling
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"Polling error: {e}", exc_info=True)
            raise
        finally:
            await self.cleanup()
    
    async def run(self):
        """Main run method"""
        try:
            await self.setup()
            await self.start_polling()
        except KeyboardInterrupt:
            logger.info("⚠️ Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            await self.cleanup()


async def main():
    """Entry point"""
    logger.info("=" * 50)
    logger.info("🚀 Currency Converter Bot Starting")
    logger.info("=" * 50)
    
    bot = CurrencyBot()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Shutdown completed")