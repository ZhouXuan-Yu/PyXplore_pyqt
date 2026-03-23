# -*- coding: utf-8 -*-
"""
XRD模拟模块页面
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox, QSpinBox,
    QTextEdit, QGroupBox, QFormLayout, QSplitter
)
from PyQt5.QtCore import Qt
from ...base_page import BasePage
from ...config import XRAY_WAVELENGTHS, DEFAULT_PARAMS
from ...utils import (
    validate_cif_file, select_file, show_error_message, show_info_message,
    format_wpem_missing_message,
    get_output_path
)


class XRDSimulationPage(BasePage):
    """XRD模拟页面"""

    def __init__(self, main_window=None):
        self.cif_file = ""
        super().__init__(main_window)

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = self.create_title_label("XRD模拟")
        layout.addWidget(title)

        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        param_widget = self._create_param_section()
        splitter.addWidget(param_widget)

        preview_widget = self._create_preview_section()
        splitter.addWidget(preview_widget)

        log_widget = self._create_log_section()
        splitter.addWidget(log_widget)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)

    def _create_param_section(self):
        """创建参数设置区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        file_group = self.create_section_group("结构输入")
        file_layout = QFormLayout()
        self.cif_file_edit = QLineEdit()
        self.cif_file_edit.setPlaceholderText("选择CIF文件...")
        self.cif_file_edit.setReadOnly(True)
        cif_btn = QPushButton("浏览...")
        cif_btn.clicked.connect(self._select_cif_file)
        file_layout.addRow("CIF文件:", self.cif_file_edit)
        file_layout.addRow("", cif_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        param_group = self.create_section_group("模拟参数")
        param_layout = QFormLayout()

        self.wavelength_combo = QComboBox()
        self.wavelength_combo.addItems(list(XRAY_WAVELENGTHS.keys()))
        self.wavelength_combo.setCurrentText(DEFAULT_PARAMS["xrd_simulation"]["wavelength"])

        self.two_theta_min = QDoubleSpinBox()
        self.two_theta_min.setRange(0, 180)
        self.two_theta_min.setValue(10)

        self.two_theta_max = QDoubleSpinBox()
        self.two_theta_max.setRange(0, 180)
        self.two_theta_max.setValue(90)

        self.step_size = QDoubleSpinBox()
        self.step_size.setRange(0.001, 1.0)
        self.step_size.setValue(0.01)
        self.step_size.setDecimals(3)

        self.supercell_check = QCheckBox()
        self.supercell_check.setText("构建超胞")
        self.supercell_check.setChecked(DEFAULT_PARAMS["xrd_simulation"]["SuperCell"])

        self.periodic_x = QSpinBox()
        self.periodic_x.setRange(1, 10)
        self.periodic_x.setValue(3)

        self.periodic_y = QSpinBox()
        self.periodic_y.setRange(1, 10)
        self.periodic_y.setValue(3)

        self.periodic_z = QSpinBox()
        self.periodic_z.setRange(1, 10)
        self.periodic_z.setValue(3)

        self.grain_size_spin = QDoubleSpinBox()
        self.grain_size_spin.setRange(5, 30)
        self.grain_size_spin.setValue(15)
        self.grain_size_spin.setSuffix(" nm")

        self.peakwidth_check = QCheckBox("考虑峰宽")
        self.peakwidth_check.setChecked(DEFAULT_PARAMS["xrd_simulation"]["PeakWidth"])

        self.zeroshift_spin = QDoubleSpinBox()
        self.zeroshift_spin.setRange(-3, 3)
        self.zeroshift_spin.setValue(0)
        self.zeroshift_spin.setSuffix("°")

        self.bacI_check = QCheckBox("添加模拟背景")

        param_layout.addRow("波长:", self.wavelength_combo)
        param_layout.addRow("2θ起始:", self.two_theta_min)
        param_layout.addRow("2θ终止:", self.two_theta_max)
        param_layout.addRow("步长:", self.step_size)
        param_layout.addRow("", self.supercell_check)
        param_layout.addRow("超胞尺寸 X:", self.periodic_x)
        param_layout.addRow("Y:", self.periodic_y)
        param_layout.addRow("Z:", self.periodic_z)
        param_layout.addRow("晶粒尺寸:", self.grain_size_spin)
        param_layout.addRow("", self.peakwidth_check)
        param_layout.addRow("零点偏移:", self.zeroshift_spin)
        param_layout.addRow("", self.bacI_check)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.run_btn = self.create_push_button("开始模拟")
        self.run_btn.clicked.connect(self._run_simulation)

        self.save_btn = self.create_secondary_button("保存结果")
        self.save_btn.clicked.connect(self._save_results)
        self.save_btn.setEnabled(False)

        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

        return widget

    def _create_preview_section(self):
        """创建预览区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        preview_label = QLabel("模拟结果预览")
        preview_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("模拟结果将显示在这里...")
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.preview_text)

        return widget

    def _create_log_section(self):
        """创建日志区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        log_label = QLabel("运行日志")
        log_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
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
        """选择CIF文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CIF文件", "",
            "CIF文件 (*.cif);;所有文件 (*.*)"
        )
        if file_path:
            self.cif_file = file_path
            self.cif_file_edit.setText(file_path)
            self.log(f"已选择CIF文件: {file_path}")

    def _run_simulation(self):
        """运行XRD模拟"""
        if not self.cif_file:
            show_error_message("错误", "请先选择CIF文件", self)
            return
        if not self.WPEM:
            show_error_message("错误", format_wpem_missing_message(self), self)
            return

        self.run_btn.setEnabled(False)
        self.log("开始XRD模拟...")

        try:
            two_theta_range = (
                self.two_theta_min.value(),
                self.two_theta_max.value(),
                self.step_size.value()
            )

            # work_dir 放在 output/simulation 下，WPEM 会在其下建 Simulation_WPEM/ 子目录
            work_dir = self.get_output_dir() / "simulation"
            work_dir.mkdir(parents=True, exist_ok=True)
            params = {
                'filepath': self.cif_file,
                'wavelength': self.wavelength_combo.currentText(),
                'two_theta_range': two_theta_range,
                'SuperCell': self.supercell_check.isChecked(),
                'PeriodicArr': [self.periodic_x.value(), self.periodic_y.value(), self.periodic_z.value()],
                'PeakWidth': self.peakwidth_check.isChecked(),
                'GrainSize': self.grain_size_spin.value() if self.peakwidth_check.isChecked() else None,
                'zero_shift': self.zeroshift_spin.value() if self.zeroshift_spin.value() != 0 else None,
                'bacI': self.bacI_check.isChecked(),
                'work_dir': str(work_dir),
            }

            result = self.WPEM.XRDSimulation(**params)

            self.log("XRD模拟完成!")
            preview = f"模拟完成\n"
            preview += f"2θ范围: {two_theta_range[0]} - {two_theta_range[1]}°\n"
            preview += f"数据点数: {len(result[1])}\n"
            preview += f"输出目录: Simulation_WPEM/"

            self.preview_text.setText(preview)
            self.save_btn.setEnabled(True)

            self.record_operation_history(
                "XRD模拟",
                str(work_dir),
                total=1,
                success=1,
                files=[self.cif_file],
            )
            show_info_message("完成", "XRD模拟完成!", self)

        except Exception as e:
            self.log(f"错误: {str(e)}")
            show_error_message("处理失败", str(e), self)

        finally:
            self.run_btn.setEnabled(True)

    def _save_results(self):
        """保存结果"""
        output_dir = self.get_output_dir() / "simulation"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 从 output/simulation/Simulation_WPEM/ 复制回来（与传入的 work_dir 一致）
        source_dir = self.get_output_dir() / "simulation" / "Simulation_WPEM"
        if source_dir.exists():
            import shutil
            dest = output_dir
            for f in source_dir.glob("*.csv"):
                shutil.copy(f, dest / f.name)
            for f in source_dir.glob("*.png"):
                shutil.copy(f, dest / f.name)

            self.log(f"结果已保存到: {output_dir}")
            show_info_message("保存成功", f"结果已保存到:\n{output_dir}", self)
        else:
            show_error_message("错误", "找不到输出文件", self)

    def log(self, message):
        self.log_text.append(f"> {message}")