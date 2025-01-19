# ..\_markdown_csv_extractor\components\FileSpecificSection.py
# ./_markdown_csv_extractor/components/FileSpecificSection.py

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QMessageBox,
    QInputDialog,
    QComboBox,
    QLineEdit,
    QHBoxLayout,
    QFileDialog,
    QWidget,
    QDialog
)
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QFont
from pathlib import Path
import os
from .Theme import ThemeColors
from .GUI_Constants_and_Settings import SettingsManager, GuiConstants
from .FileChooserDialog import FileChooserDialog




class FileSpecificSection(QFrame):
    """Section for handling file-specific settings and presets."""

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Specific Files Section
        specific_files_label = QLabel("[Specific Files]")
        specific_files_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(specific_files_label)

        specific_files_input_layout = QHBoxLayout()
        self.specific_files_input = QLineEdit()
        self.specific_files_input.setPlaceholderText("Add a specific file...")
        self.add_specific_file_btn = QPushButton("Add")
        self.add_specific_file_btn.clicked.connect(self.add_specific_file)
        specific_files_input_layout.addWidget(self.specific_files_input)
        specific_files_input_layout.addWidget(self.add_specific_file_btn)
        layout.addLayout(specific_files_input_layout)

        self.specific_files_list = QListWidget()
        self.specific_files_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.specific_files_list.setMinimumHeight(200)  # Approx. 8 items
        self.specific_files_list.setMaximumHeight(300)  # Allow flexibility
        specific_files = self.settings_manager.get_setting("file_specific", "specific_files", [])
        self.specific_files_list.addItems(specific_files)
        layout.addWidget(self.specific_files_list)

        remove_specific_file_btn = QPushButton("Remove Selected Specific File(s)")
        remove_specific_file_btn.clicked.connect(self.remove_selected_specific_files)
        layout.addWidget(remove_specific_file_btn)

        # Presets Section
        presets_label = QLabel("[Presets]")
        presets_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(presets_label)

        # Preset Dropdown
        self.preset_dropdown = QComboBox()
        presets = self.settings_manager.get_section("presets", {})
        self.preset_dropdown.addItems(presets.keys())
        self.preset_dropdown.currentTextChanged.connect(self.load_preset_files)
        layout.addWidget(self.preset_dropdown)

        # Preset Buttons
        presets_buttons_layout = QHBoxLayout()
        self.add_preset_btn = QPushButton("Add Preset")
        self.remove_preset_btn = QPushButton("Remove Preset")
        self.add_preset_btn.clicked.connect(self.add_preset)
        self.remove_preset_btn.clicked.connect(self.remove_preset)
        presets_buttons_layout.addWidget(self.add_preset_btn)
        presets_buttons_layout.addWidget(self.remove_preset_btn)
        layout.addLayout(presets_buttons_layout)

        # Preset Files Section
        preset_files_input_layout = QHBoxLayout()
        self.preset_files_input = QLineEdit()
        self.preset_files_input.setPlaceholderText("Add a file to the preset...")
        
        # Skapa en container för knapparna
        button_container = QWidget()
        button_container_layout = QHBoxLayout(button_container)
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        button_container_layout.setSpacing(8)
        
        # Lägg till båda knapparna
        self.add_preset_file_btn = QPushButton("Add File")
        self.add_preset_folder_btn = QPushButton("Add Folder")
        self.add_preset_file_btn.clicked.connect(self.add_preset_file)
        self.add_preset_folder_btn.clicked.connect(self.add_preset_folder)
        
        button_container_layout.addWidget(self.add_preset_file_btn)
        button_container_layout.addWidget(self.add_preset_folder_btn)
        
        preset_files_input_layout.addWidget(self.preset_files_input)
        preset_files_input_layout.addWidget(button_container)
        layout.addLayout(preset_files_input_layout)

        self.preset_files_list = QListWidget()
        self.preset_files_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.preset_files_list.setMinimumHeight(200)  # Approx. 8 items
        self.preset_files_list.setMaximumHeight(300)  # Allow flexibility
        layout.addWidget(self.preset_files_list)

        remove_preset_file_btn = QPushButton("Remove Selected Preset File(s)")
        remove_preset_file_btn.clicked.connect(self.remove_selected_preset_files)
        layout.addWidget(remove_preset_file_btn)

        # Add stretching space
        layout.addStretch()

        # Frame styling
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeColors.PRIMARY};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: {ThemeColors.ACCENT};
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                min-height: {GuiConstants.BUTTON_MIN_HEIGHT}px;
            }}
            QPushButton:hover {{
                background-color: {ThemeColors.ACCENT_HOVER};
            }}
            QLineEdit {{
                background-color: {ThemeColors.SECONDARY};
                border: 1px solid {ThemeColors.BORDER};
                padding: 8px;
                border-radius: 4px;
                min-height: {GuiConstants.BUTTON_MIN_HEIGHT - 16}px;
            }}
            QComboBox {{
                background-color: {ThemeColors.SECONDARY};
                border: 1px solid {ThemeColors.BORDER};
                padding: 8px;
                border-radius: 4px;
                min-height: {GuiConstants.BUTTON_MIN_HEIGHT - 16}px;
            }}
            QListWidget {{
                background-color: {ThemeColors.SECONDARY};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: 4px;
                padding: 4px;
            }}
        """)

    # -------------------------------
    # Specific Files Methods
    # -------------------------------


    def get_file_chooser_mode(self) -> str:
        """Get the current file chooser mode from the main window."""
        main_window = self.window()  # Get the main window
        return getattr(main_window, 'file_chooser_mode', 'Enhanced')

    def choose_file(self, title: str, multiple: bool = False) -> list:
        """Unified method for choosing files based on current mode."""
        mode = self.get_file_chooser_mode()
        start_path = self.settings_manager.relative_to_absolute(
            self.settings_manager.get_setting("paths", "base_dir", "")
        ) or QDir.homePath()

        if mode == "Enhanced":
            dialog = FileChooserDialog(
                parent=self,
                start_path=start_path,
                select_multiple=multiple,
                select_files=True,
                select_folders=False
            )
            dialog.setWindowTitle(title)
            dialog.scroll_action.setChecked(True)
            dialog.on_action_triggered(dialog.scroll_action)
            
            if dialog.exec() == QDialog.Accepted:
                return dialog.selected_paths
        else:  # Classic mode
            if multiple:
                files, _ = QFileDialog.getOpenFileNames(self, title, start_path, "All Files (*.*)")
                return files
            else:
                file, _ = QFileDialog.getOpenFileName(self, title, start_path, "All Files (*.*)")
                return [file] if file else []
        return []

    def choose_folder(self, title: str) -> str:
        """Unified method for choosing folders based on current mode."""
        mode = self.get_file_chooser_mode()
        start_path = self.settings_manager.relative_to_absolute(
            self.settings_manager.get_setting("paths", "base_dir", "")
        ) or QDir.homePath()

        if mode == "Enhanced":
            dialog = FileChooserDialog(
                parent=self,
                start_path=start_path,
                select_multiple=False,
                select_files=False,
                select_folders=True
            )
            dialog.setWindowTitle(title)
            dialog.scroll_action.setChecked(True)
            dialog.on_action_triggered(dialog.scroll_action)
            
            if dialog.exec() == QDialog.Accepted and dialog.selected_paths:
                return dialog.selected_paths[0]
        else:  # Classic mode
            folder = QFileDialog.getExistingDirectory(self, title, start_path)
            return folder
        return ""

    def add_specific_file(self):
        """Add a specific file to the list."""
        file_path = self.specific_files_input.text().strip()
        if not file_path:
            QMessageBox.warning(self, "Input Error", "Please enter a file path.")
            return

        absolute_path = self.settings_manager.relative_to_absolute(file_path)
        if not Path(absolute_path).exists():
            QMessageBox.warning(self, "Path Error", f"The file '{file_path}' does not exist.")
            return

        relative_path = self.settings_manager.absolute_to_relative(absolute_path)
        if relative_path in [self.specific_files_list.item(i).text() for i in range(self.specific_files_list.count())]:
            QMessageBox.information(self, "Duplicate Entry", "This file is already in the list.")
            return

        self.specific_files_list.addItem(relative_path)
        self.settings_manager.update_setting("file_specific", "specific_files", self.get_specific_files())
        self.specific_files_input.clear()

    def add_preset_folder(self):
        """Add all files from a folder to the selected preset."""
        preset_name = self.preset_dropdown.currentText()
        if not preset_name:
            QMessageBox.warning(self, "No Preset Selected", "Please select a preset to add files.")
            return

        folder_path = self.choose_folder("Select Folder to Add to Preset")
        if not folder_path:
            return

        added_files = 0
        skipped_files = 0
        presets = self.settings_manager.get_section("presets", {})
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = self.settings_manager.absolute_to_relative(file_path)
                
                if relative_path not in presets[preset_name]:
                    presets[preset_name].append(relative_path)
                    self.preset_files_list.addItem(relative_path)
                    added_files += 1
                else:
                    skipped_files += 1

        if added_files > 0:
            self.settings_manager.update_setting("presets", preset_name, presets[preset_name])
            QMessageBox.information(
                self,
                "Folder Added",
                f"Added {added_files} files to preset.\nSkipped {skipped_files} duplicate files."
            )
        else:
            QMessageBox.information(
                self,
                "No Files Added",
                f"No new files were added.\nAll {skipped_files} files were already in the preset."
            )

    def remove_selected_specific_files(self):
        """Remove selected specific files from the list."""
        selected_items = self.specific_files_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select file(s) to remove.")
            return

        for item in selected_items:
            self.specific_files_list.takeItem(self.specific_files_list.row(item))

        self.settings_manager.update_setting("file_specific", "specific_files", self.get_specific_files())

    def get_specific_files(self) -> list:
        """Retrieve the list of specific files."""
        return [self.specific_files_list.item(i).text() for i in range(self.specific_files_list.count())]

    # -------------------------------
    # Presets Methods
    # -------------------------------

    def load_preset_files(self, preset_name: str):
        """Load files for the selected preset."""
        if not preset_name:
            self.preset_files_list.clear()
            return

        self.preset_files_list.clear()
        preset_files = self.settings_manager.get_setting("presets", preset_name, [])
        self.preset_files_list.addItems(preset_files)

    def add_preset(self):
        """Add a new preset."""
        preset_name, ok = QInputDialog.getText(self, "New Preset", "Enter Preset Name:")
        if ok and preset_name:
            presets = self.settings_manager.get_section("presets", {})
            if preset_name in presets:
                QMessageBox.warning(self, "Preset Exists", f"A preset named '{preset_name}' already exists.")
                return
            presets[preset_name] = []
            self.settings_manager.update_setting("presets", preset_name, presets[preset_name])
            self.preset_dropdown.addItem(preset_name)
            QMessageBox.information(self, "Success", f"Preset '{preset_name}' has been created.")

    def remove_preset(self):
        """Remove the selected preset."""
        preset_name = self.preset_dropdown.currentText()
        if preset_name:
            confirmation = QMessageBox.question(
                self,
                "Confirm Removal",
                f"Are you sure you want to remove the preset '{preset_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirmation == QMessageBox.Yes:
                presets = self.settings_manager.get_section("presets", {})
                if preset_name in presets:
                    del presets[preset_name]
                    self.settings_manager.remove_setting("presets", preset_name)
                    self.preset_dropdown.removeItem(self.preset_dropdown.findText(preset_name))
                    self.preset_files_list.clear()

    def add_preset_file(self):
        """Add a file to the selected preset."""
        preset_name = self.preset_dropdown.currentText()
        if not preset_name:
            QMessageBox.warning(self, "No Preset Selected", "Please select a preset to add files.")
            return

        files = self.choose_file("Select File to Add to Preset")
        if not files:
            return

        file_path = files[0]  # Take first file since we're only selecting one
        relative_path = self.settings_manager.absolute_to_relative(file_path)
        presets = self.settings_manager.get_section("presets", {})
        
        if relative_path in presets[preset_name]:
            QMessageBox.information(self, "Duplicate Entry", "This file is already in the preset.")
            return
            
        presets[preset_name].append(relative_path)
        self.settings_manager.update_setting("presets", preset_name, presets[preset_name])
        self.preset_files_list.addItem(relative_path)

    def remove_selected_preset_files(self):
        """Remove selected files from the preset's file list."""
        preset_name = self.preset_dropdown.currentText()
        if not preset_name:
            QMessageBox.warning(self, "No Preset Selected", "Please select a preset first.")
            return

        selected_items = self.preset_files_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select file(s) to remove.")
            return

        presets = self.settings_manager.get_section("presets", {})
        for item in selected_items:
            presets[preset_name].remove(item.text())
            self.preset_files_list.takeItem(self.preset_files_list.row(item))

        self.settings_manager.update_setting("presets", preset_name, presets[preset_name])
