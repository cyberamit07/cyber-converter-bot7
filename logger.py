"""
Logging configuration
"""

import logging
import sys
from config import LOG_LEVEL, LOG_FORMAT


def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup and return logger"""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, LOG_LEVEL))
    
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


logger = setup_logger("CurrencyBot")