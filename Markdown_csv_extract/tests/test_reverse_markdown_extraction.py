import unittest
import os
import shutil
import logging
from pathlib import Path

# Add parent directory to sys.path to import the module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summerize_extract.Extractorz import reverse_markdown_extraction

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_reverse_markdown_extraction.log'),
        logging.StreamHandler()
    ]
)

class TestReverseMarkdownExtraction(unittest.TestCase):
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
        
        logging.info(f"Test environment setup complete - Test dir: {self.test_dir}")

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

    def test_basic_extraction(self):
        """Test basic markdown extraction functionality"""
        # Step 1: Create test markdown content
        markdown_content = '''
# File: test.py
```python
def test_function():
    return "Hello, World!"
```
'''
        md_path = self.create_test_markdown(markdown_content)
        
        # Step 2: Run extraction
        reverse_markdown_extraction(md_path, self.output_dir)
        
        # Step 3: Verify output
        expected_file = os.path.join(self.output_dir, "test.py")
        self.assertTrue(os.path.exists(expected_file))
        
        # Step 4: Check file content
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('def test_function', content)
            self.assertIn('Hello, World!', content)

    def test_multiple_files(self):
        """Test extraction of multiple files from markdown"""
        # Step 1: Create markdown with multiple files
        markdown_content = '''
# File: file1.py
```python
def function1():
    pass
```

# File: subfolder/file2.py
```python
def function2():
    pass
```
'''
        md_path = self.create_test_markdown(markdown_content)
        
        # Step 2: Run extraction
        reverse_markdown_extraction(md_path, self.output_dir)
        
        # Step 3: Verify files created
        expected_files = [
            os.path.join(self.output_dir, "file1.py"),
            os.path.join(self.output_dir, "subfolder", "file2.py")
        ]
        
        for file_path in expected_files:
            self.assertTrue(os.path.exists(file_path))

    def test_with_settings(self):
        """Test extraction with settings file"""
        # Step 1: Create settings file
        with open(self.settings_path, 'w') as f:
            f.write('''
[paths]
path_style = "unix"
''')
        
        # Step 2: Create markdown content
        markdown_content = '''
# File: ./test.py
```python
def unix_style():
    pass
```
'''
        md_path = self.create_test_markdown(markdown_content)
        
        # Step 3: Run extraction with settings
        reverse_markdown_extraction(md_path, self.output_dir, self.settings_path)
        
        # Step 4: Verify file created
        expected_file = os.path.join(self.output_dir, "test.py")
        self.assertTrue(os.path.exists(expected_file))

    def test_invalid_markdown_path(self):
        """Test handling of invalid markdown file path"""
        # Step 1: Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            reverse_markdown_extraction("nonexistent.md", self.output_dir)

    def test_empty_markdown(self):
        """Test handling of empty markdown file"""
        # Step 1: Create empty markdown file
        md_path = self.create_test_markdown("")
        
        # Step 2: Run extraction
        reverse_markdown_extraction(md_path, self.output_dir)
        
        # Step 3: Verify no files created
        self.assertEqual(len(os.listdir(self.output_dir)), 0)

    def test_different_languages(self):
        """Test extraction of different programming languages"""
        # Step 1: Create markdown with multiple languages
        markdown_content = '''
# File: script.py
```python
def python_function():
    pass
```

# File: script.js
```javascript
function jsFunction() {
    return true;
}
```

# File: style.css
```css
.class {
    color: blue;
}
```
'''
        md_path = self.create_test_markdown(markdown_content)
        
        # Step 2: Run extraction
        reverse_markdown_extraction(md_path, self.output_dir)
        
        # Step 3: Verify all files created
        expected_files = {
            "script.py": "def python_function",
            "script.js": "function jsFunction",
            "style.css": ".class"
        }
        
        for filename, expected_content in expected_files.items():
            file_path = os.path.join(self.output_dir, filename)
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn(expected_content, content)

if __name__ == '__main__':
    unittest.main()