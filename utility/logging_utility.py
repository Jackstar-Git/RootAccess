import logging
import os
from logging.handlers import RotatingFileHandler

# =====================================
# Setup Logger for the application
# =====================================

log_file = os.path.join("logs", "app.log")

# Create the log directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Set up the formatter for log messages
formatter = logging.Formatter("%(asctime)s: %(levelname)s - %(message)s", "%b %dth, %Y - %H:%M:%S")

# Set up the rotating file handler for logging
handler = RotatingFileHandler(log_file, mode='a', maxBytes=10 * 1024 * 1024,
                              backupCount=2, encoding="utf-8", delay=False)

handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

# Set up the main logger
logger = logging.getLogger("Main")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.debug("Logging setup completed successfully.")
