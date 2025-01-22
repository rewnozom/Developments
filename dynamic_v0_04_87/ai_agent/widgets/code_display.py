# AI_Agent/widgets/code_display.py

import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QLineEdit, QTextEdit, QMessageBox, QApplication)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)

class CodeDisplayWindow(QWidget):
    def __init__(self, code_block):
        super().__init__()
        self.code_block = code_block
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Code Block")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")

        layout = QVBoxLayout()

        copy_button = QPushButton("Copy Code")
        copy_button.clicked.connect(self.copy_code_to_clipboard)
        layout.addWidget(copy_button)

        file_type_label = QLabel("File Type:")
        layout.addWidget(file_type_label)
        self.file_type_entry = QLineEdit()
        self.file_type_entry.setText(".py")
        layout.addWidget(self.file_type_entry)

        version_label = QLabel("Version:")
        layout.addWidget(version_label)
        self.version_entry = QLineEdit()
        self.version_entry.setText("v1")
        layout.addWidget(self.version_entry)

        save_button = QPushButton("Save Code")
        save_button.clicked.connect(self.save_code)
        layout.addWidget(save_button)

        self.code_text = QTextEdit()
        self.code_text.setPlainText(self.code_block)
        self.code_text.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
        font = QFont("Courier")
        font.setStyleHint(QFont.Monospace)
        self.code_text.setFont(font)
        layout.addWidget(self.code_text)

        self.setLayout(layout)

    def save_code(self):
        try:
            # Add your save logic here
            QMessageBox.information(self, "Saved", "Code block saved successfully!")
            logger.info("Code block saved successfully.")
        except Exception as e:
            logger.error(f"Unexpected error saving code block: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save code block: {e}")

# Utility function to copy text to the clipboard
def copy_to_clipboard(text):
    """Copy text to clipboard."""
    try:
        QApplication.clipboard().setText(text)
        QMessageBox.information(None, "Copied", "Text copied to clipboard!")
        logger.info("Copied text to clipboard.")
    except Exception as e:
        logger.error(f"Unexpected error copying to clipboard: {e}")

# Utility function to show a code display window
def show_code_window(code_block):
    """
    Display a new window showing the code block.
    Args:
        code_block (str): The code block to be displayed in the window.
    """
    try:
        logger.debug(f"Showing code window with code block:\n{code_block}")
        code_window = CodeDisplayWindow(code_block)
        code_window.show()
        logger.info("Code window displayed successfully.")
    except Exception as e:
        logger.error(f"Unexpected error showing code window: {e}")
