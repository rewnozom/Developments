from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QTreeView,
    QFileSystemModel,
    QToolBar,
    QHBoxLayout,
    QAbstractItemView,
    QScroller,
    QScrollerProperties
)
from PySide6.QtCore import (
    Qt,
    QDir
)
from PySide6.QtGui import QAction
import os

class FileChooserDialog(QDialog):
    def __init__(self, parent=None, start_path=None, select_multiple=False, select_files=True, select_folders=False):
        super().__init__(parent)
        self.start_path = start_path or os.getcwd()
        self.select_multiple = select_multiple
        self.select_files = select_files
        self.select_folders = select_folders
        self.selected_paths = []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Select Files")
        self.setMinimumSize(400, 600)
        self.layout = QVBoxLayout(self)

        # Toolbar with toggles
        self.toolbar = QToolBar()
        self.scroll_action = QAction("Scroll", self)
        self.select_single_action = QAction("Select Single", self)
        self.select_multiple_action = QAction("Select Multiple", self)

        self.scroll_action.setCheckable(True)
        self.select_single_action.setCheckable(True)
        self.select_multiple_action.setCheckable(True)

        # By default, set scroll mode
        self.scroll_action.setChecked(True)

        self.toolbar.addAction(self.scroll_action)
        self.toolbar.addAction(self.select_single_action)
        self.toolbar.addAction(self.select_multiple_action)

        self.toolbar.actionTriggered.connect(self.on_action_triggered)

        self.layout.addWidget(self.toolbar)

        # File system model
        self.model = QFileSystemModel()
        self.model.setRootPath(self.start_path)
        # Set filters
        filters = QDir.NoDotAndDotDot  # Start with this flag
        if self.select_files:
            filters |= QDir.Files
        if self.select_folders:
            filters |= QDir.Dirs
        self.model.setFilter(filters)

        # Tree view to display files and directories
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.start_path))
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setColumnHidden(1, True)  # Hide Size column
        self.tree_view.setColumnHidden(2, True)  # Hide Type column
        self.tree_view.setColumnHidden(3, True)  # Hide Date Modified column
        self.tree_view.setHeaderHidden(True)

        # Enable touch scrolling
        self.tree_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tree_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        QScroller.grabGesture(
            self.tree_view.viewport(),
            QScroller.LeftMouseButtonGesture
        )

        scroller = QScroller.scroller(self.tree_view.viewport())
        properties = QScrollerProperties()
        scroller.setScrollerProperties(properties)

        # Initially, in scroll mode, disable selection
        self.tree_view.setSelectionMode(QAbstractItemView.NoSelection)
        self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.layout.addWidget(self.tree_view)

        # Buttons
        self.button_box = QHBoxLayout()
        self.choose_button = QPushButton("Choose")  # Changed from "OK" to "Choose"
        self.cancel_button = QPushButton("Cancel")
        self.choose_button.clicked.connect(self.on_accept)
        self.cancel_button.clicked.connect(self.reject)

        self.button_box.addWidget(self.choose_button)
        self.button_box.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_box)

        # Connect signals
        self.tree_view.doubleClicked.connect(self.on_double_clicked)

    def on_action_triggered(self, action):
        # Uncheck all actions first
        self.scroll_action.setChecked(False)
        self.select_single_action.setChecked(False)
        self.select_multiple_action.setChecked(False)

        action.setChecked(True)

        if action == self.scroll_action:
            # Set scroll mode
            self.tree_view.setSelectionMode(QAbstractItemView.NoSelection)
            self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        elif action == self.select_single_action:
            # Set single selection mode
            self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)
            self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        elif action == self.select_multiple_action:
            # Set multiple selection mode
            self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def on_double_clicked(self, index):
        if self.model.isDir(index):
            self.tree_view.setRootIndex(index)
        elif self.select_single_action.isChecked():
            self.on_accept()

    def on_accept(self):
        self.selected_paths = self.get_selected_paths()
        if not self.selected_paths and self.select_folders:
            # If no specific selection, use current directory
            current_path = self.model.filePath(self.tree_view.rootIndex())
            self.selected_paths = [current_path]
        self.accept()

    def get_selected_paths(self):
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        selected_paths = []
        
        if not selected_indexes and self.select_folders:
            # If no selection and we're selecting folders, return current directory
            current_path = self.model.filePath(self.tree_view.rootIndex())
            return [current_path]
            
        for index in selected_indexes:
            if index.column() == 0:  # Only consider the name column
                file_path = self.model.filePath(index)
                if self.select_files and not self.model.isDir(index):
                    selected_paths.append(file_path)
                elif self.select_folders and self.model.isDir(index):
                    selected_paths.append(file_path)
        return selected_paths