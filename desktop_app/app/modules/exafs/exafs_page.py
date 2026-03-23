# -*- coding: utf-8 -*-
"""
EXAFS分析模块页面
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QDoubleSpinBox, QSpinBox, QTextEdit, QCheckBox,
    QGroupBox, QFormLayout, QSplitter, QComboBox, QWidget
)
from PyQt5.QtCore import Qt
from ...base_page import BasePage
from ...config import DEFAULT_PARAMS
from ...utils import (
    select_file, show_error_message, show_info_message
)


class EXAFSPage(BasePage):
    """EXAFS分析页面"""

    def __init__(self, main_window=None):
        self.xafs_file = ""
        super().__init__(main_window)

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = self.create_title_label("EXAFS分析")
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

        group = self.create_section_group("数据输入")
        form = QFormLayout()

        self.xafs_edit = QLineEdit()
        self.xafs_edit.setReadOnly(True)
        self.xafs_edit.setPlaceholderText("选择XAFS数据文件...")
        xafs_btn = QPushButton("浏览...")
        xafs_btn.clicked.connect(self._select_xafs_file)

        form.addRow("XAFS数据:", self.xafs_edit)
        form.addRow("", xafs_btn)

        group.setLayout(form)
        layout.addWidget(group)

        return widget

    def _create_param_section(self):
        """创建参数设置区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        group = self.create_section_group("EXAFS参数")
        form = QFormLayout()

        self.power_spin = QSpinBox()
        self.power_spin.setRange(1, 5)
        self.power_spin.setValue(DEFAULT_PARAMS["exafs"]["power"])

        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(1, 20)
        self.distance_spin.setValue(DEFAULT_PARAMS["exafs"]["distance"])
        self.distance_spin.setSuffix(" Å")

        self.k_point_spin = QSpinBox()
        self.k_point_spin.setRange(1, 20)
        self.k_point_spin.setValue(DEFAULT_PARAMS["exafs"]["k_point"])

        self.k_spin = QSpinBox()
        self.k_spin.setRange(1, 5)
        self.k_spin.setValue(3)

        self.window_size_spin = QSpinBox()
        self.window_size_spin.setRange(10, 100)
        self.window_size_spin.setValue(30)

        self.transform_combo = QComboBox()
        self.transform_combo.addItems(["fourier", "wavelet"])

        self.de_bac_check = QCheckBox()

        form.addRow("k轴功率:", self.power_spin)
        form.addRow("R空间距离:", self.distance_spin)
        form.addRow("k点截断:", self.k_point_spin)
        form.addRow("样条阶数:", self.k_spin)
        form.addRow("窗口大小:", self.window_size_spin)
        form.addRow("变换方式:", self.transform_combo)
        form.addRow("扣除背景:", self.de_bac_check)

        group.setLayout(form)
        layout.addWidget(group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.run_btn = self.create_push_button("开始分析")
        self.run_btn.clicked.connect(self._run_exafs)

        btn_layout.addWidget(self.run_btn)
        layout.addLayout(btn_layout)

        return widget

    def _create_result_section(self):
        """创建结果区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("EXAFS分析结果")
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

    def _select_xafs_file(self):
        """选择XAFS文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择XAFS数据文件", "",
            "数据文件 (*.csv *.txt *.dat);;所有文件 (*.*)"
        )
        if file_path:
            self.xafs_file = file_path
            self.xafs_edit.setText(file_path)
            self.log(f"已选择XAFS文件: {file_path}")

    def _run_exafs(self):
        """运行EXAFS分析"""
        if not self.xafs_file:
            show_error_message("错误", "请先选择XAFS数据文件", self)
            return

        if not self.WPEM:
            show_error_message("错误", "PyXplore库未加载", self)
            return

        self.run_btn.setEnabled(False)
        self.log("开始EXAFS分析...")

        try:
            params = {
                'XAFSdata': self.xafs_file,
                'power': self.power_spin.value(),
                'distance': self.distance_spin.value(),
                'k_point': self.k_point_spin.value(),
                'k': self.k_spin.value(),
                'window_size': self.window_size_spin.value(),
                'transform': self.transform_combo.currentText(),
                'de_bac': self.de_bac_check.isChecked(),
            }

            self.WPEM.EXAFSfit(**params)

            self.log("EXAFS分析完成!")
            show_info_message("完成", "EXAFS分析完成!", self)

        except Exception as e:
            self.log(f"错误: {str(e)}")
            show_error_message("处理失败", str(e), self)

        finally:
            self.run_btn.setEnabled(True)

    def log(self, message):
        self.result_text.append(f"> {message}")