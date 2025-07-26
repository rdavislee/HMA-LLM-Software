import logging
import sys
from backend.src.core.config import settings

def get_logger(name: str) -> logging.Logger:
    """Configures and returns a logger."""
    logger = logging.getLogger(name)
    
    # Set the level for the logger from settings. This is the master switch.
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # If handlers are already configured, don't add them again to avoid duplicate logs.
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(stream_handler)
    
    return logger
