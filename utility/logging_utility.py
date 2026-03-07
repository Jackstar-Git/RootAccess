import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Final

LOG_DIR: Final[str] = "logs"
LOG_FILE: Final[str] = os.path.join(LOG_DIR, "app.log")
MAX_BYTES: Final[int] = 10 * 1024 * 1024
BACKUP_COUNT: Final[int] = 2

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logger: logging.Logger = logging.getLogger("Main")
logger.setLevel(logging.DEBUG)

formatter: logging.Formatter = logging.Formatter(
    fmt="%(asctime)s: %(levelname)s - %(message)s", 
    datefmt="%b %dth, %Y - %H:%M:%S"
)

handler: RotatingFileHandler = RotatingFileHandler(
    filename=LOG_FILE,
    mode="a",
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT,
    encoding="utf-8",
    delay=False
)

handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.debug("Logging setup completed successfully.")