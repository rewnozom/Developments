from PySide6.QtWidgets import QFrame, QVBoxLayout, QLineEdit, QPushButton, QLabel, QProgressBar
from PySide6.QtGui import QFont
from .Theme import ThemeColors
from .GUI_Constants_and_Settings import SettingsManager
import os
from PySide6.QtCore import (
    Qt, Signal, QObject, QTimer, QThread, Slot,
    QPoint, QPropertyAnimation, QEasingCurve, QModelIndex, QDir
)
from PySide6.QtGui import (
    QFont, QPalette, QColor, QKeyEvent
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QLineEdit,
    QFileDialog, QMessageBox, QCheckBox, QProgressBar,
    QListWidget, QSizePolicy, QInputDialog, QComboBox, QSplitter, QScrollerProperties, QScroller, QDialog
)

from android.FileChooserDialog import FileChooserDialog

class BottomControls(QFrame):
    run_clicked = Signal()
    
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setup_ui()

    def get_default_path(self):
        """Get the default path based on platform (phone or computer)"""
        # Try phone path first
        phone_path = "/storage/emulated/0"
        computer_path = "A:\\0rginize\\0dev"  # Using raw string to handle backslashes
        
        if os.path.exists(phone_path):
            print(f"Using phone default path: {phone_path}")
            return phone_path
        elif os.path.exists(computer_path):
            print(f"Using computer default path: {computer_path}")
            return computer_path
        else:
            # Fallback to home directory if neither exists
            fallback_path = QDir.homePath()
            print(f"Using fallback path: {fallback_path}")
            return fallback_path

    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Path display
        self.current_path = QLineEdit()
        self.current_path.setReadOnly(True)
        self.current_path.setPlaceholderText("Select working directory...")
        
        # Use saved path or default path
        saved_path = self.settings_manager.get_setting("paths", "base_dir", "")
        if saved_path:
            self.current_path.setText(saved_path)
        
        self.current_path.setCursor(Qt.PointingHandCursor)
        self.current_path.mousePressEvent = lambda event: self.select_directory()
        layout.addWidget(self.current_path)

        # Progress frame
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout(self.progress_frame)

        # CSV Progress
        self.csv_progress_label = QLabel("CSV Progress:")
        self.csv_progress = QProgressBar()
        self.csv_status = QLabel("")
        progress_layout.addWidget(self.csv_progress_label)
        progress_layout.addWidget(self.csv_progress)
        progress_layout.addWidget(self.csv_status)

        # Markdown Progress
        self.markdown_progress_label = QLabel("Markdown Progress:")
        self.markdown_progress = QProgressBar()
        self.markdown_status = QLabel("")
        progress_layout.addWidget(self.markdown_progress_label)
        progress_layout.addWidget(self.markdown_progress)
        progress_layout.addWidget(self.markdown_status)

        self.progress_frame.hide()

        # Run button
        self.run_button = QPushButton("Run")
        self.run_button.setMinimumHeight(48)
        self.run_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.ACCENT};
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {ThemeColors.ACCENT_HOVER};
            }}
        """)
        self.run_button.clicked.connect(self.run_clicked.emit)
        layout.addWidget(self.run_button)

        # Footer
        footer = QLabel("By: Tobias Raanaes | Version 1.0.0")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #A1A1AA;")  # zinc-400
        layout.addWidget(footer)

        # Add widgets to layout
        layout.addWidget(self.progress_frame)

        # Styling
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeColors.SECONDARY};
                border-top: 1px solid {ThemeColors.BORDER};
            }}
        """)

    def get_file_chooser_mode(self) -> str:
        """Get the current file chooser mode from the main window."""
        main_window = self.window()  # Get the main window
        return getattr(main_window, 'file_chooser_mode', 'Enhanced')

    def select_directory(self):
        """Handle directory selection"""
        print("BottomControls: Selecting working directory")  # Debug
        
        directory = self.choose_folder("Select Working Directory")
        
        if directory:
            self.current_path.setText(directory)
            self.settings_manager.update_setting("paths", "base_dir", directory)
            # Auto-set output directory
            output_dir = os.path.join(directory, 'output')
            self.settings_manager.update_setting("paths", "output_dir", output_dir)
            print(f"BottomControls: Working directory set to {directory}")

    def choose_folder(self, title: str) -> str:
        """Unified method for choosing folders based on current mode."""
        mode = self.get_file_chooser_mode()
        start_path = self.get_default_path()

        if mode == "Enhanced":
            dialog = FileChooserDialog(
                parent=self,
                start_path=start_path,
                select_multiple=False,
                select_files=False,
                select_folders=True
            )
            dialog.setWindowTitle(title)
            # Start in select single mode instead of scroll mode
            dialog.select_single_action.setChecked(True)
            dialog.on_action_triggered(dialog.select_single_action)
            
            if dialog.exec() == QDialog.Accepted and dialog.selected_paths:
                return dialog.selected_paths[0]
        else:  # Classic mode
            folder = QFileDialog.getExistingDirectory(
                self,
                title,
                start_path,
                QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog
            )
            return folder
        return ""

    def show_progress(self):
        """Show progress bars"""
        self.progress_frame.show()
        self.run_button.setEnabled(False)
        self.csv_progress.setValue(0)
        self.markdown_progress.setValue(0)
        self.csv_progress_label.show()
        self.csv_progress.show()
        self.csv_status.show()
        self.markdown_progress_label.show()
        self.markdown_progress.show()
        self.markdown_status.show()
        print("BottomControls: Progress bars shown")  # Debug

    def hide_progress(self):
        """Hide progress bars and reset"""
        self.progress_frame.hide()
        self.run_button.setEnabled(True)
        self.csv_progress_label.hide()
        self.csv_progress.hide()
        self.csv_status.hide()
        self.markdown_progress_label.hide()
        self.markdown_progress.hide()
        self.markdown_status.hide()
        print("BottomControls: Progress bars hidden")  # Debug

    def update_progress(self, extraction_type: str, value: int):
        """Update progress bar value"""
        if extraction_type == "CSV":
            self.csv_progress.setValue(value)
            print(f"BottomControls: CSV Progress updated to {value}%")  # Debug
        else:
            self.markdown_progress.setValue(value)
            print(f"BottomControls: Markdown Progress updated to {value}%")  # Debug

    def update_status(self, extraction_type: str, status: str):
        """Update status message"""
        if extraction_type == "CSV":
            self.csv_status.setText(status)
            print(f"BottomControls: CSV Status updated to '{status}'")  # Debug
        else:
            self.markdown_status.setText(status)
            print(f"BottomControls: Markdown Status updated to '{status}'")  # Debug