# ..\_markdown_csv_extractor\components\FileChooserModeSection.py
# ./_markdown_csv_extractor/components/FileChooserModeSection.py

# Corrected import statements for FileChooserModeSection.py

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QComboBox
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont


class FileChooserModeSection(QFrame):
    """Section for selecting the file chooser mode."""
    mode_changed = Signal(str)

    def __init__(self, initial_mode: str = "Enhanced", parent=None):
        super().__init__(parent)
        self.current_mode = initial_mode
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header
        header_label = QLabel("File Chooser Mode")
        header_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(header_label)

        # Dropdown for mode selection
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Enhanced", "Classic"])
        self.mode_selector.setCurrentText(self.current_mode)
        self.mode_selector.currentTextChanged.connect(self.on_mode_changed)

        layout.addWidget(self.mode_selector)

    def on_mode_changed(self, mode: str):
        """Handle mode change event."""
        self.current_mode = mode
        self.mode_changed.emit(mode)
        print(f"FileChooserModeSection: File chooser mode changed to {mode}")  # Debug

    def get_current_mode(self) -> str:
        """Return the current file chooser mode."""
        return self.current_mode
