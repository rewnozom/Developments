# ./_phone_markdown_gui_extractor.py

import os
import sys
import toml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import (
    Qt, Signal, QObject, QTimer, QThread, Slot,
    QPoint, QPropertyAnimation, QEasingCurve, QSize
)
from PySide6.QtGui import (
    QFont, QPalette, QColor, QKeyEvent
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QLineEdit,
    QFileDialog, QMessageBox, QCheckBox, QProgressBar,
    QListWidget, QScroller, QScrollerProperties, QSizePolicy,
    QInputDialog, QComboBox, QBoxLayout
)

class CustomListWidget(QListWidget):
    """Custom ListWidget with keyPressed signal for better touch handling"""
    keyPressed = Signal(QKeyEvent)

    def keyPressEvent(self, event: QKeyEvent):
        self.keyPressed.emit(event)
        super().keyPressEvent(event)

class ThemeColors:
    PRIMARY = "#18181B"      # zinc-900
    SECONDARY = "#27272A"    # zinc-800
    ACCENT = "#EF4444"       # red-500
    ACCENT_HOVER = "#DC2626" # red-600
    TEXT = "#FFFFFF"
    BORDER = "#3F3F46"       # zinc-700
    DISABLED = "#52525B"     # zinc-600

    @classmethod
    def set_theme(cls, is_dark: bool):
        if is_dark:
            cls.PRIMARY = "#18181B"      # dark theme
            cls.SECONDARY = "#27272A"
            cls.TEXT = "#FFFFFF"
        else:
            cls.PRIMARY = "#FFFFFF"      # light theme
            cls.SECONDARY = "#F4F4F5"
            cls.TEXT = "#000000"

class AppTheme:
    @staticmethod
    def get_base_stylesheet():
        return f"""
            QWidget {{
                background-color: {ThemeColors.PRIMARY};
                color: {ThemeColors.TEXT};
                font-family: 'Segoe UI', sans-serif;
            }}
            
            QPushButton {{
                background-color: {ThemeColors.ACCENT};
                border: none;
                padding: 12px;
                border-radius: 4px;
                color: {ThemeColors.TEXT};
                font-weight: bold;
                min-height: {GuiConstants.BUTTON_MIN_HEIGHT}px;
            }}
            
            QPushButton:hover {{
                background-color: {ThemeColors.ACCENT_HOVER};
            }}
            
            QPushButton:disabled {{
                background-color: {ThemeColors.DISABLED};
            }}
            
            QLineEdit {{
                background-color: {ThemeColors.SECONDARY};
                border: 1px solid {ThemeColors.BORDER};
                padding: 8px;
                border-radius: 4px;
            }}
            
            QProgressBar {{
                border: none;
                background-color: {ThemeColors.SECONDARY};
                border-radius: 2px;
                height: 8px;
            }}
            
            QProgressBar::chunk {{
                background-color: {ThemeColors.ACCENT};
                border-radius: 2px;
            }}
            
            QScrollArea {{
                border: none;
            }}
            
            QListWidget {{
                background-color: {ThemeColors.SECONDARY};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: 4px;
                padding: 4px;
                min-height: 300px;  /* Höjd för 6-8 items */
                max-height: 400px;  /* Maxhöjd som standard */
                selection-background-color: {ThemeColors.ACCENT};
                selection-color: {ThemeColors.TEXT};
                outline: none;
            }}
            
            QListWidget::item {{
                padding: 8px;
                border-radius: 2px;
                min-height: 24px;
                border: none;
            }}
            
            QListWidget::item:hover {{
                background-color: {ThemeColors.BORDER};
            }}
            
            QListWidget::item:selected {{
                background-color: {ThemeColors.ACCENT};
                color: {ThemeColors.TEXT};
            }}
            
            QCheckBox {{
                spacing: 8px;
                min-height: 24px;
                padding: 4px;
                color: {ThemeColors.TEXT};
            }}
            
            QCheckBox::indicator {{
                width: 24px;
                height: 24px;
                border: 2px solid {ThemeColors.BORDER};
                border-radius: 4px;
                background-color: {ThemeColors.SECONDARY};
            }}
            
            QCheckBox::indicator:unchecked {{
                background-color: {ThemeColors.SECONDARY};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {ThemeColors.ACCENT};
                border-color: {ThemeColors.ACCENT};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjUgNC41TDYgMTJMMi41IDguNSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==);
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {ThemeColors.ACCENT};
            }}
            
            QComboBox {{
                background-color: {ThemeColors.SECONDARY};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: 4px;
                padding: 8px;
                min-height: 48px;
                color: {ThemeColors.TEXT};
            }}
            
            QComboBox:hover {{
                border-color: {ThemeColors.ACCENT};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTIgNEw2IDhMMTAgNCIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
                width: 12px;
                height: 12px;
            }}
            
            QComboBox::down-arrow:disabled {{
                image: none;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {ThemeColors.SECONDARY};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: 4px;
                padding: 4px;
                selection-background-color: {ThemeColors.ACCENT};
                selection-color: {ThemeColors.TEXT};
            }}
            
            QFrame[frameShape="4"] {{  /* HLine */
                background-color: {ThemeColors.BORDER};
                height: 1px;
                margin: 8px 0px;
            }}
            
            QFrame[frameShape="5"] {{  /* VLine */
                background-color: {ThemeColors.BORDER};
                width: 1px;
                margin: 0px 8px;
            }}
            
            QFrame#SectionFrame {{
                background-color: {ThemeColors.SECONDARY};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0px;
            }}
            
            QLabel {{
                background: transparent;
                padding: 4px;
            }}
            
            QLabel[isHeader="true"] {{
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 8px;
            }}
            
            /* Touch-specific scrollbar styling */
            QScrollBar:vertical {{
                background-color: transparent;
                width: {GuiConstants.SCROLL_BAR_WIDTH}px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {ThemeColors.BORDER};
                min-height: 30px;
                border-radius: {GuiConstants.SCROLL_BAR_WIDTH//2}px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """



    @staticmethod
    def apply_theme(app: QApplication):
        app.setStyle("Fusion")
        app.setStyleSheet(AppTheme.get_base_stylesheet())
            
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(ThemeColors.PRIMARY))
        palette.setColor(QPalette.WindowText, QColor(ThemeColors.TEXT))
        palette.setColor(QPalette.Base, QColor(ThemeColors.SECONDARY))
        palette.setColor(QPalette.Text, QColor(ThemeColors.TEXT))
        palette.setColor(QPalette.Button, QColor(ThemeColors.ACCENT))
        palette.setColor(QPalette.ButtonText, QColor(ThemeColors.TEXT))
        palette.setColor(QPalette.Link, QColor(ThemeColors.ACCENT))
        palette.setColor(QPalette.Highlight, QColor(ThemeColors.ACCENT_HOVER))
        palette.setColor(QPalette.HighlightedText, QColor(ThemeColors.TEXT))
        app.setPalette(palette)

