"""
Exchange rate fetcher with multiple API sources
"""

import asyncio
from typing import Dict, Optional
import aiohttp
from logger import setup_logger
from config import (
    API_TIMEOUT,
    API_RETRY_ATTEMPTS,
    COINGECKO_API,
    EXCHANGERATE_API,
    BINANCE_API,
    GETBLOCK_API
)
from cache import rate_cache

logger = setup_logger(__name__)


class RateFetcher:
    """Fetch exchange rates from multiple sources"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        logger.info("✅ RateFetcher initialized")
    
    async def _fetch_with_retry(self, url: str, attempts: int = API_RETRY_ATTEMPTS) -> Optional[Dict]:
        """Fetch data with retry logic"""
        for attempt in range(1, attempts + 1):
            try:
                async with self.session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.warning(f"API returned status {response.status}")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout attempt {attempt}/{attempts}")
            except Exception as e:
                logger.warning(f"Error attempt {attempt}/{attempts}: {e}")
            
            if attempt < attempts:
                await asyncio.sleep(0.5 * attempt)
        
        return None
    
    async def _fetch_ton_rate(self) -> Optional[float]:
        """Fetch TON price in USD"""
        try:
            # Try CoinGecko first
            data = await self._fetch_with_retry(
                f"{COINGECKO_API}/simple/price?ids=the-open-network&vs_currencies=usd"
            )
            
            if data and "the-open-network" in data:
                price = float(data["the-open-network"]["usd"])
                logger.info(f"💎 TON rate: ${price}")
                return price
            
            # Fallback to Binance
            data = await self._fetch_with_retry(
                f"{BINANCE_API}/ticker/price?symbol=TONUSDT"
            )
            
            if data and "price" in data:
                price = float(data["price"])
                logger.info(f"💎 TON rate (Binance): ${price}")
                return price
            
            # Hardcoded fallback
            logger.warning("Using fallback TON rate")
            return 5.5
            
        except Exception as e:
            logger.error(f"Error fetching TON rate: {e}")
            return 5.5
    
    async def _fetch_fiat_rates(self) -> Dict[str, float]:
        """Fetch fiat currency rates"""
        try:
            data = await self._fetch_with_retry(EXCHANGERATE_API)
            
            if data and "rates" in data:
                rates = {
                    "USD": 1.0,
                    "INR": float(data["rates"].get("INR", 83.0)),
                    "RUB": float(data["rates"].get("RUB", 90.0)),
                    "EUR": float(data["rates"].get("EUR", 0.92)),
                }
                logger.info(f"💵 Fiat rates fetched")
                return rates
        except Exception as e:
            logger.error(f"Error fetching fiat rates: {e}")
        
        # Fallback rates
        return {
            "USD": 1.0,
            "INR": 83.0,
            "RUB": 90.0,
            "EUR": 0.92,
        }
    
    async def _fetch_star_rate(self) -> float:
        """Get Telegram Stars rate (1 USD ≈ 67 Stars)"""
        return 67.0
    
    async def get_all_rates(self) -> Optional[Dict[str, float]]:
        """Fetch all exchange rates with caching"""
        # Check cache
        cached_rates = await rate_cache.get("all_rates")
        if cached_rates:
            logger.debug("Using cached rates")
            return cached_rates
        
        logger.info("Fetching fresh rates...")
        
        try:
            # Fetch all rates concurrently
            ton_task = self._fetch_ton_rate()
            fiat_task = self._fetch_fiat_rates()
            star_task = self._fetch_star_rate()
            
            ton_rate, fiat_rates, star_rate = await asyncio.gather(
                ton_task,
                fiat_task,
                star_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(ton_rate, Exception) or ton_rate is None:
                ton_rate = 5.5
            
            if isinstance(fiat_rates, Exception) or fiat_rates is None:
                fiat_rates = {"USD": 1.0, "INR": 83.0, "RUB": 90.0, "EUR": 0.92}
            
            if isinstance(star_rate, Exception):
                star_rate = 67.0
            
            # Compile rates
            rates = {
                "TON": ton_rate,
                "USDT": 1.0,
                "USD": fiat_rates["USD"],
                "INR": fiat_rates["INR"],
                "RUB": fiat_rates["RUB"],
                "EUR": fiat_rates["EUR"],
                "STAR": star_rate,
            }
            
            # Cache rates
            await rate_cache.set("all_rates", rates)
            
            logger.info(f"✅ Rates cached: TON=${rates['TON']:.2f}")
            return rates
            
        except Exception as e:
            logger.error(f"Error in get_all_rates: {e}")
            # Return fallback rates
            return {
                "TON": 5.5,
                "USDT": 1.0,
                "USD": 1.0,
                "INR": 83.0,
                "RUB": 90.0,
                "EUR": 0.92,
                "STAR": 67.0,
            }
    
    async def convert(self, amount: float, from_currency: str, rates: Dict[str, float]) -> Dict[str, float]:
        """Convert amount to all currencies"""
        try:
            # Convert to USD first
            if from_currency == "STAR":
                usd_value = amount / rates["STAR"]
            else:
                usd_value = amount * rates[from_currency]
            
            # Convert to all currencies
            result = {}
            for currency, rate in rates.items():
                if currency == "STAR":
                    result[currency] = usd_value * rate
                else:
                    result[currency] = usd_value / rate
            
            return result
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return {}