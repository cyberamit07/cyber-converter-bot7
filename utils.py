"""
Utility functions for formatting
"""

from typing import Dict
from config import SUPPORTED_CURRENCIES, BOT_FOOTER
from logger import setup_logger

logger = setup_logger(__name__)


def format_conversion_result(from_currency: str, amount: float, conversions: Dict[str, float]) -> str:
    """Format conversion results"""
    lines = []
    
    currency_order = ["TON", "USDT", "USD", "INR", "RUB", "EUR", "STAR"]
    
    for currency in currency_order:
        if currency in conversions:
            emoji = SUPPORTED_CURRENCIES.get(currency, "")
            value = conversions[currency]
            
            # Format numbers
            if value >= 1000:
                formatted_value = f"{value:,.2f}"
            elif value >= 1:
                formatted_value = f"{value:.4f}"
            else:
                formatted_value = f"{value:.6f}"
            
            lines.append(f"{emoji} {currency} : {formatted_value}")
    
    result = "\n".join(lines) + BOT_FOOTER
    return result


def format_rate_info(rates: Dict[str, float]) -> str:
    """Format current rates"""
    lines = ["📊 **Current Exchange Rates**\n"]
    
    currency_order = ["TON", "USDT", "USD", "INR", "RUB", "EUR", "STAR"]
    
    for currency in currency_order:
        if currency in rates:
            emoji = SUPPORTED_CURRENCIES.get(currency, "")
            rate = rates[currency]
            
            if currency == "STAR":
                lines.append(f"{emoji} 1 USD = {rate:.2f} {currency}")
            else:
                lines.append(f"{emoji} 1 {currency} = ${rate:.4f}")
    
    return "\n".join(lines) + BOT_FOOTER