# ..\..\job\DataSources\job_scraper.py
# job_scraper.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import pandas as pd
import time
import random
import json
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from job.Utils.logger_setup import get_logger
from job.Utils.delay_handler import random_delay
from job.DataSources.job_parser import parse_job
from job.Storage.data_exporter import update_files, save_results
from job.DataProcessing.job_scorer import score_job
from job.DataProcessing.duplicate_handler import is_duplicate_job
from job.Utils.config_manager import CONFIG, SEARCH_TERMS

class JobScraper:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger, self.current_csv_path, self.current_md_path = get_logger(self.timestamp)
        self.jobs: List[Dict[str, Any]] = []
        self.processed_urls = set()
        self.setup_directories()

    def setup_directories(self):
        """Create necessary output directories"""
        Path(CONFIG["output_dir"]).mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

    def scrape_page(self, page_num: int, search_term: str) -> List[Dict[str, Any]]:
        """Scrape a single page of job listings with optimized performance"""
        encoded_search = quote(search_term)
        url = CONFIG["base_url"].format(page_num, encoded_search)
        jobs_on_page = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=not CONFIG["browser_visible"],
                    args=['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
                )
                context = browser.new_context(
                    viewport={"width": 800, "height": 600},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                context.set_default_timeout(30000)
                context.set_default_navigation_timeout(30000)
                
                page = context.new_page()
                self.logger.info(
                    "Accessing page {} for search term: {}".format(page_num, search_term)
                )
                
                try:
                    page.goto(url, wait_until="networkidle", timeout=CONFIG["performance"]["page_load_wait"] * 1000)
                except Exception as e:
                    self.logger.warning("Page load warning: {}".format(str(e)))
                
                time.sleep(CONFIG["performance"]["min_delay"])
                
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Uppdaterad selector för att inkludera alla jobbkort
                job_elements = soup.find_all('div', {'data-test-name': '_jobCard'})
                
                if not job_elements:
                    self.logger.warning(
                        "No jobs found on page {} for search term: {}".format(page_num, search_term)
                    )
                    return []
                
                self.logger.info(
                    "Found {} potential jobs on page {}".format(len(job_elements), page_num)
                )
                
                current_batch = []
                for elem in job_elements:
                    job = parse_job(elem, self.logger, self.processed_urls)
                    if job:
                        jobs_on_page.append(job)
                        current_batch.append(job)
                        
                        if len(current_batch) >= CONFIG["performance"]["batch_size"]:
                            # Filtrera jobb om filtrering är aktiverad
                            filtered_jobs = self.apply_filters(current_batch)
                            self.jobs.extend(filtered_jobs)
                            for j in filtered_jobs:
                                self.logger.info(
                                    "[+] Found: {} | Company: {} | Score: {} | Location: {} | Posted: {}".format(
                                        j['title'], j['company'], j['score'], j['location'], j['how_long']
                                    )
                                )
                            update_files(self.jobs, self.current_csv_path, self.current_md_path, self.logger)
                            current_batch = []
                    
                    time.sleep(CONFIG["performance"]["min_delay"])
                
                # Hantera återstående jobb i den sista batchen
                if current_batch:
                    filtered_jobs = self.apply_filters(current_batch)
                    self.jobs.extend(filtered_jobs)
                    for j in filtered_jobs:
                        self.logger.info(
                            "[+] Found: {} | Company: {} | Score: {} | Location: {} | Posted: {}".format(
                                j['title'], j['company'], j['score'], j['location'], j['how_long']
                            )
                        )
                    update_files(self.jobs, self.current_csv_path, self.current_md_path, self.logger)
                
                browser.close()
                
        except PlaywrightTimeout:
            self.logger.error("Timeout on page {} for search term: {}".format(page_num, search_term))
        except Exception as e:
            self.logger.error("Error scraping page {} for search term {}: {}".format(page_num, search_term, e))
        
        return jobs_on_page

    def apply_filters(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply filters to a list of jobs"""
        from job.DataProcessing.job_filter import filter_jobs
        return filter_jobs(jobs)

    def run(self):
        """Main execution method"""
        total_jobs_found = 0
        
        try:
            for search_term in SEARCH_TERMS:
                self.logger.info("Starting search for term: {}".format(search_term))
                current_page = CONFIG["start_page"]
                consecutive_empty_pages = 0
                jobs_for_term = 0
                
                while consecutive_empty_pages < 3 and jobs_for_term < CONFIG["max_jobs_per_url_search"]:
                    self.logger.info("Processing page {} for search term: {}".format(current_page, search_term))
                    
                    jobs_on_page = self.scrape_page(current_page, search_term)
                    
                    if not jobs_on_page:
                        consecutive_empty_pages += 1
                        self.logger.warning(
                            "Empty page {} for term '{}'. Empty pages count: {}".format(
                                current_page, search_term, consecutive_empty_pages
                            )
                        )
                    else:
                        consecutive_empty_pages = 0
                        jobs_for_term += len(jobs_on_page)
                        total_jobs_found += len(jobs_on_page)
                        self.logger.info(
                            "Found {} jobs on page {}. Total for term '{}': {}".format(
                                len(jobs_on_page), current_page, search_term, jobs_for_term
                            )
                        )
                    
                    current_page += 1
                    random_delay(CONFIG, self.logger)
                
                self.logger.info(
                    "Completed search for term '{}'. Total jobs found for this term: {}".format(
                        search_term, jobs_for_term
                    )
                )
                
        except KeyboardInterrupt:
            self.logger.info("Scraping interrupted by user")
        except Exception as e:
            self.logger.error("Error during scraping: {}".format(e))
        finally:
            self.logger.info("Scraping completed. Total unique jobs found: {}".format(len(self.jobs)))
            save_results(self.jobs, self.logger)
