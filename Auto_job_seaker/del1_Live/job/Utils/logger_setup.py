# logger_setup.py
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple

from job.Utils.config_manager import CONFIG

def get_logger(timestamp: str) -> Tuple[logging.Logger, Path, Path]:
    logger = logging.getLogger("JobScraper")
    logger.setLevel(logging.DEBUG)

    # Rensa tidigare handlers om de finns
    if logger.handlers:
        logger.handlers.clear()

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    fh = logging.FileHandler(f"logs/scraper_{timestamp}.log", encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(file_formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    ch.setFormatter(console_formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    # Kontrollera och skapa output-katalogen
    output_dir = Path(CONFIG["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    current_csv_path = output_dir / f"jobs_{timestamp}.csv"
    current_md_path = output_dir / f"jobs_{timestamp}.md"

    # Skriv en rubrik till Markdown-filen
    with open(current_md_path, 'w', encoding='utf-8') as f:
        f.write("# Job Listings (Sorted by Score)\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    return logger, current_csv_path, current_md_path
