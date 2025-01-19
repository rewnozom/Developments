# ./__phone_extr_v_01.py

import os
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QObject, QThread, Slot, QTimer
from PySide6.QtGui import QFont, QPalette, QColor

from android.Theme import ThemeColors, AppTheme
from android.GUI_Constants_and_Settings import SettingsManager
from android.Phone_Touch_and_Scroll import TouchScrollArea
from android.HeaderWidget import HeaderWidget
from android.SettingsSection import SettingsSection
from android.FileSpecificSection import FileSpecificSection
from android.CheckboxFrame import CheckboxFrame
from android.AppearanceSection import AppearanceSection
from android.BottomControls import BottomControls

class ExtractionWorker(QObject):
    finished = Signal()
    error = Signal(str)
    progress = Signal(int)
    status = Signal(str)

    def __init__(self, extractor_class, input_path, output_path, settings_path):
        super().__init__()
        self.extractor_class = extractor_class
        self.input_path = input_path
        self.output_path = output_path
        self.settings_path = settings_path
        self._is_running = True
        self._log("ExtractionWorker: Initialized")

    @Slot()
    def run(self):
        try:
            self._log("ExtractionWorker: run() started")
            extractor = self.initialize_extractor()
            if not extractor:
                return

            self.connect_extractor_signals(extractor)
            if self._is_running:
                extractor.run()
                self._log("ExtractionWorker: Extraction finished successfully")
        except Exception as e:
            error_msg = f"Error in extraction: {str(e)}\n{traceback.format_exc()}"
            self._log(error_msg)
            self.error.emit(error_msg)
        finally:
            # Ensure we always emit finished signal
            if self._is_running:
                self.finished.emit()

    def initialize_extractor(self):
        try:
            extractor = self.extractor_class(
                self.input_path,
                self.output_path,
                self.settings_path
            )
            self._log(f"ExtractionWorker: {self.extractor_class.__name__} initialized")
            return extractor
        except Exception as e:
            self.error.emit(f"Failed to initialize extractor: {str(e)}")
            return None

    def connect_extractor_signals(self, extractor):
        if hasattr(extractor, 'update_progress'):
            extractor.update_progress = self._handle_progress
            self._log("ExtractionWorker: Connected update_progress")
        if hasattr(extractor, 'update_status'):
            extractor.update_status = self._handle_status
            self._log("ExtractionWorker: Connected update_status")

    def _handle_progress(self, value):
        if self._is_running:
            self.progress.emit(value)
            self._log(f"Progress: {value}%")

    def _handle_status(self, message):
        if self._is_running:
            self.status.emit(message)
            self._log(f"Status: {message}")

    def stop(self):
        self._is_running = False
        self._log("ExtractionWorker stopped")

    def _log(self, message):
        print(f"ExtractionWorker: {message}")

