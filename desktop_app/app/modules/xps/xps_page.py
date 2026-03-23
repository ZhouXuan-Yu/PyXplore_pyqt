# -*- coding: utf-8 -*-
"""
XPS分析模块页面
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QDoubleSpinBox, QSpinBox, QTextEdit,
    QGroupBox, QFormLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox
)
from PyQt5.QtCore import Qt
from ...base_page import BasePage
from ...config import DEFAULT_PARAMS
from ...utils import (
    select_file, show_error_message, show_info_message
)


class XPSPage(BasePage):
    """XPS分析页面"""

    def __init__(self, main_window=None):
        self.nobac_file = ""
        self.original_file = ""
        self.bac_file = ""
        super().__init__(main_window)

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = self.create_title_label("XPS分析")
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

        self.nobac_edit = QLineEdit()
        self.nobac_edit.setReadOnly(True)
        nobac_btn = QPushButton("浏览...")
        nobac_btn.clicked.connect(lambda: self._select_file("nobac"))

        self.original_edit = QLineEdit()
        self.original_edit.setReadOnly(True)
        original_btn = QPushButton("浏览...")
        original_btn.clicked.connect(lambda: self._select_file("original"))

        self.bac_edit = QLineEdit()
        self.bac_edit.setReadOnly(True)
        bac_btn = QPushButton("浏览...")
        bac_btn.clicked.connect(lambda: self._select_file("bac"))

        form.addRow("去背景数据:", self.nobac_edit)
        form.addRow("", nobac_btn)
        form.addRow("原始数据:", self.original_edit)
        form.addRow("", original_btn)
        form.addRow("背景数据:", self.bac_edit)
        form.addRow("", bac_btn)

        group.setLayout(form)
        layout.addWidget(group)

        return widget

    def _create_param_section(self):
        """创建参数设置区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        group = self.create_section_group("XPS参数")
        form = QFormLayout()

        self.var_spin = QDoubleSpinBox()
        self.var_spin.setRange(0, 10000)
        self.var_spin.setValue(100)

        self.bta_spin = QDoubleSpinBox()
        self.bta_spin.setRange(0, 1)
        self.bta_spin.setValue(DEFAULT_PARAMS["xps"]["bta"])
        self.bta_spin.setSingleStep(0.05)

        self.iter_max_spin = QSpinBox()
        self.iter_max_spin.setRange(1, 100)
        self.iter_max_spin.setValue(DEFAULT_PARAMS["xps"]["iter_max"])

        self.energy_min = QDoubleSpinBox()
        self.energy_min.setRange(0, 2000)
        self.energy_min.setValue(920)

        self.energy_max = QDoubleSpinBox()
        self.energy_max.setRange(0, 2000)
        self.energy_max.setValue(970)

        form.addRow("方差:", self.var_spin)
        form.addRow("bta:", self.bta_spin)
        form.addRow("最大迭代:", self.iter_max_spin)
        form.addRow("能量起始:", self.energy_min)
        form.addRow("能量终止:", self.energy_max)

        group.setLayout(form)
        layout.addWidget(group)

        group2 = self.create_section_group("原子标识")
        form2 = QFormLayout()

        self.atom_id_table = QTableWidget(2, 4)
        self.atom_id_table.setHorizontalHeaderLabels(["元素", "电子态", "结合能(eV)", ""])
        self.atom_id_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        add_atom_btn = QPushButton("添加")
        add_atom_btn.clicked.connect(self._add_atom_row)
        form2.addRow("", add_atom_btn)

        group2.setLayout(form2)
        layout.addWidget(group2)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.run_btn = self.create_push_button("开始拟合")
        self.run_btn.clicked.connect(self._run_xps)

        btn_layout.addWidget(self.run_btn)
        layout.addLayout(btn_layout)

        return widget

    def _create_result_section(self):
        """创建结果区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("XPS拟合结果")
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
            if file_type == "nobac":
                self.nobac_file = file_path
                self.nobac_edit.setText(file_path)
            elif file_type == "original":
                self.original_file = file_path
                self.original_edit.setText(file_path)
            elif file_type == "bac":
                self.bac_file = file_path
                self.bac_edit.setText(file_path)

    def _add_atom_row(self):
        """添加原子标识行"""
        row = self.atom_id_table.rowCount()
        self.atom_id_table.insertRow(row)

    def _run_xps(self):
        """运行XPS拟合"""
        if not all([self.nobac_file, self.original_file, self.bac_file]):
            show_error_message("错误", "请先选择所有数据文件", self)
            return

        if not self.WPEM:
            show_error_message("错误", "PyXplore库未加载", self)
            return

        self.run_btn.setEnabled(False)
        self.log("开始XPS拟合...")

        try:
            # 读取原子标识
            atomIdentifier = []
            for row in range(self.atom_id_table.rowCount()):
                element = self.atom_id_table.item(row, 0)
                state = self.atom_id_table.item(row, 1)
                energy = self.atom_id_table.item(row, 2)

                if element and state and energy:
                    atomIdentifier.append([
                        element.text(),
                        state.text(),
                        float(energy.text())
                    ])

            if not atomIdentifier:
                show_error_message("错误", "请至少添加一个原子标识", self)
                self.run_btn.setEnabled(True)
                return

            import pandas as pd
            nobac_df = pd.read_csv(self.nobac_file)
            original_df = pd.read_csv(self.original_file)
            bac_df = pd.read_csv(self.bac_file)

            params = {
                'Var': self.var_spin.value(),
                'atomIdentifier': atomIdentifier,
                'satellitePeaks': [],
                'no_bac_df': nobac_df,
                'original_df': original_df,
                'bacground_df': bac_df,
                'energy_range': (self.energy_min.value(), self.energy_max.value()),
                'bta': self.bta_spin.value(),
                'iter_max': self.iter_max_spin.value(),
            }

            self.WPEM.XPSfit(**params)

            self.log("XPS拟合完成!")
            show_info_message("完成", "XPS拟合完成!", self)

        except Exception as e:
            self.log(f"错误: {str(e)}")
            show_error_message("处理失败", str(e), self)

        finally:
            self.run_btn.setEnabled(True)

    def log(self, message):
        self.result_text.append(f"> {message}")