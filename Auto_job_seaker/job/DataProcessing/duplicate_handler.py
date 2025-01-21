# ..\..\job\DataProcessing\duplicate_handler.py
# duplicate_handler.py
from typing import Dict, Any
import logging

def is_duplicate_job(processed_urls: set, job_url: str) -> bool:
    """Check if a job is a duplicate based on URL"""
    if job_url in processed_urls:
        return True
    processed_urls.add(job_url)
    return False