class GuiConstants:
    
    SCREEN_RATIO = 0.9
    # Device type configuration
    MOBILE_MODE = True
    
    # Touch scroll settings
    TOUCH_SCROLL = True
    KINETIC_SCROLLING = True
    SMOOTH_SCROLL = True
    
    # Touch-specific dimensions
    BUTTON_MIN_HEIGHT = 48
    SCROLL_BAR_WIDTH = 0
    SPACING = 12
    
    # Scroll behavior
    SCROLL_SPEED = 50
    SCROLL_ANIMATION_DURATION = 300
    MOMENTUM_DURATION = 1000
    
    # Visual feedback
    TOUCH_FEEDBACK = True

    @classmethod
    def get_screen_width(cls):
        """Få aktuell skärmbredd"""
        return QApplication.primaryScreen().availableGeometry().width()
    
    @classmethod
    def get_screen_height(cls):
        """Få aktuell skärmhöjd"""
        return QApplication.primaryScreen().availableGeometry().height()
    
    @classmethod
    def get_component_width(cls):
        """Beräkna komponentbredd baserat på skärm"""
        return int(cls.get_screen_width() * cls.SCREEN_RATIO)



    @classmethod
    def get_scroll_stylesheet(cls) -> str:
        return f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollArea QWidget {{
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                width: {cls.SCROLL_BAR_WIDTH}px;
                background-color: transparent;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: #666666;
                border-radius: {cls.SCROLL_BAR_WIDTH//2}px;
                min-height: 30px;
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """

# -------------------------------------
# Settings Management
# -------------------------------------

@dataclass
class SettingsData:
    """Data class for storing settings with type hints"""
    paths: Dict[str, str]
    files: Dict[str, list]
    directories: Dict[str, list]
    file_specific: Dict[str, Any]
    output: Dict[str, str]
    metrics: Dict[str, str]
    presets: Dict[str, list]

    def __post_init__(self):
        """Validate and set default values for settings"""
        if not isinstance(self.file_specific, dict):
            self.file_specific = {"use_file_specific": False, "specific_files": []}
        if "use_file_specific" not in self.file_specific:
            self.file_specific["use_file_specific"] = False
        if "specific_files" not in self.file_specific:
            self.file_specific["specific_files"] = []

class SettingsManager(QObject):
    """Manages loading, saving, and updating application settings"""
    settings_changed = Signal()

    def __init__(self, settings_path: str):
        super().__init__()
        self._settings_path = Path(settings_path).resolve()
        self._settings: Optional[SettingsData] = None
        self._load_settings()

    def _create_default_settings(self) -> SettingsData:
        """Create a default settings object"""
        return SettingsData(
            paths={"base_dir": "", "output_dir": ""},
            files={
                "ignored_extensions": [".exe", ".dll"],
                "ignored_files": []
            },
            directories={
                "ignored_directories": []
            },
            file_specific={
                "use_file_specific": False,
                "specific_files": []
            },
            output={
                "markdown_file_prefix": "Full_Project",
                "csv_file_prefix": "Detailed_Project"
            },
            metrics={"size_unit": "KB"},
            presets={"preset-1": []}
        )

    def _load_settings(self):
        """Load settings from the TOML file"""
        try:
            if not self._settings_path.exists():
                self._settings = self._create_default_settings()
                self._save_settings()
                return

            with open(self._settings_path, 'r', encoding='utf-8') as f:
                content = f.read().replace('\\', '/')
                data = toml.loads(content)
                
            self._settings = SettingsData(**data)
            self._normalize_paths()

        except Exception as e:
            print(f"Error loading settings: {e}")
            self._settings = self._create_default_settings()
            self._save_settings()

    def _normalize_paths(self) -> None:
        """Normalize all paths in settings"""
        if not self._settings:
            return
            
        def normalize(value: Any) -> Any:
            if isinstance(value, str) and ('/' in value or '\\' in value):
                return str(Path(value).resolve())
            if isinstance(value, list):
                return [normalize(item) for item in value]
            if isinstance(value, dict):
                return {k: normalize(v) for k, v in value.items()}
            return value

        self._settings.paths = normalize(self._settings.paths)

    def _save_settings(self):
        """Save current settings to the TOML file"""
        if not self._settings:
            return

        try:
            settings_dict = {
                field: getattr(self._settings, field)
                for field in self._settings.__annotations__
            }

            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._settings_path, 'w', encoding='utf-8') as f:
                toml.dump(settings_dict, f)

        except Exception as e:
            print(f"Error saving settings: {e}")

    def update_setting(self, section: str, key: str, value: Any) -> None:
        """Update a setting value, create it if missing, and emit change signal"""
        if not self._settings:
            return

        section_dict = getattr(self._settings, section, None)
        if section_dict is None:
            section_dict = {}
            setattr(self._settings, section, section_dict)

        if isinstance(section_dict, dict):
            if key not in section_dict:
                section_dict[key] = value if isinstance(value, list) else [value]
            elif isinstance(section_dict[key], list) and isinstance(value, list):
                section_dict[key].extend(v for v in value if v not in section_dict[key])
            else:
                section_dict[key] = value

            self._save_settings()
            self.settings_changed.emit()

    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Retrieve a specific setting"""
        if not self._settings or not hasattr(self._settings, section):
            return default

        section_dict = getattr(self._settings, section)
        return section_dict.get(key, default)

    def get_section(self, section: str, default: Any = None) -> Any:
        """Get an entire settings section"""
        if not self._settings or not hasattr(self._settings, section):
            return default
        return getattr(self._settings, section)

    def remove_setting(self, section: str, key: str) -> None:
        """Remove a setting key from a section"""
        if not self._settings or not hasattr(self._settings, section):
            return

        section_dict = getattr(self._settings, section)
        if isinstance(section_dict, dict) and key in section_dict:
            del section_dict[key]
            self._save_settings()
            self.settings_changed.emit()

class ExtractionManager(QObject):
    """Manages multiple extraction processes"""
    all_finished = Signal()

    def __init__(self):
        super().__init__()
        self.active_threads = 0

    def thread_finished(self):
        self.active_threads -= 1
        if self.active_threads == 0:
            self.all_finished.emit()

class ExtractionWorker(QObject):
    """Worker class for handling extractions in separate threads"""
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

    @Slot()
    def run(self):
        try:
            extractor = self.extractor_class(
                self.input_path,
                self.output_path,
                self.settings_path
            )
            
            if hasattr(extractor, 'update_progress'):
                extractor.update_progress = self._handle_progress
            if hasattr(extractor, 'update_status'):
                extractor.update_status = self._handle_status

            if self._is_running:
                extractor.run()
                self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def _handle_progress(self, value):
        if self._is_running:
            self.progress.emit(value)

    def _handle_status(self, message):
        if self._is_running:
            self.status.emit(message)

    def stop(self):
        self._is_running = False



# -------------------------------------
# GUI Components
# -------------------------------------





class TouchScrollArea(QScrollArea):
    """ScrollArea optimized for touch interaction"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_touch_scroll()
        # Låt området växa/krympa med innehåll
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        

    def sizeHint(self):
        """Föreslå storlek baserad på innehåll"""
        content = self.widget()
        if content:
            return content.sizeHint()
        return super().sizeHint()
                
    def setup_touch_scroll(self):
        if GuiConstants.TOUCH_SCROLL:
            # Enable touch scrolling
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setWidgetResizable(True)
            
            # Enable kinetic scrolling
            if GuiConstants.KINETIC_SCROLLING:
                QScroller.grabGesture(
                    self.viewport(),
                    QScroller.LeftMouseButtonGesture
                )
                
                # Configure QScrollerProperties
                scroller = QScroller.scroller(self.viewport())
                properties = QScrollerProperties()
                
                # Set scroller properties
                property_values = {
                    QScrollerProperties.DragStartDistance: 0.002,
                    QScrollerProperties.DragVelocitySmoothingFactor: 0.6,
                    QScrollerProperties.MinimumVelocity: 0.0,
                    QScrollerProperties.MaximumVelocity: 0.6,
                    QScrollerProperties.DecelerationFactor: 0.1,
                }
                
                for key, value in property_values.items():
                    properties.setScrollMetric(key, value)
                
                scroller.setScrollerProperties(properties)
                
                # Style for touch scrolling
                self.setStyleSheet(GuiConstants.get_scroll_stylesheet())
        else:
            # Desktop mode
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setWidgetResizable(True)
            
    def wheelEvent(self, event):
        if GuiConstants.SMOOTH_SCROLL:
            delta = event.angleDelta().y()
            scrollBar = self.verticalScrollBar()
            
            # Calculate new position with smooth scrolling
            value = scrollBar.value()
            newValue = value - (delta / 120.0 * GuiConstants.SCROLL_SPEED)
            
            # Create smooth animation
            self.animation = QPropertyAnimation(scrollBar, b"value")
            self.animation.setDuration(GuiConstants.SCROLL_ANIMATION_DURATION)
            self.animation.setStartValue(value)
            self.animation.setEndValue(newValue)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.start()
            
            event.accept()
        else:
            super().wheelEvent(event)

class HeaderWidget(QWidget):
    """Header widget with menu, title and settings buttons"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Menu button
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(32, 32)
        self.menu_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.SECONDARY};
                border-radius: 4px;
                font-size: 18px;
            }}
        """)
        
        # Title
        self.title = QLabel("Extraction Tool")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Settings button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.SECONDARY};
                border-radius: 4px;
                font-size: 18px;
            }}
        """)
        
        layout.addWidget(self.menu_btn)
        layout.addWidget(self.title, 1, Qt.AlignCenter)
        layout.addWidget(self.settings_btn)

