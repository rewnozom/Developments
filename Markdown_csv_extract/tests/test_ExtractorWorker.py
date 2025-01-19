import unittest
import os
import shutil
import logging
from PySide6.QtCore import QCoreApplication, QTimer
from unittest.mock import MagicMock

# Add parent directory to sys.path to import the module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summerize_extract.Extractorz import ExtractorWorker, MarkdownEx

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_extractor_worker.log'),
        logging.StreamHandler()
    ]
)

class TestExtractorWorker(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Step 1: Create Qt Application
        self.app = QCoreApplication([])
        
        # Step 2: Create test directory structure
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_dir = os.path.join(self.root_dir, "test_output")
        self.base_dir = os.path.join(self.test_dir, "base")
        self.output_dir = os.path.join(self.test_dir, "output")
        self.settings_path = os.path.join(self.test_dir, "settings.toml")
        
        # Step 3: Clean and create directories
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        os.makedirs(self.base_dir)
        os.makedirs(self.output_dir)
        
        # Step 4: Create test settings file
        self.create_test_settings()
        
        logging.info(f"Test environment setup complete - Test dir: {self.test_dir}")

    def create_test_settings(self):
        """Create a minimal test settings file"""
        settings = {
            'paths': {'path_style': 'windows'},
            'output': {'markdown_file_prefix': 'Test'}
        }
        with open(self.settings_path, 'w') as f:
            f.write(str(settings))

    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.app.quit()
        logging.info("Test environment cleaned up")

    def test_initialization(self):
        """Test ExtractorWorker initialization"""
        # Step 1: Create mock extractor
        mock_extractor = MagicMock()
        
        # Step 2: Create worker
        worker = ExtractorWorker(mock_extractor)
        
        # Step 3: Verify initial state
        self.assertTrue(worker._is_running)
        self.assertEqual(worker.extractor, mock_extractor)

    def test_signal_connections(self):
        """Test signal connections to extractor"""
        # Step 1: Create extractor instance
        extractor = MarkdownEx(self.base_dir, self.output_dir, self.settings_path)
        
        # Step 2: Create worker
        worker = ExtractorWorker(extractor)
        
        # Step 3: Verify signal connections
        self.assertEqual(extractor.update_progress, worker.progress.emit)
        self.assertEqual(extractor.update_status, worker.status.emit)

    def test_run_success(self):
        """Test successful run of worker"""
        # Step 1: Create mock extractor
        mock_extractor = MagicMock()
        
        # Step 2: Create worker
        worker = ExtractorWorker(mock_extractor)
        
        # Step 3: Set up signal tracking
        finished_called = False
        def on_finished():
            nonlocal finished_called
            finished_called = True
        
        worker.finished.connect(on_finished)
        
        # Step 4: Run worker
        worker.run()
        
        # Step 5: Verify extractor was called
        mock_extractor.run.assert_called_once()
        self.assertTrue(finished_called)

    def test_run_error(self):
        """Test worker handling of extractor errors"""
        # Step 1: Create mock extractor that raises an error
        mock_extractor = MagicMock()
        mock_extractor.run.side_effect = Exception("Test error")
        
        # Step 2: Create worker
        worker = ExtractorWorker(mock_extractor)
        
        # Step 3: Set up signal tracking
        error_message = None
        def on_error(msg):
            nonlocal error_message
            error_message = msg
        
        worker.error.connect(on_error)
        
        # Step 4: Run worker
        worker.run()
        
        # Step 5: Verify error handling
        self.assertIsNotNone(error_message)
        self.assertEqual(error_message, "Test error")

    def test_stop_functionality(self):
        """Test stopping the worker"""
        # Step 1: Create mock extractor
        mock_extractor = MagicMock()
        
        # Step 2: Create worker
        worker = ExtractorWorker(mock_extractor)
        
        # Step 3: Stop worker
        worker.stop()
        
        # Step 4: Verify states
        self.assertFalse(worker._is_running)
        mock_extractor.stop.assert_called_once()

    def test_progress_updates(self):
        """Test progress signal emissions"""
        # Step 1: Create mock extractor
        mock_extractor = MagicMock()
        
        # Step 2: Create worker
        worker = ExtractorWorker(mock_extractor)
        
        # Step 3: Track progress updates
        progress_values = []
        worker.progress.connect(lambda v: progress_values.append(v))
        
        # Step 4: Simulate progress updates
        worker.progress.emit(0)
        worker.progress.emit(50)
        worker.progress.emit(100)
        
        # Step 5: Verify progress tracking
        self.assertEqual(progress_values, [0, 50, 100])

    def test_status_updates(self):
        """Test status signal emissions"""
        # Step 1: Create mock extractor
        mock_extractor = MagicMock()
        
        # Step 2: Create worker
        worker = ExtractorWorker(mock_extractor)
        
        # Step 3: Track status updates
        status_messages = []
        worker.status.connect(lambda s: status_messages.append(s))
        
        # Step 4: Simulate status updates
        worker.status.emit("Starting")
        worker.status.emit("In progress")
        worker.status.emit("Complete")
        
        # Step 5: Verify status tracking
        self.assertEqual(status_messages, ["Starting", "In progress", "Complete"])

    def test_sequential_runs(self):
        """Test running worker multiple times"""
        # Step 1: Create mock extractor
        mock_extractor = MagicMock()
        
        # Step 2: Create worker
        worker = ExtractorWorker(mock_extractor)
        
        # Step 3: Run multiple times
        worker.run()
        worker.run()
        worker.run()
        
        # Step 4: Verify multiple runs
        self.assertEqual(mock_extractor.run.call_count, 3)

if __name__ == '__main__':
    unittest.main()