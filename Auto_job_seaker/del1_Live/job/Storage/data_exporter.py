# ..\..\job\Storage\data_exporter.py
# data_exporter.py
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import logging

from job.Utils.config_manager import CONFIG

def update_files(all_jobs: List[Dict], current_csv_path: Path, current_md_path: Path, logger: logging.Logger):
    """Update both CSV and Markdown files with current sorted jobs"""
    all_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    df = pd.DataFrame(all_jobs)
    df.to_csv(current_csv_path, index=False, encoding='utf-8-sig')
    
    with open(current_md_path, 'w', encoding='utf-8') as f:
        f.write("# Job Listings (Sorted by Score)\n\n")
        f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Jobs Found: {len(all_jobs)}\n\n")
        
        for job in all_jobs:
            f.write(f"## [{job['title']}]({job['url']})\n")
            f.write(f"**Score:** {job['score']}  \n")
            f.write(f"**Company:** {job['company']}  \n")
            f.write(f"**Location:** {job['location']}  \n")
            f.write(f"**Posted:** {job['how_long']}  \n")
            f.write(f"**Found:** {job['found_date']}  \n\n")
            f.write("### Description\n")
            f.write(f"{job['description']}\n\n---\n\n")
    
    logger.debug(f"Updated files with {len(all_jobs)} jobs")

def save_results(all_jobs: List[Dict], logger):
    """Save results to both CSV and JSON with scores"""
    if not all_jobs:
        logger.warning("No jobs to save")
        return
        
    # Sort by score
    all_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save to CSV
    output_dir = Path(CONFIG["output_dir"])
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / f"jobs_{timestamp}.csv"
    pd.DataFrame(all_jobs).to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    # Save to JSON
    json_path = output_dir / f"jobs_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Saved {len(all_jobs)} jobs to {csv_path} and {json_path}")
    
    # Skapa en Markdown-fil med detaljerad information
    md_path = output_dir / f"jobs_{timestamp}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Job Listings (Sorted by Score)\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Jobs Found: {len(all_jobs)}\n\n")
        
        for job in all_jobs:
            f.write(f"## [{job['title']}]({job['url']})\n")
            f.write(f"**Score:** {job['score']}  \n")
            f.write(f"**Company:** {job['company']}  \n")
            f.write(f"**Location:** {job['location']}  \n")
            f.write(f"**Posted:** {job['how_long']}  \n")
            f.write(f"**Found:** {job['found_date']}  \n\n")
            f.write("### Description\n")
            f.write(f"{job['description']}\n\n---\n\n")
    
    logger.info(f"Saved detailed Markdown report to {md_path}")