class SettingsSection(QFrame):
    """Combined Settings section for Paths, Files, and Directories"""
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Paths Section
        layout.addWidget(self._create_section_label("Paths"))

        # Base Directory
        base_dir_layout = QHBoxLayout()
        self.base_dir_input = QLineEdit(self.settings_manager.get_setting("paths", "base_dir", ""))
        self.base_dir_input.setReadOnly(True)
        self.base_dir_input.setPlaceholderText("Select Base Directory")
        base_dir_button = QPushButton("Browse")
        base_dir_button.clicked.connect(lambda: self.choose_directory("base_dir"))
        base_dir_layout.addWidget(self.base_dir_input)
        base_dir_layout.addWidget(base_dir_button)
        layout.addLayout(base_dir_layout)

        # Output Directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit(self.settings_manager.get_setting("paths", "output_dir", ""))
        self.output_dir_input.setReadOnly(True)
        self.output_dir_input.setPlaceholderText("Select Output Directory")
        output_dir_button = QPushButton("Browse")
        output_dir_button.clicked.connect(lambda: self.choose_directory("output_dir"))
        output_dir_layout.addWidget(self.output_dir_input)
        output_dir_layout.addWidget(output_dir_button)
        layout.addLayout(output_dir_layout)

        # Files Section
        layout.addWidget(self._create_section_label("Files"))

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

        # Ignored Files List
        layout.addWidget(QLabel("Ignored Files:"))
        self.ignored_files_list = QListWidget()
        self.ignored_files_list.setSelectionMode(QListWidget.ExtendedSelection)
        ignored_files = self.settings_manager.get_setting("files", "ignored_files", [])
        self.ignored_files_list.addItems(ignored_files)
        layout.addWidget(self.ignored_files_list)

        # File Control Buttons
        btn_layout = QHBoxLayout()
        add_file_btn = QPushButton("Add File")
        add_folder_btn = QPushButton("Add Folder")
        remove_files_btn = QPushButton("Remove Selected")
        
        add_file_btn.clicked.connect(self.add_files)
        add_folder_btn.clicked.connect(self.add_folder)
        remove_files_btn.clicked.connect(self.remove_selected_files)
        
        btn_layout.addWidget(add_file_btn)
        btn_layout.addWidget(add_folder_btn)
        btn_layout.addWidget(remove_files_btn)
        
        layout.addLayout(btn_layout)

    def _create_section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        return label

    def choose_directory(self, dir_type: str):
        directory = QFileDialog.getExistingDirectory(
            self, 
            f"Select {dir_type.replace('_', ' ').title()} Directory"
        )
        if directory:
            self.settings_manager.update_setting("paths", dir_type, directory)
            if dir_type == "base_dir":
                self.base_dir_input.setText(directory)
                # Auto-set output directory
                output_dir = str(Path(directory) / "output")
                self.settings_manager.update_setting("paths", "output_dir", output_dir)
                self.output_dir_input.setText(output_dir)
            elif dir_type == "output_dir":
                self.output_dir_input.setText(directory)

    def update_ignored_extensions(self):
        extensions = [ext.strip() for ext in self.ignored_extensions_input.text().split(",") if ext.strip()]
        self.settings_manager.update_setting("files", "ignored_extensions", extensions)

    def add_files(self):
        """Add multiple files to ignored files list"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Ignore",
            self.settings_manager.get_setting("paths", "base_dir", ""),
            "All Files (*.*)"
        )
        if files:
            current_items = [self.ignored_files_list.item(i).text() 
                           for i in range(self.ignored_files_list.count())]
            for file_path in files:
                if file_path not in current_items:
                    self.ignored_files_list.addItem(file_path)
            self.update_ignored_files()

    def add_folder(self):
        """Add all files from a folder to ignored files list"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Ignore",
            self.settings_manager.get_setting("paths", "base_dir", "")
        )
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in [self.ignored_files_list.item(i).text() 
                                       for i in range(self.ignored_files_list.count())]:
                        self.ignored_files_list.addItem(file_path)
            self.update_ignored_files()

    def remove_selected_files(self):
        """Remove selected files from ignored files list"""
        selected_items = self.ignored_files_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.ignored_files_list.takeItem(self.ignored_files_list.row(item))
        self.update_ignored_files()

    def update_ignored_files(self):
        """Update the ignored files in settings"""
        ignored_files = [self.ignored_files_list.item(i).text() 
                        for i in range(self.ignored_files_list.count())]
        self.settings_manager.update_setting("files", "ignored_files", ignored_files)



class TouchButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        # Anpassa storlek efter text och skärm
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        # Minimum touch-storlek
        self.setMinimumHeight(GuiConstants.BUTTON_MIN_HEIGHT)
        
    def sizeHint(self):
        """Beräkna lämplig storlek"""
        base_size = super().sizeHint()
        screen_width = GuiConstants.get_screen_width()
        
        # Anpassa bredd efter skärm
        if screen_width < 600:  # Smal skärm
            return QSize(int(screen_width * 0.9), base_size.height())
        return base_size



class FileSpecificSection(QFrame):
    """Section for handling file-specific settings and presets"""
    preset_changed = Signal(str, list)  # preset_name, files

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Header med visuell separator
        header_frame = QFrame()
        header_frame.setObjectName("SectionFrame")
        header_layout = QVBoxLayout(header_frame)
        
        header = QLabel("File Management")
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_layout.addWidget(header)
        layout.addWidget(header_frame)

        # Enable/Disable file specific toggle med egen ram
        toggle_frame = QFrame()
        toggle_frame.setObjectName("SectionFrame")
        toggle_layout = QVBoxLayout(toggle_frame)
        
        self.file_specific_toggle = QCheckBox("Enable File Specific Mode")
        use_file_specific = self.settings_manager.get_setting("file_specific", "use_file_specific", False)
        self.file_specific_toggle.setChecked(use_file_specific)
        toggle_layout.addWidget(self.file_specific_toggle)
        layout.addWidget(toggle_frame)

        # File Specific Files Section med ram
        specific_frame = QFrame()
        specific_frame.setObjectName("SectionFrame")
        specific_layout = QVBoxLayout(specific_frame)
        
        specific_layout.addWidget(QLabel("File Specific Files"))
        self.file_specific_list = CustomListWidget()
        self.file_specific_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_specific_list.setMinimumHeight(300)
        self.file_specific_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        specific_layout.addWidget(self.file_specific_list)
        
        # Återställ sparad storlek om den finns
        saved_height = self.settings_manager.get_setting("ui", "specific_list_height", 300)
        self.file_specific_list.setFixedHeight(saved_height)
        
        specific_files = self.settings_manager.get_setting("file_specific", "specific_files", [])
        self.file_specific_list.addItems(specific_files)

        # File Specific Controls
        fs_btn_layout = QHBoxLayout()
        add_specific_file_btn = QPushButton("Add File")
        add_specific_folder_btn = QPushButton("Add Folder")
        remove_specific_btn = QPushButton("Remove Selected")
        
        add_specific_file_btn.clicked.connect(self.add_specific_files)
        add_specific_folder_btn.clicked.connect(self.add_specific_folder)
        remove_specific_btn.clicked.connect(self.remove_selected_specific_files)
        
        fs_btn_layout.addWidget(add_specific_file_btn)
        fs_btn_layout.addWidget(add_specific_folder_btn)
        fs_btn_layout.addWidget(remove_specific_btn)
        specific_layout.addLayout(fs_btn_layout)
        
        layout.addWidget(specific_frame)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Preset Section med ram
        preset_frame = QFrame()
        preset_frame.setObjectName("SectionFrame")
        preset_layout = QVBoxLayout(preset_frame)
        
        preset_header = QLabel("Presets")
        preset_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        preset_layout.addWidget(preset_header)

        # Preset Selection
        preset_selection = QHBoxLayout()
        self.preset_combo = QComboBox()
        presets = self.settings_manager.get_section("presets", {})
        self.preset_combo.addItems(presets.keys())
        preset_selection.addWidget(QLabel("Select Preset:"))
        preset_selection.addWidget(self.preset_combo)
        preset_layout.addLayout(preset_selection)

        # Preset Files List
        preset_layout.addWidget(QLabel("Preset Files"))
        self.preset_list = CustomListWidget()
        self.preset_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.preset_list.setMinimumHeight(300)
        self.preset_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preset_layout.addWidget(self.preset_list)
        
        # Återställ sparad storlek för preset-listan
        saved_preset_height = self.settings_manager.get_setting("ui", "preset_list_height", 300)
        self.preset_list.setFixedHeight(saved_preset_height)
        
        initial_preset = self.preset_combo.currentText()
        if initial_preset:
            preset_files = self.settings_manager.get_setting("presets", initial_preset, [])
            self.preset_list.addItems(preset_files)

        # Preset File Controls
        preset_file_layout = QHBoxLayout()
        add_preset_file_btn = QPushButton("Add File")
        add_preset_folder_btn = QPushButton("Add Folder")
        remove_preset_file_btn = QPushButton("Remove Selected")
        
        add_preset_file_btn.clicked.connect(self.add_preset_files)
        add_preset_folder_btn.clicked.connect(self.add_preset_folder)
        remove_preset_file_btn.clicked.connect(self.remove_selected_preset_files)
        
        preset_file_layout.addWidget(add_preset_file_btn)
        preset_file_layout.addWidget(add_preset_folder_btn)
        preset_file_layout.addWidget(remove_preset_file_btn)
        preset_layout.addLayout(preset_file_layout)

        # Preset Management
        preset_manage_layout = QHBoxLayout()
        add_preset_btn = QPushButton("Add New Preset")
        remove_preset_btn = QPushButton("Remove Preset")
        
        add_preset_btn.clicked.connect(self.add_preset)
        remove_preset_btn.clicked.connect(self.remove_preset)
        
        preset_manage_layout.addWidget(add_preset_btn)
        preset_manage_layout.addWidget(remove_preset_btn)
        preset_layout.addLayout(preset_manage_layout)
        
        layout.addWidget(preset_frame)

        # Spara storlek när listorna ändras
        self.file_specific_list.resizeEvent = self.handle_specific_list_resize
        self.preset_list.resizeEvent = self.handle_preset_list_resize


    def setup_connections(self):
        self.file_specific_toggle.toggled.connect(self.toggle_file_specific)
        self.preset_combo.currentTextChanged.connect(self.load_preset_files)
        self.file_specific_list.keyPressed.connect(self.handle_file_specific_key_press)
        self.preset_list.keyPressed.connect(self.handle_preset_key_press)

    def toggle_file_specific(self, enabled: bool):
        self.settings_manager.update_setting("file_specific", "use_file_specific", enabled)

    def add_specific_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            self.settings_manager.get_setting("paths", "base_dir", ""),
            "All Files (*.*)"
        )
        if files:
            current_items = [self.file_specific_list.item(i).text() 
                           for i in range(self.file_specific_list.count())]
            for file_path in files:
                relative_path = self._get_relative_path(file_path)
                if relative_path not in current_items:
                    self.file_specific_list.addItem(relative_path)
            self.update_specific_files()

    def add_specific_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            self.settings_manager.get_setting("paths", "base_dir", "")
        )
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = self._get_relative_path(file_path)
                    if relative_path not in [self.file_specific_list.item(i).text() 
                                          for i in range(self.file_specific_list.count())]:
                        self.file_specific_list.addItem(relative_path)
            self.update_specific_files()

    def remove_selected_specific_files(self):
        selected_items = self.file_specific_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.file_specific_list.takeItem(self.file_specific_list.row(item))
        self.update_specific_files()

    def update_specific_files(self):
        specific_files = [self.file_specific_list.item(i).text() 
                         for i in range(self.file_specific_list.count())]
        self.settings_manager.update_setting("file_specific", "specific_files", specific_files)

    def add_preset_files(self):
        preset_name = self.preset_combo.currentText()
        if not preset_name:
            QMessageBox.warning(self, "No Preset Selected", "Please select or create a preset first.")
            return

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            self.settings_manager.get_setting("paths", "base_dir", ""),
            "All Files (*.*)"
        )
        if files:
            self._add_files_to_preset(files)

    def add_preset_folder(self):
        preset_name = self.preset_combo.currentText()
        if not preset_name:
            QMessageBox.warning(self, "No Preset Selected", "Please select or create a preset first.")
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            self.settings_manager.get_setting("paths", "base_dir", "")
        )
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            self._add_files_to_preset(files)

    def _add_files_to_preset(self, files: List[str]):
        preset_name = self.preset_combo.currentText()
        if not preset_name:
            return

        current_items = [self.preset_list.item(i).text() 
                        for i in range(self.preset_list.count())]
        for file_path in files:
            relative_path = self._get_relative_path(file_path)
            if relative_path not in current_items:
                self.preset_list.addItem(relative_path)
        self.update_preset_files()

    def remove_selected_preset_files(self):
        selected_items = self.preset_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.preset_list.takeItem(self.preset_list.row(item))
        self.update_preset_files()

    def update_preset_files(self):
        preset_name = self.preset_combo.currentText()
        if not preset_name:
            return
        
        preset_files = [self.preset_list.item(i).text() 
                       for i in range(self.preset_list.count())]
        self.settings_manager.update_setting("presets", preset_name, preset_files)
        self.preset_changed.emit(preset_name, preset_files)

    def load_preset_files(self, preset_name: str):
        if not preset_name:
            return
            
        self.preset_list.clear()
        preset_files = self.settings_manager.get_setting("presets", preset_name, [])
        self.preset_list.addItems(preset_files)

    def add_preset(self):
        name, ok = QInputDialog.getText(
            self,
            "New Preset",
            "Enter the name for the new preset:"
        )
        if ok and name:
            if name in self.settings_manager.get_section("presets", {}):
                QMessageBox.warning(self, "Warning", "A preset with this name already exists.")
                return
                
            self.settings_manager.update_setting("presets", name, [])
            self.preset_combo.addItem(name)
            self.preset_combo.setCurrentText(name)
            self.preset_list.clear()

    def remove_preset(self):
        preset_name = self.preset_combo.currentText()
        if not preset_name:
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove the preset '{preset_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            self.settings_manager.remove_setting("presets", preset_name)
            self.preset_combo.removeItem(self.preset_combo.findText(preset_name))
            self.preset_list.clear()
            self.preset_changed.emit(preset_name, [])

    def _get_relative_path(self, file_path: str) -> str:
        base_dir = self.settings_manager.get_setting("paths", "base_dir", "")
        return os.path.relpath(file_path, base_dir) if base_dir else file_path

    def handle_specific_list_resize(self, event):
        """Hantera storleksändring av file specific listan"""
        if event.size().height() != event.oldSize().height():
            self.settings_manager.update_setting("ui", "specific_list_height", event.size().height())
        super(CustomListWidget, self.file_specific_list).resizeEvent(event)

    def handle_preset_list_resize(self, event):
        """Hantera storleksändring av preset listan"""
        if event.size().height() != event.oldSize().height():
            self.settings_manager.update_setting("ui", "preset_list_height", event.size().height())
        super(CustomListWidget, self.preset_list).resizeEvent(event)

    def handle_file_specific_key_press(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            self.remove_selected_specific_files()

    def handle_preset_key_press(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            self.remove_selected_preset_files()

class RadiobuttonFrame(QFrame):
    """Frame containing reverse extraction controls"""
    csv_file_selected = Signal(str)
    csv_output_selected = Signal(str)
    markdown_file_selected = Signal(str)
    markdown_output_selected = Signal(str)
    reverse_csv_triggered = Signal()
    reverse_markdown_triggered = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_paths = {}
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Header
        self.header = QLabel("Reverse Extraction")
        self.header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.layout.addWidget(self.header)
        
        # CSV Controls
        csv_section = QFrame()
        csv_layout = QVBoxLayout(csv_section)
        csv_layout.setSpacing(8)
        
        csv_header = QLabel("CSV Extraction")
        csv_header.setFont(QFont("Segoe UI", 11))
        csv_layout.addWidget(csv_header)
        
        self.csv_file_btn = QPushButton("Select CSV File")
        self.csv_output_btn = QPushButton("Select CSV Output Directory")
        self.reverse_csv_btn = QPushButton("Reverse CSV Extraction")
        
        csv_layout.addWidget(self.csv_file_btn)
        csv_layout.addWidget(self.csv_output_btn)
        csv_layout.addWidget(self.reverse_csv_btn)
        
        self.layout.addWidget(csv_section)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {ThemeColors.BORDER};")
        self.layout.addWidget(separator)
        
        # Markdown Controls
        md_section = QFrame()
        md_layout = QVBoxLayout(md_section)
        md_layout.setSpacing(8)
        
        md_header = QLabel("Markdown Extraction")
        md_header.setFont(QFont("Segoe UI", 11))
        md_layout.addWidget(md_header)
        
        self.md_file_btn = QPushButton("Select Markdown File")
        self.md_output_btn = QPushButton("Select Markdown Output Directory")
        self.reverse_md_btn = QPushButton("Reverse Markdown Extraction")
        
        md_layout.addWidget(self.md_file_btn)
        md_layout.addWidget(self.md_output_btn)
        md_layout.addWidget(self.reverse_md_btn)
        
        self.layout.addWidget(md_section)
        
        # Apply mobile-friendly styling
        for btn in [self.csv_file_btn, self.csv_output_btn, self.reverse_csv_btn,
                   self.md_file_btn, self.md_output_btn, self.reverse_md_btn]:
            btn.setMinimumHeight(GuiConstants.BUTTON_MIN_HEIGHT)

    def setup_connections(self):
        self.csv_file_btn.clicked.connect(self.select_csv_file)
        self.csv_output_btn.clicked.connect(self.select_csv_output)
        self.reverse_csv_btn.clicked.connect(self.run_reverse_csv)
        
        self.md_file_btn.clicked.connect(self.select_markdown_file)
        self.md_output_btn.clicked.connect(self.select_markdown_output)
        self.reverse_md_btn.clicked.connect(self.run_reverse_markdown)

    def select_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "Excel Files (*.xlsx)"
        )
        if file_path:
            self.selected_paths['csv_file'] = file_path
            self.csv_file_selected.emit(file_path)
            self.csv_file_btn.setText(os.path.basename(file_path))

    def select_csv_output(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select CSV Output Directory"
        )
        if directory:
            self.selected_paths['csv_output'] = directory
            self.csv_output_selected.emit(directory)
            self.csv_output_btn.setText(f"Output: {os.path.basename(directory)}")

    def select_markdown_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Markdown File",
            "",
            "Markdown Files (*.md)"
        )
        if file_path:
            self.selected_paths['markdown_file'] = file_path
            self.markdown_file_selected.emit(file_path)
            self.md_file_btn.setText(os.path.basename(file_path))

    def select_markdown_output(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Markdown Output Directory"
        )
        if directory:
            self.selected_paths['markdown_output'] = directory
            self.markdown_output_selected.emit(directory)
            self.md_output_btn.setText(f"Output: {os.path.basename(directory)}")

    def run_reverse_csv(self):
        if 'csv_file' not in self.selected_paths or 'csv_output' not in self.selected_paths:
            QMessageBox.warning(
                self,
                "Missing Selection",
                "Please select both a CSV file and an output directory."
            )
            return
        
        self.reverse_csv_triggered.emit()

    def run_reverse_markdown(self):
        if 'markdown_file' not in self.selected_paths or 'markdown_output' not in self.selected_paths:
            QMessageBox.warning(
                self,
                "Missing Selection",
                "Please select both a Markdown file and an output directory."
            )
            return
        
        self.reverse_markdown_triggered.emit()

    def get_selected_paths(self) -> dict:
        return self.selected_paths.copy()

    def clear_selections(self):
        self.selected_paths.clear()
        self.csv_file_btn.setText("Select CSV File")
        self.csv_output_btn.setText("Select CSV Output Directory")
        self.md_file_btn.setText("Select Markdown File")
        self.md_output_btn.setText("Select Markdown Output Directory")

