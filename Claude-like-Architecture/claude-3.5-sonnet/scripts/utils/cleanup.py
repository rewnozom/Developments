# scripts/utils/cleanup.py
import shutil
from pathlib import Path
import logging
import os
from typing import List, Optional

def cleanup_directory(directory: Path, 
                     file_patterns: Optional[List[str]] = None) -> bool:
    """Clean up a directory by removing files matching patterns."""
    try:
        if not directory.exists():
            return True
            
        if file_patterns:
            for pattern in file_patterns:
                for file_path in directory.glob(pattern):
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
        else:
            shutil.rmtree(directory)
            directory.mkdir(exist_ok=True)
            
        return True
        
    except Exception as e:
        logging.error(f"Failed to cleanup directory {directory}: {str(e)}")
        return False

def cleanup_temp_files(temp_dir: Path = Path("temp")) -> bool:
    """Clean up temporary files."""
    return cleanup_directory(temp_dir)

def cleanup_cache(cache_dir: Path = Path("cache")) -> bool:
    """Clean up cache files."""
    return cleanup_directory(cache_dir)

def cleanup_logs(log_dir: Path = Path("logs"),
                keep_latest: bool = True) -> bool:
    """Clean up log files."""
    try:
        if not log_dir.exists():
            return True
            
        log_files = sorted(log_dir.glob("*.log"), 
                          key=os.path.getmtime,
                          reverse=True)
                          
        # Keep latest log file if requested
        if keep_latest and log_files:
            log_files = log_files[1:]
            
        for log_file in log_files:
            log_file.unlink()
            
        return True
        
    except Exception as e:
        logging.error(f"Failed to cleanup logs: {str(e)}")
        return False

def cleanup_all(base_dir: Path = Path(".")) -> bool:
    """Clean up all temporary files, cache and logs."""
    success = True
    
    if not cleanup_temp_files(base_dir / "temp"):
        success = False
    if not cleanup_cache(base_dir / "cache"):
        success = False
    if not cleanup_logs(base_dir / "logs"):
        success = False
        
    return success

def main():
    """Main cleanup script."""
    logging.basicConfig(level=logging.INFO)
    
    logging.info("Starting cleanup...")
    if cleanup_all():
        logging.info("Cleanup completed successfully.")
    else:
        logging.error("Cleanup failed.")
        exit(1)

if __name__ == "__main__":
    main()