# main.py
from job.DataSources.job_scraper import JobScraper
from job.Utils.config_manager import CONFIG, SEARCH_TERMS

def main():
    scraper = JobScraper()
    scraper.run()

if __name__ == "__main__":
    main()
