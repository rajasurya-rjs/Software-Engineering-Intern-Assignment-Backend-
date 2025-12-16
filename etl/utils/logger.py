# etl/utils/logger.py

import logging
import os

LOG_DIR = "etl/logs"
LOG_FILE = os.path.join(LOG_DIR, "etl.log")

def get_logger():
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("ETL")
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
