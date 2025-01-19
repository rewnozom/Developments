# tests/conftest.py
import pytest
from pathlib import Path
from typing import Dict, Any
import json
import yaml

@pytest.fixture
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent / "data"

@pytest.fixture
def config_data() -> Dict[str, Any]:
    """Return test configuration data."""
    return {
        'system': {
            'debug_mode': True,
            'environment': 'testing',
            'max_retries': 3,
            'timeout': 30
        },
        'security': {
            'enable_safety_filters': True,
            'content_filtering': True,
            'max_tokens': 1000,
            'rate_limit': 60
        },
        'resources': {
            'base_path': 'resources',
            'max_file_size': 1048576,
            'allowed_extensions': ['.txt', '.json', '.yaml', '.md']
        },
        'logging': {
            'level': 'DEBUG',
            'file_path': 'logs/test.log',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }

@pytest.fixture
def temp_config_file(tmp_path: Path, config_data: Dict[str, Any]) -> Path:
    """Create temporary config file."""
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    return config_file

@pytest.fixture
def sample_conversation_data() -> Dict[str, Any]:
    """Return sample conversation data."""
    return {
        'messages': [
            {
                'role': 'user',
                'content': 'Hello!',
                'timestamp': '2024-01-01T10:00:00'
            },
            {
                'role': 'assistant',
                'content': 'Hi! How can I help you today?',
                'timestamp': '2024-01-01T10:00:01'
            }
        ],
        'metadata': {
            'created_at': '2024-01-01T10:00:00',
            'modified_at': '2024-01-01T10:00:01',
            'total_messages': 2,
            'total_tokens': 20
        }
    }

@pytest.fixture
def test_logger(tmp_path: Path):
    """Create test logger."""
    import logging
    
    log_file = tmp_path / "test.log"
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    
    handler = logging.FileHandler(log_file)
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    logger.addHandler(handler)
    return logger