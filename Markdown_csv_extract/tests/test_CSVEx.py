import unittest
import os
import shutil
import logging
import toml
import pandas as pd
from pathlib import Path
from typing import Dict, Any

# Add parent directory to sys.path to import the module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summerize_extract.Extractorz import CSVEx

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_csv_ex.log'),
        logging.StreamHandler()
    ]
)

class TestCSVEx(unittest.TestCase):
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
            'metrics': {
                'size_unit': 'KB'
            },
            'output': {
                'csv_file_prefix': 'Detailed_Project'
            }
        }
        with open(self.settings_path, 'w') as f:
            toml.dump(settings, f)

    def create_test_files(self):
        """Create sample test files"""
        # Step 1: Create Python file with class and functions
        test_py = os.path.join(self.base_dir, 'test.py')
        with open(test_py, 'w') as f:
            f.write('''
class TestClass:
    def __init__(self):
        self.value = 42

    def test_method(self):
        x = 10
        return x + self.value

def standalone_function():
    pass
''')
        
        # Step 2: Create a simple text file
        test_txt = os.path.join(self.base_dir, 'test.txt')
        with open(test_txt, 'w') as f:
            f.write('Hello\nWorld\n')

    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        logging.info("Test environment cleaned up")

    def test_initialization(self):
        """Test CSVEx initialization"""
        # Step 1: Create instance
        csv_ex = CSVEx(self.base_dir, self.output_dir, self.settings_path)
        
        # Step 2: Verify paths are normalized
        self.assertTrue(isinstance(csv_ex.base_dir, str))
        self.assertTrue(isinstance(csv_ex.output_dir, str))
        self.assertTrue('\\' not in csv_ex.base_dir)
        self.assertTrue('\\' not in csv_ex.output_dir)
        
        # Step 3: Verify settings loaded correctly
        self.assertTrue(isinstance(csv_ex.settings, dict))
        self.assertEqual(csv_ex.settings['metrics']['size_unit'], 'KB')
        
        # Step 4: Verify running state
        self.assertTrue(csv_ex._is_running)

    def test_count_file_metrics(self):
        """Test file metrics counting functionality"""
        # Step 1: Create test file with known metrics
        test_file = os.path.join(self.base_dir, 'metrics_test.txt')
        content = "Line 1\nLine 2\nLine 3"
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Step 2: Calculate expected metrics
        expected_chars = len(content)
        expected_words = len(content.split())
        expected_lines = content.count('\n') + 1
        
        # Step 3: Get actual metrics
        char_count, word_count, line_count = CSVEx.count_file_metrics(test_file)
        
        # Step 4: Verify metrics
        self.assertEqual(char_count, expected_chars)
        self.assertEqual(word_count, expected_words)
        self.assertEqual(line_count, expected_lines)

    def test_count_classes_functions_variables(self):
        """Test counting of Python code elements"""
        # Step 1: Get Python test file path
        test_py = os.path.join(self.base_dir, 'test.py')
        
        # Step 2: Count elements
        class_count, function_count, variable_count = CSVEx.count_classes_functions_variables(test_py)
        
        # Step 3: Verify counts
        self.assertEqual(class_count, 1)  # TestClass
        self.assertEqual(function_count, 2)  # test_method and standalone_function
        self.assertTrue(variable_count >= 2)  # value and x at minimum

    def test_should_skip_directory(self):
        """Test directory skipping logic"""
        # Step 1: Create instance
        csv_ex = CSVEx(self.base_dir, self.output_dir, self.settings_path)
        
        # Step 2: Test ignored directory
        self.assertTrue(csv_ex.should_skip_directory('node_modules'))
        
        # Step 3: Test skip path
        skip_path = os.path.join(self.base_dir, 'skip_me')
        self.assertTrue(csv_ex.should_skip_directory(skip_path))
        
        # Step 4: Test valid directory
        valid_path = os.path.join(self.base_dir, 'valid')
        self.assertFalse(csv_ex.should_skip_directory(valid_path))

    def test_generate_directory_tree_with_detailed_metrics(self):
        """Test directory tree generation with metrics"""
        # Step 1: Create instance
        csv_ex = CSVEx(self.base_dir, self.output_dir, self.settings_path)
        
        # Step 2: Generate directory tree
        tree_data = csv_ex.generate_directory_tree_with_detailed_metrics()
        
        # Step 3: Verify tree structure
        self.assertTrue(isinstance(tree_data, list))
        self.assertTrue(len(tree_data) > 0)
        
        # Step 4: Check data format
        first_entry = tree_data[0]
        self.assertEqual(len(first_entry), 3)  # [Path, Metrics, Code]
        self.assertTrue(isinstance(first_entry[0], str))  # Path is string
        self.assertTrue(isinstance(first_entry[1], str))  # Metrics is string
        self.assertTrue(isinstance(first_entry[2], str))  # Code is string
        
        # Step 5: Verify metrics format
        metrics = first_entry[1]
        self.assertIn('KB', metrics)
        self.assertIn('C', metrics)  # Chars
        self.assertIn('W', metrics)  # Words
        self.assertIn('L', metrics)  # Lines

if __name__ == '__main__':
    unittest.main()