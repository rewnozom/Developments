import unittest
import os
import shutil
import logging
import pandas as pd

# Add parent directory to sys.path to import the module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summerize_extract.Extractorz import ReverseCSVEx

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_reverse_csv.log'),
        logging.StreamHandler()
    ]
)

class TestReverseCSVEx(unittest.TestCase):
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

    def test_initialization(self):
        """Test ReverseCSVEx initialization"""
        # Step 1: Create test Excel file
        excel_path = self.create_test_excel([
            ["test.py", "metrics", "def test(): pass"]
        ])
        
        # Step 2: Create instance
        extractor = ReverseCSVEx(excel_path, self.output_dir)
        
        # Step 3: Verify paths are normalized
        self.assertTrue(isinstance(extractor.output_dir, str))
        self.assertTrue('\\' not in extractor.output_dir)
        
        # Step 4: Verify running state
        self.assertTrue(extractor._is_running)

    def test_basic_extraction(self):
        """Test basic file extraction from Excel"""
        # Step 1: Create test data
        test_data = [
            ["test.py", "metrics", "def test_function():\n    return True"]
        ]
        excel_path = self.create_test_excel(test_data)
        
        # Step 2: Create and run extractor
        extractor = ReverseCSVEx(excel_path, self.output_dir)
        extractor.run()
        
        # Step 3: Verify file created
        expected_file = os.path.join(self.output_dir, "test.py")
        self.assertTrue(os.path.exists(expected_file))
        
        # Step 4: Verify content
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('def test_function', content)
            self.assertIn('return True', content)

    def test_multiple_files(self):
        """Test extraction of multiple files"""
        # Step 1: Create test data with multiple files
        test_data = [
            ["file1.py", "metrics1", "def function1(): pass"],
            ["subfolder/file2.py", "metrics2", "def function2(): pass"]
        ]
        excel_path = self.create_test_excel(test_data)
        
        # Step 2: Run extraction
        extractor = ReverseCSVEx(excel_path, self.output_dir)
        extractor.run()
        
        # Step 3: Verify files created
        expected_files = [
            os.path.join(self.output_dir, "file1.py"),
            os.path.join(self.output_dir, "subfolder", "file2.py")
        ]
        
        for file_path in expected_files:
            self.assertTrue(os.path.exists(file_path))

    def test_empty_excel(self):
        """Test handling of empty Excel file"""
        # Step 1: Create empty Excel
        excel_path = self.create_test_excel([])
        
        # Step 2: Run extraction
        extractor = ReverseCSVEx(excel_path, self.output_dir)
        extractor.run()
        
        # Step 3: Verify no files created
        self.assertEqual(len(os.listdir(self.output_dir)), 0)

    def test_invalid_excel_path(self):
        """Test handling of invalid Excel file path"""
        # Step 1: Test with non-existent file
        with self.assertRaises(Exception):
            extractor = ReverseCSVEx("nonexistent.xlsx", self.output_dir)
            extractor.run()

    def test_progress_tracking(self):
        """Test progress tracking functionality"""
        # Step 1: Create test data
        test_data = [
            ["test1.py", "metrics1", "def function1(): pass"],
            ["test2.py", "metrics2", "def function2(): pass"]
        ]
        excel_path = self.create_test_excel(test_data)
        
        # Step 2: Create extractor with progress tracking
        extractor = ReverseCSVEx(excel_path, self.output_dir)
        progress_values = []
        
        def track_progress(value):
            progress_values.append(value)
        
        extractor.update_progress = track_progress
        
        # Step 3: Run extraction
        extractor.run()
        
        # Step 4: Verify progress tracking
        self.assertTrue(len(progress_values) > 0)
        self.assertEqual(progress_values[-1], 100)

    def test_stop_functionality(self):
        """Test stopping the extraction process"""
        # Step 1: Create test data
        test_data = [
            ["test1.py", "metrics1", "def function1(): pass"],
            ["test2.py", "metrics2", "def function2(): pass"]
        ]
        excel_path = self.create_test_excel(test_data)
        
        # Step 2: Create extractor
        extractor = ReverseCSVEx(excel_path, self.output_dir)
        
        # Step 3: Stop before running
        extractor.stop()
        extractor.run()
        
        # Step 4: Verify no files created
        self.assertEqual(len(os.listdir(self.output_dir)), 0)

if __name__ == '__main__':
    unittest.main()