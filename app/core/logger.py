import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if not exists
os.makedirs("logs", exist_ok=True)

# Basic formatter
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

# File handler (rotating)
file_handler = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=3)
file_handler.setFormatter(formatter)

# Console handler (stdout)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Root logger config
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
