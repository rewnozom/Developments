# scripts/utils/validate.py
import sys
from pathlib import Path
import logging
import yaml
import json
from typing import Any, Dict, Optional

def validate_config_file(config_path: Path) -> bool:
    """Validate configuration file."""
    try:
        if not config_path.exists():
            logging.error(f"Config file not found: {config_path}")
            return False
            
        # Load config
        if config_path.suffix == '.json':
            with open(config_path) as f:
                config = json.load(f)
        elif config_path.suffix in ('.yaml', '.yml'):
            with open(config_path) as f:
                config = yaml.safe_load(f)
        else:
            logging.error(f"Unsupported config format: {config_path.suffix}")
            return False
            
        # Validate required sections
        required_sections = ['system', 'security', 'resources', 'logging']
        for section in required_sections:
            if section not in config:
                logging.error(f"Missing required section: {section}")
                return False
                
        return True
        
    except Exception as e:
        logging.error(f"Config validation failed: {str(e)}")
        return False

def validate_directory_structure(base_dir: Path = Path(".")) -> bool:
    """Validate project directory structure."""
    required_dirs = [
        "logs",
        "data",
        "cache",
        "temp",
        "resources"
    ]
    
    success = True
    for directory in required_dirs:
        dir_path = base_dir / directory
        if not dir_path.exists():
            logging.error(f"Missing required directory: {directory}")
            success = False
            
    return success

def validate_requirements(requirements_file: Path) -> bool:
    """Validate requirements file."""
    try:
        if not requirements_file.exists():
            logging.error(f"Requirements file not found: {requirements_file}")
            return False
            
        with open(requirements_file) as f:
            requirements = f.readlines()
            
        # Basic validation of requirement format
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                # Check for valid requirement format
                if not any(char in req for char in ['==', '>=', '<=', '>']):
                    logging.warning(f"Possibly invalid requirement format: {req}")
                    
        return True
        
    except Exception as e:
        logging.error(f"Requirements validation failed: {str(e)}")
        return False

def validate_project_structure() -> bool:
    """Validate entire project structure."""
    success = True
    
    # Validate directory structure
    if not validate_directory_structure():
        success = False
        
    # Validate config files
    config_files = [
        Path("config/settings.yaml"),
        Path("config/logging.yaml")
    ]
    
    for config_file in config_files:
        if not validate_config_file(config_file):
            success = False
            
    # Validate requirements
    requirements_files = [
        Path("requirements.txt"),
        Path("requirements/dev.txt")
    ]
    
    for req_file in requirements_files:
        if not validate_requirements(req_file):
            success = False
            
    return success

def main():
    """Main validation script."""
    logging.basicConfig(level=logging.INFO)
    
    logging.info("Validating project structure...")
    if validate_project_structure():
        logging.info("Validation successful.")
    else:
        logging.error("Validation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()