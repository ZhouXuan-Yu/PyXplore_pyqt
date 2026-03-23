# -*- coding: utf-8 -*-
"""
Main Window Module
Implements the main window framework: Navigation + Content Area + Status Bar
"""

import sys
from pathlib import Path

# Add src directory to Python path to import PyXplore library
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QStackedWidget, QStatusBar,
    QMenuBar, QMenu, QAction, QLabel, QToolBar, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont

from .config import COLORS, FONTS, PROJECT_ROOT
from .utils import get_project_logger, import_pyXplore

# Import functional module pages
from .modules.background.background_page import BackgroundPage
from .modules.cif_preprocess.cif_page import CIFPreprocessPage
from .modules.xrd_simulation.simulation_page import XRDSimulationPage
from .modules.xrd_refinement.refinement_page import XRDRefinementPage
from .modules.amorphous.amorphous_page import AmorphousPage
from .modules.xps.xps_page import XPSPage
from .modules.exafs.exafs_page import EXAFSPage
from .modules.batch.batch_page import BatchPage


class MainWindow(QMainWindow):
    """Main Window Class"""

    # Signal: emitted when switching pages
    module_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Logger
        self.logger = get_project_logger("MainWindow")

        # PyXplore library
        self.WPEM = None
        self._init_pyXplore()

        # Current module
        self.current_module = None

        # Initialize UI
        self._init_ui()

        # Connect signals and slots
        self._connect_signals()

        self.logger.info("Main window initialized")

    def _init_pyXplore(self):
        """Initialize PyXplore library"""
        success, result = import_pyXplore()
        if success:
            self.WPEM = result
            self.logger.info("PyXplore library loaded successfully")
        else:
            self.logger.warning(f"Failed to load PyXplore library: {result}")

    def _init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("PyXplore Desktop - X-ray Diffraction Analysis Software")
        self.setGeometry(100, 100, 1400, 900)

        # Set central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #ddd; }")
        main_layout.addWidget(splitter)

        # Create left navigation bar
        nav_widget = self._create_navigation()
        splitter.addWidget(nav_widget)

        # Create right content area
        content_widget = self._create_content_area()
        splitter.addWidget(content_widget)

        # Set split ratio
        splitter.setStretchFactor(0, 250)
        splitter.setStretchFactor(1, 1150)

        # Create menu bar
        self._create_menu_bar()

        # Create status bar
        self._create_status_bar()

        # Create toolbar
        self._create_toolbar()

    def _create_navigation(self):
        """Create left navigation bar"""
        nav_widget = QWidget()
        nav_widget.setMaximumWidth(280)
        nav_widget.setMinimumWidth(200)
        nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['primary']};
            }}
        """)

        layout = QVBoxLayout(nav_widget)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(5)

        # Title
        title_label = QLabel("PyXplore")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white; padding: 10px;")
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("X-ray Diffraction Analysis")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #aaa; padding-left: 10px; margin-bottom: 15px;")
        layout.addWidget(subtitle_label)

        # Navigation tree
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setIndentation(15)
        self.nav_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: transparent;
                border: none;
                color: white;
                font-size: 13px;
            }}
            QTreeWidget::item {{
                padding: 8px 5px;
                border-radius: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: rgba(255, 255, 255, 10);
            }}
            QTreeWidget::item:selected {{
                background-color: {COLORS['secondary']};
            }}
            QTreeWidget::branch {{
                background-color: transparent;
            }}
        """)

        # Create navigation items
        self._create_nav_items()

        layout.addWidget(self.nav_tree)

        # Version info
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(version_label)

        return nav_widget

    def _create_nav_items(self):
        """Create navigation items"""

        # Data Processing Module
        data_item = QTreeWidgetItem(self.nav_tree)
        data_item.setText(0, "Data Processing")
        data_item.setData(0, Qt.UserRole, {"module": "background", "icon": "folder"})

        child_items = [
            {"name": "Background Deduction", "module": "background", "icon": "chart"},
            {"name": "File Conversion", "module": "file_convert", "icon": "file"},
        ]
        for child in child_items:
            child_item = QTreeWidgetItem(data_item)
            child_item.setText(0, f"  {child['icon']} {child['name']}")
            child_item.setData(0, Qt.UserRole, {"module": child['module'], "icon": child['icon']})

        # Structure Analysis Module
        structure_item = QTreeWidgetItem(self.nav_tree)
        structure_item.setText(0, "Structure Analysis")

        structure_children = [
            {"name": "CIF Preprocess", "module": "cif_preprocess", "icon": "doc"},
            {"name": "XRD Simulation", "module": "xrd_simulation", "icon": "graph"},
        ]
        for child in structure_children:
            child_item = QTreeWidgetItem(structure_item)
            child_item.setText(0, f"  {child['icon']} {child['name']}")
            child_item.setData(0, Qt.UserRole, {"module": child['module'], "icon": child['icon']})

        # Refinement Module
        refinement_item = QTreeWidgetItem(self.nav_tree)
        refinement_item.setText(0, "Refinement Analysis")
        refinement_item.setData(0, Qt.UserRole, {"module": "xrd_refinement", "icon": "settings"})

        # Amorphous Module
        amorphous_item = QTreeWidgetItem(self.nav_tree)
        amorphous_item.setText(0, "Amorphous Analysis")

        amorphous_children = [
            {"name": "Amorphous Peak Fitting", "module": "amorphous_fit", "icon": "curve"},
            {"name": "RDF Calculation", "module": "rdf_calc", "icon": "circle"},
        ]
        for child in amorphous_children:
            child_item = QTreeWidgetItem(amorphous_item)
            child_item.setText(0, f"  {child['icon']} {child['name']}")
            child_item.setData(0, Qt.UserRole, {"module": child['module'], "icon": child['icon']})

        # Spectrum Analysis Module
        spectrum_item = QTreeWidgetItem(self.nav_tree)
        spectrum_item.setText(0, "Spectrum Analysis")

        spectrum_children = [
            {"name": "XPS Analysis", "module": "xps", "icon": "flash"},
            {"name": "EXAFS Analysis", "module": "exafs", "icon": "diamond"},
        ]
        for child in spectrum_children:
            child_item = QTreeWidgetItem(spectrum_item)
            child_item.setText(0, f"  {child['icon']} {child['name']}")
            child_item.setData(0, Qt.UserRole, {"module": child['module'], "icon": child['icon']})

        # Batch Processing Module
        batch_item = QTreeWidgetItem(self.nav_tree)
        batch_item.setText(0, "Batch Processing")
        batch_item.setData(0, Qt.UserRole, {"module": "batch", "icon": "stack"})

        # Expand all items
        self.nav_tree.expandAll()

    def _create_content_area(self):
        """Create right content area"""
        content_widget = QWidget()
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Content stacked widget
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack)

        # Create each module page
        self._create_module_pages()

        return content_widget

    def _create_module_pages(self):
        """Create each module page"""

        # Background deduction page
        self.background_page = BackgroundPage(self)
        self.content_stack.addWidget(self.background_page)

        # CIF preprocess page
        self.cif_page = CIFPreprocessPage(self)
        self.content_stack.addWidget(self.cif_page)

        # XRD simulation page
        self.simulation_page = XRDSimulationPage(self)
        self.content_stack.addWidget(self.simulation_page)

        # XRD refinement page
        self.refinement_page = XRDRefinementPage(self)
        self.content_stack.addWidget(self.refinement_page)

        # Amorphous analysis page
        self.amorphous_page = AmorphousPage(self)
        self.content_stack.addWidget(self.amorphous_page)

        # XPS analysis page
        self.xps_page = XPSPage(self)
        self.content_stack.addWidget(self.xps_page)

        # EXAFS analysis page
        self.exafs_page = EXAFSPage(self)
        self.content_stack.addWidget(self.exafs_page)

        # Batch processing page
        self.batch_page = BatchPage(self)
        self.content_stack.addWidget(self.batch_page)

        # Module mapping
        self.module_pages = {
            "background": self.background_page,
            "cif_preprocess": self.cif_page,
            "xrd_simulation": self.simulation_page,
            "xrd_refinement": self.refinement_page,
            "amorphous_fit": self.amorphous_page,
            "xps": self.xps_page,
            "exafs": self.exafs_page,
            "batch": self.batch_page,
        }

    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: white;
                color: {COLORS['text']};
                border-bottom: 1px solid #ddd;
            }}
            QMenuBar::item:selected {{
                background-color: {COLORS['secondary']};
            }}
            QMenu {{
                background-color: white;
                border: 1px solid #ddd;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['secondary']};
            }}
        """)

        # File menu
        file_menu = menubar.addMenu("File(&F)")

        open_action = QAction("Open File...", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        open_dir_action = QAction("Open Directory...", self)
        file_menu.addAction(open_dir_action)

        file_menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit(&E)")

        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        edit_menu.addAction(paste_action)

        # View menu
        view_menu = menubar.addMenu("View(&V)")

        reset_layout_action = QAction("Reset Layout", self)
        view_menu.addAction(reset_layout_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools(&T)")

        settings_action = QAction("Settings...", self)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("Help(&H)")

        about_action = QAction("About...", self)
        help_menu.addAction(about_action)

        docs_action = QAction("Documentation...", self)
        help_menu.addAction(docs_action)

    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: white;
                border-bottom: 1px solid #ddd;
                spacing: 5px;
                padding: 5px;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            QToolButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        self.addToolBar(toolbar)

    def _create_status_bar(self):
        """Create status bar"""
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: white;
                border-top: 1px solid #ddd;
                color: {COLORS['text']};
            }}
        """)

        # Left status label
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)

        # Right info
        info_label = QLabel("PyXplore Desktop v1.0.0")
        self.statusBar().addPermanentWidget(info_label)

    def _connect_signals(self):
        """Connect signals and slots"""
        self.nav_tree.itemClicked.connect(self._on_nav_item_clicked)

    def _on_nav_item_clicked(self, item, column):
        """Navigation item click event"""
        data = item.data(0, Qt.UserRole)
        if data:
            module = data.get("module")
            if module and module in self.module_pages:
                self._switch_module(module)

    def _switch_module(self, module_name):
        """Switch module"""
        if module_name in self.module_pages:
            page = self.module_pages[module_name]
            self.content_stack.setCurrentWidget(page)
            self.current_module = module_name
            self.module_changed.emit(module_name)
            self.logger.info(f"Switched to module: {module_name}")

            # Update status bar
            module_names = {
                "background": "Background Deduction",
                "cif_preprocess": "CIF Preprocess",
                "xrd_simulation": "XRD Simulation",
                "xrd_refinement": "XRD Refinement",
                "amorphous_fit": "Amorphous Fitting",
                "xps": "XPS Analysis",
                "exafs": "EXAFS Analysis",
                "batch": "Batch Processing",
            }
            self.status_label.setText(f"Current Module: {module_names.get(module_name, module_name)}")

    def set_status(self, message):
        """Set status bar message"""
        self.status_label.setText(message)

    def get_wpem(self):
        """Get PyXplore library instance"""
        return self.WPEM