import unittest
import os
import shutil
import logging
import pandas as pd

# Add parent directory to sys.path to import the module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summerize_extract.Extractorz import reverse_csv_extraction

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_reverse_csv_extraction.log'),
        logging.StreamHandler()
    ]
)

class TestReverseCsvExtraction(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Step 1: Create test directory structure
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_dir = os.path.join(self.root_dir, "test_output")
        self.output_dir = os.path.join(self.test_dir, "reverse")
        
        # Step 2: Clean and create directories
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        os.makedirs(self.output_dir)
        
        logging.info(f"Test environment setup complete - Test dir: {self.test_dir}")

    def create_test_excel(self, data: list) -> str:
        """Create a test Excel file with given data"""
        # Step 1: Create DataFrame
        df = pd.DataFrame(data, columns=["Path", "Metrics", "Code"])
        excel_path = os.path.join(self.test_dir, "test.xlsx")
        
        # Step 2: Write to Excel
        df.to_excel(excel_path, index=False)
        return excel_path

    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        logging.info("Test environment cleaned up")

    def test_basic_extraction(self):
        """Test basic file extraction from Excel"""
        # Step 1: Create test data
        test_data = [
            ["test.py", "metrics", "def test_function():\n    return True"]
        ]
        excel_path = self.create_test_excel(test_data)
        
        # Step 2: Run extraction
        reverse_csv_extraction(excel_path, self.output_dir)
        
        # Step 3: Verify file created
        expected_file = os.path.join(self.output_dir, "test.py")
        self.assertTrue(os.path.exists(expected_file))
        
        # Step 4: Verify content
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('def test_function', content)
            self.assertIn('return True', content)

    def test_nested_directories(self):
        """Test extraction with nested directory structure"""
        # Step 1: Create test data with nested paths
        test_data = [
            ["folder1/test1.py", "metrics1", "def function1(): pass"],
            ["folder1/folder2/test2.py", "metrics2", "def function2(): pass"]
        ]
        excel_path = self.create_test_excel(test_data)
        
        # Step 2: Run extraction
        reverse_csv_extraction(excel_path, self.output_dir)
        
        # Step 3: Verify directory structure
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "folder1")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "folder1", "folder2")))
        
        # Step 4: Verify files
        expected_files = [
            os.path.join(self.output_dir, "folder1", "test1.py"),
            os.path.join(self.output_dir, "folder1", "folder2", "test2.py")
        ]
        for file_path in expected_files:
            self.assertTrue(os.path.exists(file_path))

    def test_different_file_types(self):
        """Test extraction of different file types"""
        # Step 1: Create test data with different file types
        test_data = [
            ["script.py", "metrics1", "def python_function(): pass"],
            ["style.css", "metrics2", ".class { color: blue; }"],
            ["code.js", "metrics3", "function jsFunction() { return true; }"]
        ]
        excel_path = self.create_test_excel(test_data)
        
        # Step 2: Run extraction
        reverse_csv_extraction(excel_path, self.output_dir)
        
        # Step 3: Verify all files
        expected_files = {
            "script.py": "def python_function",
            "style.css": ".class",
            "code.js": "function jsFunction"
        }
        
        for filename, expected_content in expected_files.items():
            file_path = os.path.join(self.output_dir, filename)
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn(expected_content, content)

    def test_empty_excel(self):
        """Test handling of empty Excel file"""
        # Step 1: Create empty Excel file
        excel_path = self.create_test_excel([])
        
        # Step 2: Run extraction
        reverse_csv_extraction(excel_path, self.output_dir)
        
        # Step 3: Verify no files created
        self.assertEqual(len(os.listdir(self.output_dir)), 0)

    def test_invalid_excel_path(self):
        """Test handling of invalid Excel file path"""
        # Step 1: Test with non-existent file
        with self.assertRaises(Exception):
            reverse_csv_extraction("nonexistent.xlsx", self.output_dir)

    def test_special_characters(self):
        """Test handling of special characters in paths and content"""
        # Step 1: Create test data with special characters
        test_data = [
            ["special_chars!@#.py", "metrics", "def special_function(): pass"],
            ["folder with spaces/test.py", "metrics", "def space_function(): pass"]
        ]
        excel_path = self.create_test_excel(test_data)
        
        # Step 2: Run extraction
        reverse_csv_extraction(excel_path, self.output_dir)
        
        # Step 3: Verify files created
        expected_files = [
            os.path.join(self.output_dir, "special_chars!@#.py"),
            os.path.join(self.output_dir, "folder with spaces", "test.py")
        ]
        
        for file_path in expected_files:
            self.assertTrue(os.path.exists(file_path))

if __name__ == '__main__':
    unittest.main()