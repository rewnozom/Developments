
# Test Module for GUI Functionality and Interactions
import unittest
import sys
import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent
from unittest.mock import patch
import PySide6.QtTest as QTest

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _gui_ import (
    App, SidebarFrame, ScrollableTextboxFrame, TabViewFrame,
    CheckboxFrame, EntryRunFrame, RadiobuttonFrame, QuickPasteFrame,
    ExtractionWorker, ExtractionManager
)

class TestGUIFunctional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create QApplication instance for all tests"""
        cls.app = QApplication([])
        
    def setUp(self):
        """Set up test environment"""
        # Create test directory structure
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_output")
        self.settings_path = os.path.join(self.test_dir, "settings.toml")
        
        # Clean and create test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create test settings file
        self.create_test_settings()
        
        # Initialize main window
        self.window = App()

    def create_test_settings(self):
        """Create a minimal test settings file"""
        settings_data = {
            'paths': {
                'base_dir': self.test_dir,
                'output_dir': os.path.join(self.test_dir, 'output'),
                'path_style': 'windows'
            },
            'files': {
                'ignored_extensions': ['.pyc'],
                'ignored_files': ["test.ignore"]
            },
            'directories': {
                'ignored_directories': ['__pycache__']
            },
            'file_specific': {
                'use_file_specific': False,
                'specific_files': []
            },
            'output': {
                'markdown_file_prefix': 'Test_Project',
                'csv_file_prefix': 'Test_Details'
            },
            'metrics': {
                'size_unit': 'KB'
            },
            'presets': {
                'test-preset': ['test.py']
            }
        }
        
        with open(self.settings_path, 'w') as f:
            import toml
            toml.dump(settings_data, f)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.window.close()

    def test_extraction_workflow(self):
        """Test complete extraction workflow"""
        # Step 1: Set up extraction options
        self.window.checkbox_frame.checkbox_extract_csv.setChecked(True)
        self.window.checkbox_frame.checkbox_extract_markdown.setChecked(True)
        
        # Step 2: Set directory path
        self.window.entry_run_frame.entry_path.setText(self.test_dir)
        
        # Step 3: Trigger extraction
        with patch.object(ExtractionWorker, 'run'):
            QTest.mouseClick(self.window.entry_run_frame.run_button, Qt.LeftButton)
            
        # Step 4: Verify progress UI updates
        self.assertTrue(self.window.entry_run_frame.csv_group.isVisible())
        self.assertTrue(self.window.entry_run_frame.markdown_group.isVisible())

    def test_quick_paste_extraction(self):
        """Test quick paste extraction functionality"""
        quick_paste = self.window.quick_paste_frame
        
        # Step 1: Set up test content
        test_content = '''
# test.py
```python
def test():
    pass
```
'''
        quick_paste.text_edit.setText(test_content)
        
        # Step 2: Mock extraction
        with patch.object(ExtractionWorker, 'run'):
            QTest.mouseClick(quick_paste.extract_button, Qt.LeftButton)
        
        # Step 3: Verify progress UI
        self.assertTrue(quick_paste.progress_frame.isVisible())
        self.assertFalse(quick_paste.extract_button.isEnabled())

    def test_preset_management(self):
        """Test preset management functionality"""
        tabview = self.window.tabview_frame
        
        # Step 1: Add new preset
        with patch.object(QFileDialog, 'getOpenFileNames', return_value=([self.mock_file_path], "")):
            preset_name = "test_preset"
            tabview.add_preset()
            tabview.preset_combo.setCurrentText(preset_name)
        
        # Step 2: Add files to preset
        tabview.add_files()
        
        # Step 3: Verify preset content
        self.assertEqual(tabview.file_listbox.count(), 1)
        
        # Step 4: Remove preset
        with patch.object(QFileDialog, 'question', return_value=True):
            tabview.remove_preset()
            self.assertEqual(tabview.file_listbox.count(), 0)

    def test_reverse_extraction(self):
        """Test reverse extraction functionality"""
        radiobutton = self.window.radiobutton_frame
        
        # Step 1: Select files
        radiobutton.open_file_dialog_csv()
        radiobutton.open_file_dialog_markdown()
        
        # Step 2: Mock extraction
        with patch.object(ExtractionWorker, 'run'):
            radiobutton.handle_reverse_csv()
            radiobutton.handle_reverse_markdown()
            
        # Step 3: Verify file list
        self.assertEqual(radiobutton.csv_file_selected.count(), 1)
        self.assertEqual(radiobutton.markdown_file_selected.count(), 1)

    def test_entry_run_frame(self):
        """Test entry run frame initialization and components"""
        entry_run_frame = self.window.entry_run_frame
        
        # Step 1: Verify basic components
        self.assertTrue(hasattr(entry_run_frame, 'entry_path'))
        self.assertTrue(hasattr(entry_run_frame, 'run_button'))
        
        # Step 2: Test progress components
        self.assertTrue(hasattr(entry_run_frame, 'csv_group'))
        self.assertTrue(hasattr(entry_run_frame, 'markdown_group'))
        
        # Step 3: Verify initial states
        self.assertTrue(entry_run_frame.run_button.isEnabled())
        self.assertFalse(entry_run_frame.csv_group.isVisible())
        self.assertFalse(entry_run_frame.markdown_group.isVisible())

    def test_quick_paste_frame(self):
        """Test quick paste frame initialization and components"""
        quick_paste = self.window.quick_paste_frame
        
        # Step 1: Verify frame components
        self.assertTrue(hasattr(quick_paste, 'text_edit'))
        self.assertTrue(hasattr(quick_paste, 'extract_button'))
        self.assertTrue(hasattr(quick_paste, 'clear_button'))
        
        # Step 2: Test text edit functionality
        test_text = "def test():\n    pass"
        quick_paste.text_edit.setText(test_text)
        self.assertEqual(quick_paste.text_edit.toPlainText(), test_text)
        
        # Step 3: Test clear functionality
        quick_paste.clear_text()
        self.assertEqual(quick_paste.text_edit.toPlainText(), "")

    @classmethod
    def tearDownClass(cls):
        """Clean up the QApplication instance"""
        cls.app.quit()


if __name__ == '__main__':
    unittest.main()
