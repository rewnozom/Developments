# scripts/utils/install.py
import subprocess
import sys
from pathlib import Path
import logging

def install_requirements(requirements_file: str = "requirements.txt") -> bool:
    """Install required packages from requirements file."""
    try:
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "-r", 
            requirements_file
        ])
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install requirements: {str(e)}")
        return False

def install_dev_requirements() -> bool:
    """Install development requirements."""
    return install_requirements("requirements/dev.txt")

def setup_development_environment() -> bool:
    """Set up development environment."""
    try:
        # Create necessary directories
        directories = [
            "logs",
            "data",
            "cache",
            "temp",
            "resources"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            
        # Install requirements
        if not install_requirements():
            return False
            
        # Install dev requirements
        if not install_dev_requirements():
            return False
            
        return True
        
    except Exception as e:
        logging.error(f"Failed to setup development environment: {str(e)}")
        return False

def main():
    """Main setup script."""
    logging.basicConfig(level=logging.INFO)
    
    logging.info("Setting up development environment...")
    if setup_development_environment():
        logging.info("Development environment setup complete.")
    else:
        logging.error("Development environment setup failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()