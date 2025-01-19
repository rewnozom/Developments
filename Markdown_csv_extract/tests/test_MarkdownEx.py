import unittest
import os
import shutil
import logging
import toml
from pathlib import Path
from typing import Dict, Any

# Add parent directory to sys.path to import the module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summerize_extract.Extractorz import MarkdownEx

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_markdown_ex.log'),
        logging.StreamHandler()
    ]
)

class TestMarkdownEx(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Step 1: Create test directory structure
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_dir = os.path.join(self.root_dir, "test_output")
        self.base_dir = os.path.join(self.test_dir, "base")
        self.output_dir = os.path.join(self.test_dir, "output")
        self.settings_path = os.path.join(self.test_dir, "settings.toml")
        
        # Step 2: Clean and create directories
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        os.makedirs(self.base_dir)
        os.makedirs(self.output_dir)
        
        # Step 3: Create test settings file
        self.create_test_settings()
        
        # Step 4: Create sample test files
        self.create_test_files()
        
        logging.info(f"Test environment setup complete - Test dir: {self.test_dir}")

    def create_test_settings(self):
        """Create a test settings.toml file"""
        settings = {
            'paths': {
                'path_style': 'windows',
                'output_dir': self.output_dir,
                'skip_paths': [os.path.join(self.base_dir, 'skip_me')]
            },
            'directories': {
                'ignored_directories': ['node_modules', '__pycache__']
            },
            'files': {
                'ignored_extensions': ['.pyc', '.pyo'],
                'ignored_files': ['ignored.txt']
            },
            'file_specific': {
                'use_file_specific': False,
                'specific_files': []
            },
            'output': {
                'markdown_file_prefix': 'Full_Project'
            }
        }
        with open(self.settings_path, 'w') as f:
            toml.dump(settings, f)

    def create_test_files(self):
        """Create sample test files"""
        # Step 1: Create regular Python file
        test_py = os.path.join(self.base_dir, 'test.py')
        with open(test_py, 'w') as f:
            f.write('def test():\n    pass\n')
        
        # Step 2: Create binary file
        binary_file = os.path.join(self.base_dir, 'binary.bin')
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03')
        
        # Step 3: Create ignored file
        ignored_file = os.path.join(self.base_dir, 'ignored.txt')
        with open(ignored_file, 'w') as f:
            f.write('This should be ignored')

    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        logging.info("Test environment cleaned up")

    def test_initialization(self):
        """Test MarkdownEx initialization and path normalization"""
        # Step 1: Create instance
        markdown_ex = MarkdownEx(self.base_dir, self.output_dir, self.settings_path)
        
        # Step 2: Verify paths are normalized
        self.assertTrue(isinstance(markdown_ex.base_dir, str))
        self.assertTrue(isinstance(markdown_ex.output_dir, str))
        self.assertTrue(isinstance(markdown_ex.settings_path, str))
        self.assertTrue('\\' not in markdown_ex.base_dir)
        self.assertTrue('\\' not in markdown_ex.output_dir)
        
        # Step 3: Verify settings loaded correctly
        self.assertTrue(isinstance(markdown_ex.settings, dict))
        self.assertEqual(markdown_ex.settings['paths']['path_style'], 'windows')
        
        # Step 4: Verify running state
        self.assertTrue(markdown_ex._is_running)
        
        # Step 5: Verify directories created
        self.assertTrue(os.path.exists(self.output_dir))

    def test_format_path(self):
        """Test path formatting functionality"""
        # Step 1: Create instance
        markdown_ex = MarkdownEx(self.base_dir, self.output_dir, self.settings_path)
        
        # Step 2: Test Windows style path formatting
        test_path = "test/path/file.py"
        windows_path = markdown_ex.format_path(test_path)
        self.assertIn('\\', windows_path)
        self.assertTrue(windows_path.startswith('..'))
        
        # Step 3: Test Unix style path formatting
        markdown_ex.settings['paths']['path_style'] = 'unix'
        unix_path = markdown_ex.format_path(test_path)
        self.assertIn('/', unix_path)
        self.assertTrue(unix_path.startswith('.'))

    def test_is_binary_file(self):
        """Test binary file detection"""
        # Step 1: Create instance
        markdown_ex = MarkdownEx(self.base_dir, self.output_dir, self.settings_path)
        
        # Step 2: Test text file
        text_file = os.path.join(self.base_dir, 'test.py')
        self.assertFalse(markdown_ex.is_binary_file(text_file))
        
        # Step 3: Test binary file
        binary_file = os.path.join(self.base_dir, 'binary.bin')
        self.assertTrue(markdown_ex.is_binary_file(binary_file))

    def test_should_skip_directory(self):
        """Test directory skipping logic"""
        # Step 1: Create instance
        markdown_ex = MarkdownEx(self.base_dir, self.output_dir, self.settings_path)
        
        # Step 2: Test ignored directory
        self.assertTrue(markdown_ex.should_skip_directory('node_modules'))
        
        # Step 3: Test skip path
        skip_path = os.path.join(self.base_dir, 'skip_me')
        self.assertTrue(markdown_ex.should_skip_directory(skip_path))
        
        # Step 4: Test valid directory
        valid_path = os.path.join(self.base_dir, 'valid')
        self.assertFalse(markdown_ex.should_skip_directory(valid_path))

    def test_get_files_in_directory(self):
        """Test file collection functionality"""
        # Step 1: Create instance
        markdown_ex = MarkdownEx(self.base_dir, self.output_dir, self.settings_path)
        
        # Step 2: Test normal file collection
        files = markdown_ex.get_files_in_directory(self.base_dir)
        self.assertTrue(any('test.py' in f for f in files))
        self.assertFalse(any('ignored.txt' in f for f in files))
        
        # Step 3: Test with file_specific mode
        markdown_ex.settings['file_specific']['use_file_specific'] = True
        markdown_ex.settings['file_specific']['specific_files'] = ['test.py']
        specific_files = markdown_ex.get_files_in_directory(self.base_dir)
        self.assertEqual(len(specific_files), 1)
        self.assertTrue('test.py' in specific_files[0])

if __name__ == '__main__':
    unittest.main()