class CheckboxFrame(QFrame):
    """Frame containing extraction checkboxes"""
    extract_csv_changed = Signal(bool)
    extract_markdown_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # CSV Checkbox
        self.checkbox_extract_csv = QCheckBox("Extract - CSV")
        self.checkbox_extract_csv.setFont(QFont("Segoe UI", 10))
        self.layout.addWidget(self.checkbox_extract_csv)
        
        # Markdown Checkbox
        self.checkbox_extract_markdown = QCheckBox("Extract - Markdown")
        self.checkbox_extract_markdown.setFont(QFont("Segoe UI", 10))
        self.layout.addWidget(self.checkbox_extract_markdown)
        
        self.layout.addStretch()

        # Mobile-friendly styling adjustments
        for checkbox in [self.checkbox_extract_csv, self.checkbox_extract_markdown]:
            checkbox.setMinimumHeight(GuiConstants.BUTTON_MIN_HEIGHT)

    def setup_connections(self):
        self.checkbox_extract_csv.stateChanged.connect(
            lambda state: self.extract_csv_changed.emit(bool(state))
        )
        self.checkbox_extract_markdown.stateChanged.connect(
            lambda state: self.extract_markdown_changed.emit(bool(state))
        )

    @property
    def extract_csv(self) -> bool:
        return self.checkbox_extract_csv.isChecked()
        
    @property
    def extract_markdown(self) -> bool:
        return self.checkbox_extract_markdown.isChecked()

