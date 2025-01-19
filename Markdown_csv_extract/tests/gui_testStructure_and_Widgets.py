import unittest
import sys
import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _gui_ import (
    App, SidebarFrame, ScrollableTextboxFrame, TabViewFrame,
    CheckboxFrame, EntryRunFrame, RadiobuttonFrame, QuickPasteFrame,
    CustomListWidget, SettingsData, SettingsManager
)

class TestGUIStructure(unittest.TestCase):
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
        
        # Create settings manager
        self.settings_manager = SettingsManager(self.settings_path)
        
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
                'ignored_files': ['test.ignore']
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

    def test_main_window_initialization(self):
        """Test main window initialization and basic properties"""
        # Step 1: Verify window title and geometry
        self.assertEqual(self.window.windowTitle(), "Project Manager")
        self.assertTrue(self.window.width() >= 1200)
        self.assertTrue(self.window.height() >= 800)
        
        # Step 2: Verify central widget
        self.assertIsNotNone(self.window.centralWidget())
        
        # Step 3: Verify main layout
        main_layout = self.window.main_layout
        self.assertEqual(main_layout.columnCount(), 6)
        self.assertEqual(main_layout.rowCount(), 4)

    def test_sidebar_frame(self):
        """Test sidebar frame initialization and components"""
        sidebar = self.window.sidebar_frame
        
        # Step 1: Verify frame properties
        self.assertEqual(sidebar.minimumWidth(), 200)
        
        # Step 2: Check logo/title label
        self.assertTrue(hasattr(sidebar, 'logo_label'))
        self.assertEqual(sidebar.logo_label.text(), "extractor")
        
        # Step 3: Verify appearance mode combo
        self.assertTrue(hasattr(sidebar, 'appearance_mode_combo'))
        self.assertEqual(sidebar.appearance_mode_combo.count(), 3)
        self.assertEqual(sidebar.appearance_mode_combo.currentText(), "Dark")

    def test_tabview_frame(self):
        """Test tab view frame initialization and functionality"""
        tabview = self.window.tabview_frame
        
        # Step 1: Verify frame initialization
        self.assertTrue(hasattr(tabview, 'preset_combo'))
        self.assertTrue(hasattr(tabview, 'file_listbox'))
        
        # Step 2: Test preset combo functionality
        preset_name = "test-preset"
        preset_files = ['test.py']
        tabview.preset_combo.setCurrentText(preset_name)
        tabview.load_preset_files(preset_name)
        
        # Step 3: Verify file list
        self.assertEqual(tabview.file_listbox.count(), len(preset_files))

    def test_checkbox_frame(self):
        """Test checkbox frame initialization and state changes"""
        checkbox_frame = self.window.checkbox_frame
        
        # Step 1: Verify checkboxes exist
        self.assertTrue(hasattr(checkbox_frame, 'checkbox_extract_csv'))
        self.assertTrue(hasattr(checkbox_frame, 'checkbox_extract_markdown'))
        
        # Step 2: Test initial states
        self.assertFalse(checkbox_frame.extract_csv)
        self.assertFalse(checkbox_frame.extract_markdown)
        
        # Step 3: Test state changes
        checkbox_frame.checkbox_extract_csv.setChecked(True)
        self.assertTrue(checkbox_frame.extract_csv)

    def test_entry_run_frame(self):
        """Test entry run frame initialization and components"""
        entry_frame = self.window.entry_run_frame
        
        # Step 1: Verify basic components
        self.assertTrue(hasattr(entry_frame, 'entry_path'))
        self.assertTrue(hasattr(entry_frame, 'run_button'))
        
        # Step 2: Test progress components
        self.assertTrue(hasattr(entry_frame, 'csv_progress'))
        self.assertTrue(hasattr(entry_frame, 'markdown_progress'))
        
        # Step 3: Verify initial states
        self.assertTrue(entry_frame.run_button.isEnabled())
        self.assertFalse(entry_frame.csv_group.isVisible())
        self.assertFalse(entry_frame.markdown_group.isVisible())

    def test_custom_list_widget(self):
        """Test custom list widget functionality"""
        list_widget = CustomListWidget()
        
        # Step 1: Verify signal exists
        self.assertTrue(hasattr(list_widget, 'keyPressed'))
        
        # Step 2: Test key press handling
        test_event = QTest.createKeyEvent(QTest.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        list_widget.keyPressEvent(test_event)

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