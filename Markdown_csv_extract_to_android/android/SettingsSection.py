# ..\_markdown_csv_extractor\components\SettingsSection.py
# ./_markdown_csv_extractor/components/SettingsSection.py

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
    QFileDialog,
    QDialog
)
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QFont
import os
from pathlib import Path
from .Theme import ThemeColors
from .GUI_Constants_and_Settings import GuiConstants, SettingsManager
from .FileChooserDialog import FileChooserDialog


class SettingsSection(QFrame):
    """Combined Settings section for Paths, Files, and Directories"""

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # -------------------------------
        # Paths Subsection
        # -------------------------------
        paths_label = QLabel("[Paths]")
        paths_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(paths_label)

        # Base Directory
        base_dir_layout = QHBoxLayout()
        self.base_dir_input = QLineEdit()
        self.base_dir_input.setReadOnly(True)
        self.base_dir_input.setPlaceholderText("Select Base Directory")
        self.base_dir_input.setText(
            self.settings_manager.relative_to_absolute(self.settings_manager.get_setting("paths", "base_dir", ""))
        )
        base_dir_button = QPushButton("Browse")
        base_dir_button.clicked.connect(lambda: self.choose_directory("base_dir"))
        base_dir_layout.addWidget(self.base_dir_input)
        base_dir_layout.addWidget(base_dir_button)
        layout.addLayout(base_dir_layout)

        # Output Directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setReadOnly(True)
        self.output_dir_input.setPlaceholderText("Select Output Directory")
        self.output_dir_input.setText(
            self.settings_manager.relative_to_absolute(self.settings_manager.get_setting("paths", "output_dir", ""))
        )
        output_dir_button = QPushButton("Browse")
        output_dir_button.clicked.connect(lambda: self.choose_directory("output_dir"))
        output_dir_layout.addWidget(self.output_dir_input)
        output_dir_layout.addWidget(output_dir_button)
        layout.addLayout(output_dir_layout)

        # -------------------------------
        # Files Subsection
        # -------------------------------
        files_label = QLabel("[Files]")
        files_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(files_label)

        # Ignored Extensions
        ignored_ext_layout = QHBoxLayout()
        self.ignored_extensions_input = QLineEdit(
            ", ".join(self.settings_manager.get_setting("files", "ignored_extensions", []))
        )
        self.ignored_extensions_input.setPlaceholderText("e.g., .exe, .dll")
        self.ignored_extensions_input.textChanged.connect(self.update_ignored_extensions)
        ignored_ext_layout.addWidget(QLabel("Ignored Extensions:"))
        ignored_ext_layout.addWidget(self.ignored_extensions_input)
        layout.addLayout(ignored_ext_layout)

        # Ignored Files
        ignored_files_label = QLabel("Ignored Files:")
        self.ignored_files_list = QListWidget()
        ignored_files = self.settings_manager.get_setting("files", "ignored_files", [])
        self.ignored_files_list.addItems([self.settings_manager.relative_to_absolute(file) for file in ignored_files])
        self.ignored_files_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(ignored_files_label)
        layout.addWidget(self.ignored_files_list)

        # Add File and Folder Buttons
        add_file_button = QPushButton("Add File(s)")
        add_folder_button = QPushButton("Add Folder")
        add_file_button.clicked.connect(self.add_files)
        add_folder_button.clicked.connect(self.add_folder)
        layout.addWidget(add_file_button)
        layout.addWidget(add_folder_button)

        # Remove Ignored Files Button
        remove_ignored_files_button = QPushButton("Remove Selected Ignored File(s)")
        remove_ignored_files_button.clicked.connect(self.remove_selected_ignored_files)
        layout.addWidget(remove_ignored_files_button)

        # -------------------------------
        # Directories Subsection
        # -------------------------------
        directories_label = QLabel("[Directories]")
        directories_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(directories_label)

        # Ignored Directories
        ignored_dirs_label = QLabel("Ignored Directories:")
        self.ignored_dirs_list = QListWidget()
        ignored_dirs = self.settings_manager.get_setting("directories", "ignored_directories", [])
        self.ignored_dirs_list.addItems([self.settings_manager.relative_to_absolute(dir_) for dir_ in ignored_dirs])
        self.ignored_dirs_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(ignored_dirs_label)
        layout.addWidget(self.ignored_dirs_list)

        # Add Directory Button
        add_directory_button = QPushButton("Add Directory")
        add_directory_button.clicked.connect(self.add_directory)
        layout.addWidget(add_directory_button)

        # Remove Ignored Directories Button
        remove_ignored_dirs_button = QPushButton("Remove Selected Ignored Directory(s)")
        remove_ignored_dirs_button.clicked.connect(self.remove_selected_ignored_dirs)
        layout.addWidget(remove_ignored_dirs_button)

    def get_file_chooser_mode(self) -> str:
        """Get the current file chooser mode from the main window."""
        main_window = self.window()  # Get the main window
        return getattr(main_window, 'file_chooser_mode', 'Enhanced')

    def choose_directory(self, dir_type: str):
        """Open directory dialog and save selection."""
        mode = self.get_file_chooser_mode()
        start_path = self.settings_manager.relative_to_absolute(
            self.settings_manager.get_setting("paths", "base_dir", "")
        ) or QDir.homePath()

        directory = ""
        if mode == "Enhanced":
            dialog = FileChooserDialog(
                parent=self,
                start_path=start_path,
                select_multiple=False,
                select_files=False,
                select_folders=True
            )
            dialog.setWindowTitle(f"Select {dir_type.replace('_', ' ').title()} Directory")
            dialog.scroll_action.setChecked(True)
            dialog.on_action_triggered(dialog.scroll_action)
            if dialog.exec() == QDialog.Accepted and dialog.selected_paths:
                directory = dialog.selected_paths[0]
        else:  # Classic mode
            directory = QFileDialog.getExistingDirectory(
                self,
                f"Select {dir_type.replace('_', ' ').title()} Directory",
                start_path
            )

        if directory:
            relative_directory = self.settings_manager.absolute_to_relative(directory)
            self.settings_manager.update_setting("paths", dir_type, relative_directory)
            if dir_type == "base_dir":
                self.base_dir_input.setText(directory)
                output_dir = os.path.join(directory, 'output')
                relative_output_dir = self.settings_manager.absolute_to_relative(output_dir)
                self.settings_manager.update_setting("paths", "output_dir", relative_output_dir)
                self.output_dir_input.setText(output_dir)
            elif dir_type == "output_dir":
                self.output_dir_input.setText(directory)

    def update_ignored_extensions(self):
        extensions = [ext.strip() for ext in self.ignored_extensions_input.text().split(",") if ext.strip()]
        self.settings_manager.update_setting("files", "ignored_extensions", extensions)

    def add_files(self):
        """Add files to ignored files list."""
        mode = self.get_file_chooser_mode()
        start_path = self.settings_manager.relative_to_absolute(
            self.settings_manager.get_setting("paths", "base_dir", "")
        ) or QDir.homePath()

        files = []
        if mode == "Enhanced":
            dialog = FileChooserDialog(
                parent=self,
                start_path=start_path,
                select_multiple=True,
                select_files=True,
                select_folders=False
            )
            dialog.setWindowTitle("Select Files to Ignore")
            dialog.scroll_action.setChecked(True)
            dialog.on_action_triggered(dialog.scroll_action)
            if dialog.exec() == QDialog.Accepted:
                files = dialog.selected_paths
        else:  # Classic mode
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Files to Ignore",
                start_path,
                "All Files (*.*)"
            )

        if files:
            current_items = [self.ignored_files_list.item(i).text() for i in range(self.ignored_files_list.count())]
            for file_path in files:
                relative_path = self.settings_manager.absolute_to_relative(file_path)
                if relative_path not in current_items:
                    self.ignored_files_list.addItem(relative_path)
            self.update_ignored_files()

    def add_folder(self):
        """Add all files from a folder to ignored files list."""
        mode = self.get_file_chooser_mode()
        start_path = self.settings_manager.relative_to_absolute(
            self.settings_manager.get_setting("paths", "base_dir", "")
        ) or QDir.homePath()

        folder = ""
        if mode == "Enhanced":
            dialog = FileChooserDialog(
                parent=self,
                start_path=start_path,
                select_multiple=False,
                select_files=False,
                select_folders=True
            )
            dialog.setWindowTitle("Select Folder to Ignore")
            dialog.scroll_action.setChecked(True)
            dialog.on_action_triggered(dialog.scroll_action)
            if dialog.exec() == QDialog.Accepted and dialog.selected_paths:
                folder = dialog.selected_paths[0]
        else:  # Classic mode
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Folder to Ignore",
                start_path
            )

        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = self.settings_manager.absolute_to_relative(file_path)
                    if relative_path not in [self.ignored_files_list.item(i).text() for i in range(self.ignored_files_list.count())]:
                        self.ignored_files_list.addItem(relative_path)
            self.update_ignored_files()

    def remove_selected_ignored_files(self):
        selected_items = self.ignored_files_list.selectedItems()
        for item in selected_items:
            self.ignored_files_list.takeItem(self.ignored_files_list.row(item))
        self.update_ignored_files()

    def update_ignored_files(self):
        ignored_files = [self.settings_manager.absolute_to_relative(self.ignored_files_list.item(i).text())
                         for i in range(self.ignored_files_list.count())]
        self.settings_manager.update_setting("files", "ignored_files", ignored_files)

    def add_directory(self):
        main_window = self.parent().parent()
        file_chooser_mode = main_window.file_chooser_mode

        if file_chooser_mode == "Enhanced":
            dialog = FileChooserDialog(
                parent=self,
                start_path=os.getcwd(),
                select_multiple=False,
                select_files=False,
                select_folders=True
            )
            dialog.setWindowTitle("Select Directory to Ignore")
            dialog.scroll_action.setChecked(True)
            dialog.on_action_triggered(dialog.scroll_action)
            if dialog.exec() == QDialog.Accepted and dialog.selected_paths:
                directory = dialog.selected_paths[0]
        else:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory to Ignore")

        if directory:
            relative_directory = self.settings_manager.absolute_to_relative(directory)
            if relative_directory not in [self.ignored_dirs_list.item(i).text() for i in range(self.ignored_dirs_list.count())]:
                self.ignored_dirs_list.addItem(relative_directory)
            self.update_ignored_dirs()

    def remove_selected_ignored_dirs(self):
        selected_items = self.ignored_dirs_list.selectedItems()
        for item in selected_items:
            self.ignored_dirs_list.takeItem(self.ignored_dirs_list.row(item))
        self.update_ignored_dirs()

    def update_ignored_dirs(self):
        ignored_dirs = [self.settings_manager.absolute_to_relative(self.ignored_dirs_list.item(i).text())
                        for i in range(self.ignored_dirs_list.count())]
        self.settings_manager.update_setting("directories", "ignored_directories", ignored_dirs)
