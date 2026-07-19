"""
Configuration module for Currency Converter Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8353088470:AAE4r0flce7s3rmyqaPLuKHpuX5Lx8Vn50c")
GETBLOCK_API = os.getenv("GETBLOCK_API", "https://go.getblock.io/901801f87b2947a7bc3403109e652d91")

# Cache Configuration
CACHE_TTL = 30  # seconds

# Rate Limiting
USER_COOLDOWN = 2  # seconds

# API Configuration
API_TIMEOUT = 10
API_RETRY_ATTEMPTS = 3

# Supported Currencies
SUPPORTED_CURRENCIES = {
    "TON": "💎",
    "USDT": "💵",
    "USD": "🇺🇸",
    "INR": "🇮🇳",
    "RUB": "🇷🇺",
    "EUR": "🇪🇺",
    "STAR": "⭐",
}

# API Endpoints
COINGECKO_API = "https://api.coingecko.com/api/v3"
EXCHANGERATE_API = "https://api.exchangerate-api.com/v4/latest/USD"
BINANCE_API = "https://api.binance.com/api/v3"

# Bot Footer
BOT_FOOTER = "\n\n@cyber_amit"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"