class EntryRunFrame(QFrame):
    """Frame containing path entry and run button"""
    run_triggered = Signal()
    extraction_progress = Signal(str, int)  # type, progress value
    extraction_status = Signal(str, str)    # type, status message
    
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setup_ui()
        self.setup_connections()
        self.active_workers = {}
        
        # Set initial directory to base_dir from settings
        base_dir = self.settings_manager.get_setting("paths", "base_dir", "")
        if base_dir:
            self.current_path.setText(base_dir)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Path display/selection
        self.current_path = QLineEdit()
        self.current_path.setReadOnly(True)
        self.current_path.setPlaceholderText("Select working directory...")
        self.current_path.setCursor(Qt.PointingHandCursor)
        self.current_path.setMinimumHeight(GuiConstants.BUTTON_MIN_HEIGHT)
        layout.addWidget(self.current_path)

        # Progress frame
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setSpacing(8)

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
        layout.addWidget(self.progress_frame)

        # Run button
        self.run_button = QPushButton("Run")
        self.run_button.setMinimumHeight(GuiConstants.BUTTON_MIN_HEIGHT)
        self.run_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(self.run_button)

        # Footer
        footer = QLabel("By: Tobias Raanaes | Version 1.0.0")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {ThemeColors.DISABLED};")
        layout.addWidget(footer)

    def setup_connections(self):
        self.current_path.mousePressEvent = self.select_directory
        self.run_button.clicked.connect(self.run_extractions)

    def select_directory(self, event):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Working Directory",
            self.current_path.text()
        )
        if directory:
            self.current_path.setText(directory)
            self.settings_manager.update_setting("paths", "base_dir", directory)

            # Auto-set output directory
            output_dir = str(Path(directory) / "output")
            self.settings_manager.update_setting("paths", "output_dir", output_dir)

    def run_extractions(self):
        """Start the extraction process"""
        if not self.current_path.text():
            QMessageBox.warning(self, "No Directory Selected", "Please select a working directory first.")
            return

        try:
            from backends.Extractorz import CSVEx, MarkdownEx
        except ImportError as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import extractors: {str(e)}")
            return

        selected_path = self.current_path.text()
        output_path = os.path.join(selected_path, 'output')

        # Access the main window to get the checkbox_frame
        main_window = self.window()
        if not hasattr(main_window, 'checkbox_frame'):
            QMessageBox.critical(self, "Error", "Checkbox frame not found.")
            return

        checkbox_frame = main_window.checkbox_frame
        extraction_started = False

        # Initialize ExtractionManager
        self.extraction_manager = ExtractionManager()
        self.extraction_manager.all_finished.connect(self.on_all_extractions_finished)

        # Show progress frame and prepare UI
        self.show_progress()

        # Start CSV extraction if selected
        if checkbox_frame.extract_csv:
            thread = QThread()
            worker = ExtractionWorker(CSVEx, selected_path, output_path, main_window.settings_path)
            worker.moveToThread(thread)
            self.setup_worker_connections(worker, thread, "CSV")
            thread.started.connect(worker.run)
            thread.start()
            self.active_workers["CSV"] = (worker, thread)
            extraction_started = True

        # Start Markdown extraction if selected
        if checkbox_frame.extract_markdown:
            thread = QThread()
            worker = ExtractionWorker(MarkdownEx, selected_path, output_path, main_window.settings_path)
            worker.moveToThread(thread)
            self.setup_worker_connections(worker, thread, "Markdown")
            thread.started.connect(worker.run)
            thread.start()
            self.active_workers["Markdown"] = (worker, thread)
            extraction_started = True

        if not extraction_started:
            self.hide_progress()
            QMessageBox.warning(self, "No Selection", "Please select at least one extraction type.")

    def setup_worker_connections(self, worker, thread, worker_type):
        worker.progress.connect(lambda v: self.update_progress(worker_type, v))
        worker.status.connect(lambda s: self.update_status(worker_type, s))
        worker.finished.connect(lambda: self.handle_extraction_finished(worker_type))
        worker.error.connect(lambda e: self.handle_extraction_error(worker_type, e))
        
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)

    def update_progress(self, extraction_type, value):
        if extraction_type == "CSV":
            self.csv_progress.setValue(value)
        else:
            self.markdown_progress.setValue(value)

    def update_status(self, extraction_type, message):
        if extraction_type == "CSV":
            self.csv_status.setText(message)
        else:
            self.markdown_status.setText(message)

    def show_progress(self):
        """Show progress bars and prepare for extraction"""
        self.progress_frame.show()
        self.run_button.setEnabled(False)
        self.csv_progress.setValue(0)
        self.markdown_progress.setValue(0)
        self.csv_status.setText("")
        self.markdown_status.setText("")

    def hide_progress(self):
        """Hide progress bars and reset UI"""
        self.progress_frame.hide()
        self.run_button.setEnabled(True)

    def handle_extraction_finished(self, extraction_type):
        if extraction_type in self.active_workers:
            del self.active_workers[extraction_type]
            
        if not self.active_workers:
            self.hide_progress()
            QMessageBox.information(
                self,
                "Success",
                "All extractions completed successfully."
            )
            self.run_triggered.emit()

    def handle_extraction_error(self, extraction_type, error_message):
        QMessageBox.critical(
            self,
            f"{extraction_type} Extraction Error",
            f"Error during {extraction_type} extraction:\n{error_message}"
        )
        
        if extraction_type in self.active_workers:
            worker, thread = self.active_workers.pop(extraction_type)
            worker.stop()
            thread.quit()
            
        if not self.active_workers:
            self.hide_progress()

    def on_all_extractions_finished(self):
        self.hide_progress()
        QMessageBox.information(
            self,
            "Extraction Complete",
            "All extraction processes have completed successfully."
        )
        self.run_triggered.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_path = "./settings/settings.toml"


        # Ta bort fast storlek
        # window.resize(450, 640) # Ta bort denna
        
        # Använd skärmens storlek istället
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(screen.width(), screen.height())
        
        # Sätt minimum storlek för komponenter istället för fixed
        self.setMinimumWidth(360) # Minimum bredd för mobil
        
        # Lyssna på orientationsändringar
        screen = QApplication.primaryScreen()
        screen.orientationChanged.connect(self.handle_orientation_change)


        # Ensure settings directory exists
        Path(self.settings_path).parent.mkdir(parents=True, exist_ok=True)

        self.settings_manager = SettingsManager(self.settings_path)
        self.active_extractions = {}
        
        # Create component instances
        self.settings_section = SettingsSection(self.settings_manager)
        self.file_specific_section = FileSpecificSection(self.settings_manager)
        self.radiobutton_frame = RadiobuttonFrame()
        self.checkbox_frame = CheckboxFrame()
        
        # Setup UI and connections
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("Mobile Extraction Tool")
        self.setMinimumWidth(360)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add header
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)

        # Create scroll area for content
        scroll_area = TouchScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(GuiConstants.SPACING, GuiConstants.SPACING,
                                       GuiConstants.SPACING, GuiConstants.SPACING)
        scroll_layout.setSpacing(GuiConstants.SPACING)

        # Add main components with frames and separators
        # Settings Section
        settings_frame = QFrame()
        settings_frame.setObjectName("SectionFrame")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.addWidget(self.settings_section)
        scroll_layout.addWidget(settings_frame)

        scroll_layout.addWidget(self._create_separator())

        # File Specific Section
        file_specific_frame = QFrame()
        file_specific_frame.setObjectName("SectionFrame")
        file_specific_layout = QVBoxLayout(file_specific_frame)
        file_specific_layout.addWidget(self.file_specific_section)
        scroll_layout.addWidget(file_specific_frame)

        scroll_layout.addWidget(self._create_separator())

        # Radio Button Section
        radio_frame = QFrame()
        radio_frame.setObjectName("SectionFrame")
        radio_layout = QVBoxLayout(radio_frame)
        radio_layout.addWidget(self.radiobutton_frame)
        scroll_layout.addWidget(radio_frame)

        scroll_layout.addWidget(self._create_separator())

        # Checkbox Section
        checkbox_frame = QFrame()
        checkbox_frame.setObjectName("SectionFrame")
        checkbox_layout = QVBoxLayout(checkbox_frame)
        checkbox_layout.addWidget(self.checkbox_frame)
        scroll_layout.addWidget(checkbox_frame)

        # Add stretch to fill space
        scroll_layout.addStretch()

        # Set scroll area content
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, stretch=1)

        # Add EntryRunFrame at the bottom
        self.entry_run_frame = EntryRunFrame(self.settings_manager)
        main_layout.addWidget(self.entry_run_frame, stretch=0)


    def setup_connections(self):
        # Connect file specific section signals
        self.file_specific_section.preset_changed.connect(self.handle_preset_change)
        
        # Connect reverse extraction signals
        self.radiobutton_frame.reverse_csv_triggered.connect(self.handle_reverse_csv)
        self.radiobutton_frame.reverse_markdown_triggered.connect(self.handle_reverse_markdown)
        
        # Connect extraction checkbox signals
        self.checkbox_frame.extract_csv_changed.connect(self.handle_extract_csv_changed)
        self.checkbox_frame.extract_markdown_changed.connect(self.handle_extract_markdown_changed)
        
        # Connect run frame signals
        self.entry_run_frame.run_triggered.connect(self.handle_run_triggered)

    def handle_orientation_change(self, orientation):
        """Hantera när enheten roteras"""
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(screen.width(), screen.height())
        # Uppdatera layout vid behov
        self.update_layout_for_size(screen.width(), screen.height())
        
    def update_layout_for_size(self, width, height):
        """Uppdatera layout baserat på storlek"""
        is_portrait = height > width
        
        # Exempel på layout-justeringar
        if is_portrait:
            # Vertikal layout
            self.main_layout.setDirection(QBoxLayout.TopToBottom)
        else:
            # Horisontell layout för landscape
            self.main_layout.setDirection(QBoxLayout.LeftToRight)

    def handle_preset_change(self, preset_name: str, files: list):
        print(f"Preset changed: {preset_name} with {len(files)} files")

    def handle_reverse_csv(self):
        paths = self.radiobutton_frame.get_selected_paths()
        print(f"Reverse CSV extraction with paths: {paths}")

    def handle_reverse_markdown(self):
        paths = self.radiobutton_frame.get_selected_paths()
        print(f"Reverse Markdown extraction with paths: {paths}")

    def handle_extract_csv_changed(self, enabled: bool):
        self.settings_manager.update_setting("extractions", "extract_csv", enabled)

    def handle_extract_markdown_changed(self, enabled: bool):
        self.settings_manager.update_setting("extractions", "extract_markdown", enabled)

    def handle_run_triggered(self):
        print("Run process completed")

    def _create_separator(self) -> QFrame:
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        return separator

    def closeEvent(self, event):
        self.settings_manager._save_settings()
        event.accept()

class SectionBase(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SectionFrame")
        self.setContentsMargins(12, 12, 12, 12)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Apply theme
    AppTheme.apply_theme(app)
    
    # Create and show main window
    window = MainWindow()
    #window.resize(450, 640)  # Mobile-first dimensions
    window.show()
    
    sys.exit(app.exec())

