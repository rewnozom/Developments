# ..\..\job\DataSources\job_parser.py
# job_parser.py
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
import logging

from job.DataProcessing.job_scorer import score_job
from job.DataProcessing.duplicate_handler import is_duplicate_job
from job.Storage.data_exporter import update_files
from job.Utils.config_manager import CONFIG

def parse_job(element: BeautifulSoup, logger: logging.Logger, processed_urls: set) -> Optional[Dict[str, Any]]:
    """Parse a job listing element"""
    try:
        title_elem = (
            element.select_one('a._8w9Ce2') or
            element.select_one('div.MhjGza > h2 > a') or
            element.select_one('h2 > a') or
            element.select_one('a[href*="jooble.org"]')
        )
        
        if not title_elem:
            return None
            
        title = title_elem.get_text(strip=True)
        url = title_elem.get('href', '').strip()
        if not url.startswith('http'):
            url = f"https://se.jooble.org{url}"
            
        # Uppdaterade selektorer för beskrivning
        desc_elem = (
            element.select_one('div.GEyos4') or
            element.select_one('div.PAM72f') or
            element.select_one('div.slQ-DR')
        )
        description = desc_elem.get_text(separator=' ', strip=True) if desc_elem else ""
        
        company_elem = (
            element.select_one('p.z6WlhX') or
            element.select_one('[data-test-name="_companyName"]')
        )
        if company_elem:
            # Extrahera endast direkt text utan inbäddade element
            company_text = ''.join(
                [text for text in company_elem.find_all(text=True, recursive=False)]
            ).strip()
            company = company_text if company_text else "Unknown"
        else:
            company = "Unknown"
        
        # Extrahera plats
        location_elem = (
            element.select_one('div.caption.NTRJBV') or
            element.select_one('.location')
        )
        location = location_elem.get_text(strip=True) if location_elem else "Stockholm"
        
        # Extrahera "hur länge sedan"
        how_long_elem = (
            element.select_one('div.caption.Vk-5Da') or
            element.select_one('div.how-long')  # Lägg till fler selektorer om nödvändigt
        )
        how_long = how_long_elem.get_text(strip=True) if how_long_elem else "Okänt"

        job = {
            "title": title,
            "url": url,
            "company": company,
            "location": location,
            "description": description,
            "how_long": how_long,  # Nytt fält
            "found_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if not is_duplicate_job(processed_urls, job["url"]):
            job["score"] = score_job(job)
            return job
        
        return None
        
    except Exception as e:
        logger.error(f"Error parsing job: {e}")
        return None
