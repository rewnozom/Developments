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

from summerize_extract.Extractorz import ReverseMarkdownEx, CodeBlock

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_reverse_markdown.log'),
        logging.StreamHandler()
    ]
)

class TestReverseMarkdownEx(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Step 1: Create test directory structure
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_dir = os.path.join(self.root_dir, "test_output")
        self.output_dir = os.path.join(self.test_dir, "reverse")
        self.settings_path = os.path.join(self.test_dir, "settings.toml")
        
        # Step 2: Clean and create directories
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        os.makedirs(self.output_dir)
        
        # Step 3: Create test settings
        self.create_test_settings()
        
        logging.info(f"Test environment setup complete - Test dir: {self.test_dir}")

    def create_test_settings(self):
        """Create a test settings.toml file"""
        settings = {
            'paths': {
                'path_style': 'windows',
                'output_dir': self.output_dir,
            }
        }
        with open(self.settings_path, 'w') as f:
            toml.dump(settings, f)

    def create_test_markdown(self, content: str) -> str:
        """Create a markdown file with test content"""
        md_path = os.path.join(self.test_dir, "test.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return md_path

    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        logging.info("Test environment cleaned up")

    def test_initialization(self):
        """Test ReverseMarkdownEx initialization"""
        # Step 1: Create instance
        md_path = self.create_test_markdown("")
        extractor = ReverseMarkdownEx(md_path, self.output_dir, self.settings_path)
        
        # Step 2: Verify paths are normalized
        self.assertTrue(isinstance(extractor.output_dir, str))
        self.assertTrue('\\' not in extractor.output_dir)
        
        # Step 3: Verify settings loaded correctly
        self.assertTrue(isinstance(extractor.settings, dict))
        self.assertEqual(extractor.settings['paths']['path_style'], 'windows')
        
        # Step 4: Verify running state
        self.assertTrue(extractor._is_running)

    def test_normalize_path(self):
        """Test path normalization functionality"""
        # Step 1: Create instance
        md_path = self.create_test_markdown("")
        extractor = ReverseMarkdownEx(md_path, self.output_dir, self.settings_path)
        
        # Step 2: Test various path formats
        test_cases = [
            ("file://test.py", "./test.py"),
            ("path:test.py", "./test.py"),
            ("[test.py]", "./test.py"),
            ("test.py", "./test.py"),
        ]
        
        # Step 3: Verify each case
        for input_path, expected in test_cases:
            normalized = extractor._normalize_path(input_path)
            self.assertEqual(normalized, expected)

    def test_detect_language(self):
        """Test programming language detection"""
        # Step 1: Create instance
        md_path = self.create_test_markdown("")
        extractor = ReverseMarkdownEx(md_path, self.output_dir, self.settings_path)
        
        # Step 2: Test various file extensions
        test_cases = [
            ("test.py", "python"),
            ("test.js", "javascript"),
            ("test.cpp", "cpp"),
            ("test.unknown", "text"),
        ]
        
        # Step 3: Verify each case
        for file_path, expected_lang in test_cases:
            detected = extractor._detect_language(file_path)
            self.assertEqual(detected, expected_lang)

    def test_extract_code_blocks(self):
        """Test code block extraction from markdown"""
        # Step 1: Create markdown content
        markdown_content = '''
# File: test1.py
```python
def test1():
    pass
```

## File: test2.py
```python
def test2():
    pass
```
'''
        md_path = self.create_test_markdown(markdown_content)
        
        # Step 2: Create extractor and extract blocks
        extractor = ReverseMarkdownEx(md_path, self.output_dir, self.settings_path)
        blocks = extractor.extract_code_blocks(markdown_content)
        
        # Step 3: Verify extracted blocks
        self.assertEqual(len(blocks), 2)
        self.assertTrue(all(isinstance(block, CodeBlock) for block in blocks))
        self.assertEqual(blocks[0].language, "python")
        self.assertTrue("test1" in blocks[0].content)
        self.assertTrue("test2" in blocks[1].content)

    def test_update_class_in_file(self):
        """Test class update functionality"""
        # Step 1: Create initial file with class
        test_file = os.path.join(self.output_dir, "test_class.py")
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        initial_content = '''
class TestClass:
    def old_method(self):
        pass

class OtherClass:
    def other_method(self):
        pass
'''
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # Step 2: Create extractor
        md_path = self.create_test_markdown("")
        extractor = ReverseMarkdownEx(md_path, self.output_dir, self.settings_path)
        
        # Step 3: Update class
        new_class_content = '''class TestClass:
    def new_method(self):
        return "new"'''
        
        success = extractor.update_class_in_file(test_file, "TestClass", new_class_content)
        
        # Step 4: Verify update
        self.assertTrue(success)
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('new_method', content)
            self.assertNotIn('old_method', content)
            self.assertIn('OtherClass', content)

    def test_run_full_extraction(self):
        """Test full markdown extraction process"""
        # Step 1: Create markdown content
        markdown_content = '''
# File: subfolder/test1.py
```python
def function1():
    return "test1"
```

# File: test2.py
```python
def function2():
    return "test2"
```
'''
        md_path = self.create_test_markdown(markdown_content)
        
        # Step 2: Create extractor and run
        extractor = ReverseMarkdownEx(md_path, self.output_dir, self.settings_path)
        extractor.run()
        
        # Step 3: Verify files created
        expected_files = [
            os.path.join(self.output_dir, "subfolder", "test1.py"),
            os.path.join(self.output_dir, "test2.py")
        ]
        
        for file_path in expected_files:
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('function', content)
                self.assertIn('return', content)

if __name__ == '__main__':
    unittest.main()