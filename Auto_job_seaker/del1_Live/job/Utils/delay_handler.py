# delay_handler.py
import random
import time
from typing import Dict
import logging

from job.Utils.config_manager import CONFIG

def random_delay(config: Dict, logger: logging.Logger):
    """Add random delay between actions"""
    delay = random.uniform(
        config["random_delays"]["min"],
        config["random_delays"]["max"]
    )
    logger.debug(f"Sleeping for {delay:.2f} seconds")
    time.sleep(delay)