class ExtractionManager(QObject):
    all_finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.active_threads = 0

    def increment_active(self):
        self.active_threads += 1

    def decrement_active(self):
        self.active_threads -= 1
        if self.active_threads == 0:
            self.all_finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_path = "./settings/settings.toml"
        Path(self.settings_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.settings_manager = SettingsManager(self.settings_path)
        self.active_extractions = {}
        self.extraction_manager = ExtractionManager()
        
        self.setup_ui()
        QTimer.singleShot(100, self.initialize_components)

    def setup_ui(self):
        self.setWindowTitle("Mobile Extraction Tool")
        self.setMinimumWidth(360)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add header
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)

        # Create scroll area
        scroll_area = TouchScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameStyle(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(12, 12, 12, 12)
        scroll_layout.setSpacing(8)

        # Add sections
        self.settings_section = SettingsSection(self.settings_manager)
        self.checkbox_frame = CheckboxFrame(self.settings_manager)
        self.appearance_section = AppearanceSection(self.settings_manager)
        self.file_specific_section = FileSpecificSection(self.settings_manager)

        sections = [
            self.settings_section,
            self.checkbox_frame,
            self.appearance_section,
            self.file_specific_section
        ]

        for section in sections:
            scroll_layout.addWidget(section)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, stretch=1)

        # Add bottom controls
        self.bottom_controls = BottomControls(self.settings_manager)
        main_layout.addWidget(self.bottom_controls, stretch=0)

        self.connect_signals()

    def initialize_components(self):
        """Initialize components after the main window is shown"""
        current_preset = self.file_specific_section.preset_dropdown.currentText()
        if current_preset:
            self.file_specific_section.load_preset_files(current_preset)

    def connect_signals(self):
        self.appearance_section.dark_mode_toggle.toggled.connect(self.toggle_theme)
        self.appearance_section.scaling_bar.valueChanged.connect(self.update_scaling)
        
        self.checkbox_frame.extract_csv_changed.connect(self.handle_extract_csv_changed)
        self.checkbox_frame.extract_markdown_changed.connect(self.handle_extract_markdown_changed)
        
        self.bottom_controls.run_clicked.connect(self.start_extraction)
        self.extraction_manager.all_finished.connect(self.handle_all_extractions_finished)

    def toggle_theme(self, is_dark: bool):
        ThemeColors.set_theme(is_dark)
        AppTheme.apply_theme(QApplication.instance())

    def update_scaling(self, value: int):
        scaling_factor = value / 100.0
        font = QApplication.instance().font()
        font.setPointSize(max(int(10 * scaling_factor), 8))
        QApplication.instance().setFont(font)

    def handle_extract_csv_changed(self, enabled: bool):
        self.settings_manager.update_setting("extractions", "extract_csv", enabled)

    def handle_extract_markdown_changed(self, enabled: bool):
        self.settings_manager.update_setting("extractions", "extract_markdown", enabled)

    def start_extraction(self):
        if not self.bottom_controls.current_path.text():
            QMessageBox.warning(self, "No Directory Selected", "Please select a working directory first.")
            return

        extract_csv = self.checkbox_frame.checkbox_extract_csv.isChecked()
        extract_markdown = self.checkbox_frame.checkbox_extract_markdown.isChecked()

        if not extract_csv and not extract_markdown:
            QMessageBox.warning(self, "No Extraction Selected", "Please select at least one extraction option.")
            return

        try:
            from backends.Extractorz import CSVEx, MarkdownEx
        except ImportError as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import extractors: {str(e)}")
            return

        self.bottom_controls.show_progress()
        base_dir = self.bottom_controls.current_path.text()
        output_dir = self.settings_manager.get_setting("paths", "output_dir", "")

        if extract_csv:
            self.start_extraction_thread("CSV", CSVEx, base_dir, output_dir)
            self.extraction_manager.increment_active()

        if extract_markdown:
            self.start_extraction_thread("Markdown", MarkdownEx, base_dir, output_dir)
            self.extraction_manager.increment_active()

    def start_extraction_thread(self, extraction_type, extractor_class, input_path, output_path):
        thread = QThread(self)  # Set parent to ensure proper cleanup
        worker = ExtractionWorker(extractor_class, input_path, output_path, self.settings_path)
        
        worker.moveToThread(thread)
        
        # Connect signals in the correct order
        worker.progress.connect(
            lambda v: self.bottom_controls.update_progress(extraction_type, v),
            Qt.QueuedConnection
        )
        worker.status.connect(
            lambda s: self.bottom_controls.update_status(extraction_type, s),
            Qt.QueuedConnection
        )
        worker.error.connect(
            lambda e: self.handle_extraction_error(extraction_type, e),
            Qt.QueuedConnection
        )
        worker.finished.connect(
            lambda: self.handle_extraction_finished(extraction_type),
            Qt.QueuedConnection
        )
        
        # Cleanup connections
        worker.finished.connect(worker.deleteLater, Qt.QueuedConnection)
        worker.finished.connect(thread.quit, Qt.QueuedConnection)
        thread.finished.connect(thread.deleteLater, Qt.QueuedConnection)
        
        # Start the thread
        thread.started.connect(worker.run)
        thread.start()
        
        # Store references
        self.active_extractions[extraction_type] = (worker, thread)

    def handle_extraction_error(self, extraction_type, error_message):
        try:
            QMessageBox.critical(
                self,
                f"{extraction_type} Extraction Error",
                f"An error occurred during {extraction_type} extraction:\n{error_message}"
            )
            
            if extraction_type in self.active_extractions:
                worker, thread = self.active_extractions.pop(extraction_type)
                worker.stop()
                
                # Ensure thread is properly stopped
                thread.quit()
                if not thread.wait(1000):  # Wait up to 1 second
                    thread.terminate()
                
                self.extraction_manager.decrement_active()

            if not self.active_extractions:
                self.bottom_controls.hide_progress()
        except Exception as e:
            print(f"Error in handle_extraction_error: {str(e)}")

    def handle_extraction_finished(self, extraction_type):
        try:
            if extraction_type in self.active_extractions:
                worker, thread = self.active_extractions.pop(extraction_type)
                
                # Ensure thread is properly stopped
                thread.quit()
                if not thread.wait(1000):  # Wait up to 1 second
                    thread.terminate()
                
                self.extraction_manager.decrement_active()
        except Exception as e:
            print(f"Error in handle_extraction_finished: {str(e)}")

    def handle_all_extractions_finished(self):
        try:
            self.bottom_controls.hide_progress()
            QMessageBox.information(
                self,
                "Extraction Complete",
                "All extraction processes have completed successfully."
            )
        except Exception as e:
            print(f"Error in handle_all_extractions_finished: {str(e)}")

    def closeEvent(self, event):
        """Handle application closure"""
        try:
            # Stop all active extractions
            for worker, thread in list(self.active_extractions.values()):
                worker.stop()
                thread.quit()
                if not thread.wait(1000):  # Wait up to 1 second
                    thread.terminate()
            
            # Clear active extractions
            self.active_extractions.clear()
            
            # Save settings
            self.settings_manager._save_settings()
            
            # Accept the close event
            event.accept()
        except Exception as e:
            print(f"Error in closeEvent: {str(e)}")
            event.accept()

def main():
    try:
        app = QApplication(sys.argv)
        
        # Set default font
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        # Apply theme
        AppTheme.apply_theme(app)
        
        # Create and show main window
        window = MainWindow()
        window.resize(360, 640)
        window.show()
        
        # Start event loop
        return app.exec()
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())