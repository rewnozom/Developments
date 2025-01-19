# ..\..\job\DataProcessing\job_filter.py
# job_filter.py
from typing import List, Dict
from datetime import datetime, timedelta
import re
import logging

from job.Utils.config_manager import CONFIG

def filter_jobs(jobs: List[Dict]) -> List[Dict]:
    """Filter jobs based on how long ago they were posted"""
    if not CONFIG["date_filter"]["enabled"]:
        return jobs

    max_days = CONFIG["date_filter"]["max_days"]
    filtered_jobs = []
    logger = logging.getLogger("JobScraper")

    for job in jobs:
        how_long_str = job.get("how_long", "").lower()
        days_posted = parse_how_long(how_long_str)
        if days_posted is None:
            logger.debug(f"Could not parse how_long for job {job['url']}: '{how_long_str}'")
            continue  # Exclude jobs where we can't determine the posting date

        if days_posted <= max_days:
            filtered_jobs.append(job)
        else:
            logger.debug(f"Excluding job {job['url']} posted {days_posted} days ago (max {max_days})")

    return filtered_jobs

def parse_how_long(how_long_str: str) -> int:
    """
    Parse the 'how long ago' string and return the number of days.
    Examples:
        "3 dagar sedan" -> 3
        "1 vecka sedan" -> 7
        "2 veckor sedan" -> 14
        "1 månad sedan" -> 30
    """
    try:
        if not how_long_str:
            return None

        how_long_str = how_long_str.lower()
        match = re.match(r"(\d+)\s+(\w+)\s+sedan", how_long_str)
        if not match:
            return None

        quantity = int(match.group(1))
        unit = match.group(2)

        if "dag" in unit:
            return quantity
        elif "vecka" in unit:
            return quantity * 7
        elif "månad" in unit:
            return quantity * 30
        elif "år" in unit:
            return quantity * 365
        else:
            return None
    except Exception:
        return None
