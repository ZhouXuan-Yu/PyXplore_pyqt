# -*- coding: utf-8 -*-
"""
CIF Preprocess Module Page
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox,
    QTextEdit, QGroupBox, QFormLayout, QSplitter
)
from PyQt5.QtCore import Qt
from ...base_page import BasePage
from ...config import XRAY_WAVELENGTHS, DEFAULT_PARAMS
from ...utils import (
    validate_cif_file, select_file, show_error_message, show_info_message,
    format_number
)


class CIFPreprocessPage(BasePage):
    """CIF Preprocess Page"""

    def __init__(self, main_window=None):
        self.cif_file = ""
        self.lattice_constants = None
        self.atom_coordinates = None
        self.lattice_density = None
        super().__init__(main_window)

    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = self.create_title_label("CIF Preprocess")
        layout.addWidget(title)

        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        param_widget = self._create_param_section()
        splitter.addWidget(param_widget)

        result_widget = self._create_result_section()
        splitter.addWidget(result_widget)

        log_widget = self._create_log_section()
        splitter.addWidget(log_widget)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)

    def _create_param_section(self):
        """Create parameter setting area"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        file_group = self.create_section_group("File Input")
        file_layout = QFormLayout()

        self.cif_file_edit = QLineEdit()
        self.cif_file_edit.setPlaceholderText("Select CIF file...")
        self.cif_file_edit.setReadOnly(True)

        cif_btn = QPushButton("Browse...")
        cif_btn.clicked.connect(self._select_cif_file)

        file_layout.addRow("CIF File:", self.cif_file_edit)
        file_layout.addRow("", cif_btn)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        param_group = self.create_section_group("Parameters")
        param_layout = QFormLayout()

        self.wavelength_combo = QComboBox()
        self.wavelength_combo.addItems(list(XRAY_WAVELENGTHS.keys()))
        self.wavelength_combo.setCurrentText(DEFAULT_PARAMS["cif_preprocess"]["wavelength"])

        self.two_theta_min_spin = QDoubleSpinBox()
        self.two_theta_min_spin.setRange(0, 180)
        self.two_theta_min_spin.setValue(DEFAULT_PARAMS["cif_preprocess"]["two_theta_range"][0])

        self.two_theta_max_spin = QDoubleSpinBox()
        self.two_theta_max_spin.setRange(0, 180)
        self.two_theta_max_spin.setValue(DEFAULT_PARAMS["cif_preprocess"]["two_theta_range"][1])

        self.show_unitcell_check = QCheckBox()
        self.show_unitcell_check.setChecked(DEFAULT_PARAMS["cif_preprocess"]["show_unitcell"])

        self.cal_extinction_check = QCheckBox()
        self.cal_extinction_check.setChecked(DEFAULT_PARAMS["cif_preprocess"]["cal_extinction"])

        param_layout.addRow("Wavelength:", self.wavelength_combo)
        param_layout.addRow("2theta Min:", self.two_theta_min_spin)
        param_layout.addRow("2theta Max:", self.two_theta_max_spin)
        param_layout.addRow("Show UnitCell:", self.show_unitcell_check)
        param_layout.addRow("Calculate Extinction:", self.cal_extinction_check)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.run_btn = self.create_push_button("Parse CIF")
        self.run_btn.clicked.connect(self._run_cif_preprocess)

        self.export_btn = self.create_secondary_button("Export Parameters")
        self.export_btn.clicked.connect(self._export_params)
        self.export_btn.setEnabled(False)

        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.export_btn)

        layout.addLayout(btn_layout)

        return widget

    def _create_result_section(self):
        """Create result area"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        result_label = QLabel("Parse Result")
        result_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("CIF parse result will be displayed here...")
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.result_text)

        return widget

    def _create_log_section(self):
        """Create log area"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        log_label = QLabel("Run Log")
        log_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Run log will be displayed here...")
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.log_text)

        return widget

    def _select_cif_file(self):
        """Select CIF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CIF File", "",
            "CIF files (*.cif);;All files (*.*)"
        )
        if file_path:
            self.cif_file = file_path
            self.cif_file_edit.setText(file_path)
            self.log(f"Selected CIF file: {file_path}")

    def _run_cif_preprocess(self):
        """Run CIF preprocess - directly calls PyXplore library"""
        if not self.cif_file:
            show_error_message("Error", "Please select a CIF file first", self)
            return

        if not self.WPEM:
            show_error_message("Error", "PyXplore library not loaded", self)
            return

        self.run_btn.setEnabled(False)
        self.log("Starting CIF preprocess...")

        try:
            # Prepare parameters for PyXplore
            params = {
                'filepath': self.cif_file,
                'wavelength': self.wavelength_combo.currentText(),
                'two_theta_range': (
                    self.two_theta_min_spin.value(),
                    self.two_theta_max_spin.value()
                ),
                'show_unitcell': self.show_unitcell_check.isChecked(),
                'cal_extinction': self.cal_extinction_check.isChecked(),
            }

            # Call PyXplore library directly
            result = self.WPEM.CIFpreprocess(**params)

            self.lattice_constants, self.atom_coordinates, self.lattice_density = result

            self._display_results()
            self.export_btn.setEnabled(True)

            show_info_message("Complete", "CIF preprocess completed!", self)

        except Exception as e:
            self.log(f"Error: {str(e)}")
            show_error_message("Process Failed", str(e), self)

        finally:
            self.run_btn.setEnabled(True)

    def _display_results(self):
        """Display results"""
        result = f"Lattice Constants:\n"
        result += f"  a = {format_number(self.lattice_constants[0])} A\n"
        result += f"  b = {format_number(self.lattice_constants[1])} A\n"
        result += f"  c = {format_number(self.lattice_constants[2])} A\n"
        result += f"  alpha = {format_number(self.lattice_constants[3])} deg\n"
        result += f"  beta = {format_number(self.lattice_constants[4])} deg\n"
        result += f"  gamma = {format_number(self.lattice_constants[5])} deg\n\n"
        result += f"Lattice Density: {format_number(self.lattice_density, 6)} g/cm3\n\n"
        result += f"Atom Coordinates ({len(self.atom_coordinates)} atoms):\n"

        for i, atom in enumerate(self.atom_coordinates[:20]):
            result += f"  {atom[0]}: ({format_number(atom[1])}, {format_number(atom[2])}, {format_number(atom[3])})\n"

        if len(self.atom_coordinates) > 20:
            result += f"  ... and {len(self.atom_coordinates) - 20} more atoms\n"

        self.result_text.setText(result)
        self.log("CIF preprocess completed")

    def _export_params(self):
        """Export parameters"""
        if not self.lattice_constants:
            show_error_message("Error", "No data to export", self)
            return

        from ...utils import save_file_dialog
        file_path = save_file_dialog(
            self, "Save Parameters", "lattice_params.txt",
            "Text files (*.txt);;All files (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Lattice Constants\n")
                    f.write(f"a = {self.lattice_constants[0]}\n")
                    f.write(f"b = {self.lattice_constants[1]}\n")
                    f.write(f"c = {self.lattice_constants[2]}\n")
                    f.write(f"alpha = {self.lattice_constants[3]}\n")
                    f.write(f"beta = {self.lattice_constants[4]}\n")
                    f.write(f"gamma = {self.lattice_constants[5]}\n\n")
                    f.write(f"Lattice Density = {self.lattice_density}\n\n")
                    f.write("Atom Coordinates\n")
                    for atom in self.atom_coordinates:
                        f.write(f"{atom[0]}\t{atom[1]}\t{atom[2]}\t{atom[3]}\n")

                self.log(f"Parameters exported to: {file_path}")
                show_info_message("Export Success", f"Parameters saved to:\n{file_path}", self)

            except Exception as e:
                show_error_message("Export Failed", str(e), self)

    def log(self, message):
        """Add log message"""
        self.log_text.append(f"> {message}")