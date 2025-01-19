import unittest
import os
import logging
from dataclasses import asdict, fields

# Add parent directory to sys.path to import the module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summerize_extract.Extractorz import CodeBlock

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_code_block.log'),
        logging.StreamHandler()
    ]
)

class TestCodeBlock(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Step 1: Define test data
        self.test_data = {
            'path': './test/file.py',
            'language': 'python',
            'content': 'def test():\n    pass',
            'style': 'unix',
            'update_class': None
        }
        logging.info("Test environment setup complete")

    def test_initialization(self):
        """Test CodeBlock initialization with different parameters"""
        # Step 1: Create with all parameters
        block = CodeBlock(
            path=self.test_data['path'],
            language=self.test_data['language'],
            content=self.test_data['content'],
            style=self.test_data['style'],
            update_class=self.test_data['update_class']
        )
        
        # Step 2: Verify all attributes
        self.assertEqual(block.path, self.test_data['path'])
        self.assertEqual(block.language, self.test_data['language'])
        self.assertEqual(block.content, self.test_data['content'])
        self.assertEqual(block.style, self.test_data['style'])
        self.assertIsNone(block.update_class)

    def test_optional_parameters(self):
        """Test CodeBlock initialization with optional parameters"""
        # Step 1: Create with only required parameters
        block = CodeBlock(
            path=self.test_data['path'],
            language=self.test_data['language'],
            content=self.test_data['content'],
            style=self.test_data['style']
        )
        
        # Step 2: Verify required attributes
        self.assertEqual(block.path, self.test_data['path'])
        self.assertEqual(block.language, self.test_data['language'])
        self.assertEqual(block.content, self.test_data['content'])
        self.assertEqual(block.style, self.test_data['style'])
        
        # Step 3: Verify optional attribute defaults to None
        self.assertIsNone(block.update_class)

    def test_update_class_parameter(self):
        """Test CodeBlock with update_class parameter"""
        # Step 1: Create with update_class parameter
        block = CodeBlock(
            path=self.test_data['path'],
            language=self.test_data['language'],
            content=self.test_data['content'],
            style=self.test_data['style'],
            update_class='TestClass'
        )
        
        # Step 2: Verify update_class is set
        self.assertEqual(block.update_class, 'TestClass')

    def test_dataclass_features(self):
        """Test dataclass-specific features of CodeBlock"""
        # Step 1: Create instance
        block = CodeBlock(**self.test_data)
        
        # Step 2: Test conversion to dictionary
        block_dict = asdict(block)
        self.assertEqual(block_dict['path'], self.test_data['path'])
        self.assertEqual(block_dict['language'], self.test_data['language'])
        
        # Step 3: Test field introspection
        field_names = {f.name for f in fields(CodeBlock)}
        expected_fields = {'path', 'language', 'content', 'style', 'update_class'}
        self.assertEqual(field_names, expected_fields)

    def test_string_representation(self):
        """Test string representation of CodeBlock"""
        # Step 1: Create instance
        block = CodeBlock(**self.test_data)
        
        # Step 2: Get string representation
        str_repr = str(block)
        
        # Step 3: Verify all fields are included in string
        self.assertIn(self.test_data['path'], str_repr)
        self.assertIn(self.test_data['language'], str_repr)
        self.assertIn(self.test_data['style'], str_repr)

    def test_equality_comparison(self):
        """Test equality comparison between CodeBlock instances"""
        # Step 1: Create two identical instances
        block1 = CodeBlock(**self.test_data)
        block2 = CodeBlock(**self.test_data)
        
        # Step 2: Test equality
        self.assertEqual(block1, block2)
        
        # Step 3: Create instance with different data
        different_data = self.test_data.copy()
        different_data['path'] = './different/path.py'
        block3 = CodeBlock(**different_data)
        
        # Step 4: Test inequality
        self.assertNotEqual(block1, block3)

if __name__ == '__main__':
    unittest.main()