# -*- coding: utf-8 -*-
"""
XRD精修模块页面
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox, QSpinBox,
    QTextEdit, QGroupBox, QFormLayout, QSplitter, QListWidget
)
from PyQt5.QtCore import Qt
from ...base_page import BasePage
from ...config import DEFAULT_PARAMS
from ...utils import (
    select_file, select_files, show_error_message, show_info_message
)


class XRDRefinementPage(BasePage):
    """XRD精修页面"""

    def __init__(self, main_window=None):
        self.original_file = ""
        self.nobac_file = ""
        self.bac_file = ""
        self.cif_files = []
        super().__init__(main_window)

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = self.create_title_label("XRD精修 (WPEM)")
        layout.addWidget(title)

        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        data_widget = self._create_data_section()
        splitter.addWidget(data_widget)

        param_widget = self._create_param_section()
        splitter.addWidget(param_widget)

        result_widget = self._create_result_section()
        splitter.addWidget(result_widget)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)

    def _create_data_section(self):
        """创建数据输入区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        group = self.create_section_group("数据文件")
        form = QFormLayout()

        self.original_edit = QLineEdit()
        self.original_edit.setReadOnly(True)
        original_btn = QPushButton("浏览...")
        original_btn.clicked.connect(lambda: self._select_file("original"))

        self.nobac_edit = QLineEdit()
        self.nobac_edit.setReadOnly(True)
        nobac_btn = QPushButton("浏览...")
        nobac_btn.clicked.connect(lambda: self._select_file("nobac"))

        self.bac_edit = QLineEdit()
        self.bac_edit.setReadOnly(True)
        bac_btn = QPushButton("浏览...")
        bac_btn.clicked.connect(lambda: self._select_file("bac"))

        self.cif_list = QListWidget()
        cif_btn = QPushButton("添加CIF文件...")
        cif_btn.clicked.connect(self._add_cif_files)

        form.addRow("原始数据:", self.original_edit)
        form.addRow("", original_btn)
        form.addRow("去背景数据:", self.nobac_edit)
        form.addRow("", nobac_btn)
        form.addRow("背景数据:", self.bac_edit)
        form.addRow("", bac_btn)
        form.addRow("CIF文件:", self.cif_list)
        form.addRow("", cif_btn)

        group.setLayout(form)
        layout.addWidget(group)

        return widget

    def _create_param_section(self):
        """创建参数设置区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        group = self.create_section_group("精修参数")
        form = QFormLayout()

        self.wavelength_edit = QLineEdit("1.54184")
        self.wavelength_edit.setPlaceholderText("波长(Å)")

        self.var_spin = QDoubleSpinBox()
        self.var_spin.setRange(0, 10000)
        self.var_spin.setValue(100)

        self.bta_spin = QDoubleSpinBox()
        self.bta_spin.setRange(0, 1)
        self.bta_spin.setValue(DEFAULT_PARAMS["xrd_refinement"]["bta"])
        self.bta_spin.setSingleStep(0.05)

        self.iter_max_spin = QSpinBox()
        self.iter_max_spin.setRange(1, 100)
        self.iter_max_spin.setValue(DEFAULT_PARAMS["xrd_refinement"]["iter_max"])

        self.cpu_spin = QSpinBox()
        self.cpu_spin.setRange(1, 16)
        self.cpu_spin.setValue(DEFAULT_PARAMS["xrd_refinement"]["cpu"])

        self.model_combo = QComboBox()
        self.model_combo.addItems(["REFINEMENT", "ANALYSIS"])

        form.addRow("波长(Å):", self.wavelength_edit)
        form.addRow("方差:", self.var_spin)
        form.addRow("bta:", self.bta_spin)
        form.addRow("最大迭代:", self.iter_max_spin)
        form.addRow("CPU核心:", self.cpu_spin)
        form.addRow("模式:", self.model_combo)

        group.setLayout(form)
        layout.addWidget(group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.run_btn = self.create_push_button("开始精修")
        self.run_btn.clicked.connect(self._run_refinement)

        btn_layout.addWidget(self.run_btn)
        layout.addLayout(btn_layout)

        return widget

    def _create_result_section(self):
        """创建结果区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("精修结果")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
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

    def _select_file(self, file_type):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "",
            "CSV文件 (*.csv);;所有文件 (*.*)"
        )
        if file_path:
            if file_type == "original":
                self.original_file = file_path
                self.original_edit.setText(file_path)
            elif file_type == "nobac":
                self.nobac_file = file_path
                self.nobac_edit.setText(file_path)
            elif file_type == "bac":
                self.bac_file = file_path
                self.bac_edit.setText(file_path)

    def _add_cif_files(self):
        """添加CIF文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择CIF文件", "",
            "CIF文件 (*.cif);;所有文件 (*.*)"
        )
        for f in files:
            if f not in self.cif_files:
                self.cif_files.append(f)
                self.cif_list.addItem(f)

    def _run_refinement(self):
        """运行精修"""
        if not all([self.original_file, self.nobac_file, self.bac_file]):
            show_error_message("错误", "请先选择所有必要的数据文件", self)
            return

        if not self.cif_files:
            show_error_message("错误", "请至少添加一个CIF文件", self)
            return

        if not self.WPEM:
            show_error_message("错误", "PyXplore库未加载", self)
            return

        self.run_btn.setEnabled(False)
        self.log("开始XRD精修...")

        try:
            # Parse lattice constants using PyXplore directly
            lattice_list = []
            density_list = []

            for cif in self.cif_files:
                latt, atoms, dens = self.WPEM.CIFpreprocess(
                    filepath=cif,
                    wavelength='CuKa',
                    cal_extinction=False
                )
                lattice_list.append(latt)
                density_list.append(dens)

            params = {
                'wavelength': [float(self.wavelength_edit.text())],
                'Var': self.var_spin.value(),
                'Lattice_constants': lattice_list,
                'no_bac_intensity_file': self.nobac_file,
                'original_file': self.original_file,
                'bacground_file': self.bac_file,
                'density_list': density_list,
                'bta': self.bta_spin.value(),
                'iter_max': self.iter_max_spin.value(),
                'cpu': self.cpu_spin.value(),
                'MODEL': self.model_combo.currentText(),
            }

            durtime, ini_CL = self.WPEM.XRDfit(**params)

            result = f"精修完成!\n"
            result += f"运行时间: {durtime}\n\n"
            result += "精修后的晶格常数:\n"

            for i, lc in enumerate(ini_CL):
                result += f"相{i+1}: a={lc[0]:.4f} b={lc[1]:.4f} c={lc[2]:.4f} "
                result += f"α={lc[3]:.2f}° β={lc[4]:.2f}° γ={lc[5]:.2f}°\n"

            self.result_text.setText(result)
            self.log("XRD精修完成!")

            show_info_message("完成", "精修完成!", self)

        except Exception as e:
            self.log(f"错误: {str(e)}")
            show_error_message("处理失败", str(e), self)

        finally:
            self.run_btn.setEnabled(True)

    def log(self, message):
        self.result_text.append(f"> {message}")