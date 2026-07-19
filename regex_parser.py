"""
Currency pattern parser
"""

import re
from typing import Optional, Tuple
from logger import setup_logger

logger = setup_logger(__name__)


class CurrencyParser:
    """Parse currency expressions from text"""
    
    ALIASES = {
        "t": "TON",
        "ton": "TON",
        "usdt": "USDT",
        "tether": "USDT",
        "usd": "USD",
        "dollar": "USD",
        "dollars": "USD",
        "inr": "INR",
        "rupee": "INR",
        "rupees": "INR",
        "rub": "RUB",
        "ruble": "RUB",
        "rubles": "RUB",
        "eur": "EUR",
        "euro": "EUR",
        "euros": "EUR",
        "star": "STAR",
        "stars": "STAR",
    }
    
    PATTERN = re.compile(
        r'\b(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\b',
        re.IGNORECASE
    )
    
    @classmethod
    def parse(cls, text: str) -> Optional[Tuple[float, str]]:
        """Parse text and extract currency info"""
        if not text or not isinstance(text, str):
            return None
        
        text = text.strip()
        matches = cls.PATTERN.findall(text)
        
        if not matches:
            return None
        
        for amount_str, currency_str in matches:
            try:
                amount = float(amount_str)
                currency = currency_str.lower().strip()
                
                if currency in cls.ALIASES:
                    actual_currency = cls.ALIASES[currency]
                    return (amount, actual_currency)
            except ValueError:
                continue
        
        return None
    
    @classmethod
    def is_currency_message(cls, text: str) -> bool:
        """Check if text contains currency"""
        return cls.parse(text) is not None


parser = CurrencyParser()