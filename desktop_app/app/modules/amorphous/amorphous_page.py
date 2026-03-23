# -*- coding: utf-8 -*-
"""
非晶分析模块页面
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QTextEdit, QGroupBox, QFormLayout, QSplitter, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from ...base_page import BasePage
from ...config import XRAY_WAVELENGTHS, DEFAULT_PARAMS
from pathlib import Path
from ...utils import (
    select_file, show_error_message, show_info_message,
    format_wpem_missing_message,
)


class AmorphousPage(BasePage):
    """非晶分析页面"""

    def __init__(self, main_window=None):
        self.amorphous_file = ""
        super().__init__(main_window)

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = self.create_title_label("非晶分析")
        layout.addWidget(title)

        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # 非晶峰拟合页面
        fit_tab = self._create_fit_tab()
        tab_widget.addTab(fit_tab, "非晶峰拟合")

        # RDF计算页面
        rdf_tab = self._create_rdf_tab()
        tab_widget.addTab(rdf_tab, "RDF计算")

    def _create_fit_tab(self):
        """创建非晶峰拟合标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        param_group = self.create_section_group("参数设置")
        form = QFormLayout()

        self.amorphous_edit = QLineEdit()
        self.amorphous_edit.setReadOnly(True)
        self.amorphous_edit.setPlaceholderText("选择非晶相数据文件...")
        amor_btn = QPushButton("浏览...")
        amor_btn.clicked.connect(self._select_amorphous_file)

        form.addRow("数据文件:", self.amorphous_edit)
        form.addRow("", amor_btn)

        self.mix_component_spin = QSpinBox()
        self.mix_component_spin.setRange(1, 10)
        self.mix_component_spin.setValue(DEFAULT_PARAMS["amorphous"]["mix_component"])

        self.ang_min = QDoubleSpinBox()
        self.ang_min.setRange(0, 180)
        self.ang_min.setValue(10)

        self.ang_max = QDoubleSpinBox()
        self.ang_max.setRange(0, 180)
        self.ang_max.setValue(50)

        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(100, 10000)
        self.max_iter_spin.setValue(DEFAULT_PARAMS["amorphous"]["max_iter"])

        form.addRow("峰数量:", self.mix_component_spin)
        form.addRow("2θ起始:", self.ang_min)
        form.addRow("2θ终止:", self.ang_max)
        form.addRow("最大迭代:", self.max_iter_spin)

        param_group.setLayout(form)
        splitter.addWidget(param_group)

        self.fit_log = QTextEdit()
        self.fit_log.setReadOnly(True)
        self.fit_log.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
            }
        """)
        splitter.addWidget(self.fit_log)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.fit_btn = self.create_push_button("开始拟合")
        self.fit_btn.clicked.connect(self._run_amorphous_fit)

        btn_layout.addWidget(self.fit_btn)
        layout.addLayout(btn_layout)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        return widget

    def _create_rdf_tab(self):
        """创建RDF计算标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        param_group = self.create_section_group("参数设置")
        form = QFormLayout()

        self.rdf_wavelength_combo = QComboBox()
        self.rdf_wavelength_combo.addItems(list(XRAY_WAVELENGTHS.keys()))
        self.rdf_wavelength_combo.setCurrentText("CuKa")

        self.r_max_spin = QDoubleSpinBox()
        self.r_max_spin.setRange(1, 20)
        self.r_max_spin.setValue(5)
        self.r_max_spin.setSuffix(" Å")

        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(0.1, 100)
        self.density_spin.setValue(5)
        self.density_spin.setSuffix(" g/cm³")

        self.highlight_spin = QSpinBox()
        self.highlight_spin.setRange(1, 10)
        self.highlight_spin.setValue(4)

        form.addRow("波长:", self.rdf_wavelength_combo)
        form.addRow("最大半径:", self.r_max_spin)
        form.addRow("样品密度:", self.density_spin)
        form.addRow("突出峰数:", self.highlight_spin)

        param_group.setLayout(form)
        layout.addWidget(param_group)

        self.rdf_log = QTextEdit()
        self.rdf_log.setReadOnly(True)
        self.rdf_log.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.rdf_log)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.rdf_btn = self.create_push_button("计算RDF")
        self.rdf_btn.clicked.connect(self._run_rdf)

        btn_layout.addWidget(self.rdf_btn)

        return widget

    def _select_amorphous_file(self):
        """选择非晶数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择非晶数据文件", "",
            "CSV文件 (*.csv);;所有文件 (*.*)"
        )
        if file_path:
            self.amorphous_file = file_path
            self.amorphous_edit.setText(file_path)
            self.log("已选择非晶数据文件")

    def _run_amorphous_fit(self):
        """运行非晶峰拟合"""
        if not self.amorphous_file:
            show_error_message("错误", "请先选择非晶数据文件", self)
            return

        if not self.WPEM:
            show_error_message("错误", format_wpem_missing_message(self), self)
            return

        self.fit_btn.setEnabled(False)
        self.log("开始非晶峰拟合...")

        try:
            # work_dir 放在 output/amorphous 下，WPEM 会在其下建 DecomposedComponents/ 等目录
            work_dir = self.get_output_dir() / "amorphous"
            work_dir.mkdir(parents=True, exist_ok=True)
            params = {
                'mix_component': self.mix_component_spin.value(),
                'amor_file': self.amorphous_file,
                'ang_range': (self.ang_min.value(), self.ang_max.value()),
                'max_iter': self.max_iter_spin.value(),
                'Wavelength': XRAY_WAVELENGTHS[self.rdf_wavelength_combo.currentText()],
                'work_dir': str(work_dir),
            }

            self.WPEM.Amorphous_fit(**params)

            self.log("非晶峰拟合完成!")
            self.record_operation_history(
                "非晶峰拟合",
                str(work_dir),
                total=1,
                success=1,
                files=[self.amorphous_file],
            )
            show_info_message("完成", "非晶峰拟合完成!", self)

        except Exception as e:
            self.log(f"错误: {str(e)}")
            show_error_message("处理失败", str(e), self)

        finally:
            self.fit_btn.setEnabled(True)

    def _run_rdf(self):
        """运行RDF计算"""
        if not self.WPEM:
            show_error_message("错误", format_wpem_missing_message(self), self)
            return

        self.rdf_btn.setEnabled(False)
        self.log("开始RDF计算...")

        try:
            # work_dir 放在 output/amorphous 下，WPEM 会在其下建 DecomposedComponents/ 等目录
            work_dir = self.get_output_dir() / "amorphous"
            work_dir.mkdir(parents=True, exist_ok=True)
            params = {
                'wavelength': XRAY_WAVELENGTHS[self.rdf_wavelength_combo.currentText()],
                'r_max': self.r_max_spin.value(),
                'density_zero': self.density_spin.value(),
                'highlight': self.highlight_spin.value(),
                'work_dir': str(work_dir),
            }

            self.WPEM.AmorphousRDFun(**params)

            self.log("RDF计算完成!")
            self.record_operation_history(
                "RDF计算",
                str(work_dir),
                total=1,
                success=1,
                files=[self.amorphous_file] if self.amorphous_file else None,
            )
            show_info_message("完成", "RDF计算完成!", self)

        except Exception as e:
            self.log(f"错误: {str(e)}")
            show_error_message("处理失败", str(e), self)

        finally:
            self.rdf_btn.setEnabled(True)

    def log(self, message):
        self.fit_log.append(f"> {message}")
        self.rdf_log.append(f"> {message}")