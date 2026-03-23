# -*- coding: utf-8 -*-
"""
背景扣除模块页面
"""

import os
import pandas as pd
from pathlib import Path
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QTextEdit, QGroupBox, QFormLayout, QMessageBox, QSplitter, QWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from ...base_page import BasePage
from ...config import XRAY_WAVELENGTHS, SPECTRUM_TYPES, BAC_VAR_TYPES, DEFAULT_PARAMS
from ...utils import (
    load_xrd_data, validate_data_file, select_file, save_file_dialog,
    show_error_message, show_info_message, get_output_path
)


class BackgroundPage(BasePage):
    """背景扣除页面"""

    def __init__(self, main_window=None):
        self.input_file = ""
        self.output_data = None
        self.background_std = None
        super().__init__(main_window)

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 标题
        title = self.create_title_label("背景扣除")
        layout.addWidget(title)

        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        # 上部：参数设置
        param_widget = self._create_param_section()
        splitter.addWidget(param_widget)

        # 中部：预览区
        preview_widget = self._create_preview_section()
        splitter.addWidget(preview_widget)

        # 下部：日志区
        log_widget = self._create_log_section()
        splitter.addWidget(log_widget)

        # 设置分割比例
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)

    def _create_param_section(self):
        """创建参数设置区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 文件输入组
        file_group = self.create_section_group("文件输入")
        file_layout = QFormLayout()

        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("选择XRD数据文件...")
        self.input_file_edit.setReadOnly(True)

        input_btn = QPushButton("浏览...")
        input_btn.clicked.connect(self._select_input_file)

        file_layout.addRow("原始数据:", self.input_file_edit)
        file_layout.addRow("", input_btn)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 参数设置组
        param_group = self.create_section_group("参数设置")
        param_layout = QFormLayout()

        # 谱图类型
        self.spectrum_type_combo = QComboBox()
        self.spectrum_type_combo.addItems(SPECTRUM_TYPES)
        self.spectrum_type_combo.setCurrentText("XRD")

        # 波长
        self.wavelength_combo = QComboBox()
        self.wavelength_combo.addItems(list(XRAY_WAVELENGTHS.keys()))

        # 低频滤波比例
        self.lfctg_spin = QDoubleSpinBox()
        self.lfctg_spin.setRange(0.01, 1.0)
        self.lfctg_spin.setValue(DEFAULT_PARAMS["background"]["LFctg"])
        self.lfctg_spin.setSingleStep(0.05)
        self.lfctg_spin.setDecimals(2)

        # 背景点数
        self.bac_num_spin = QSpinBox()
        self.bac_num_spin.setRange(10, 1000)
        self.bac_num_spin.setValue(100)

        # 分段数
        self.bac_split_spin = QSpinBox()
        self.bac_split_spin.setRange(2, 20)
        self.bac_split_spin.setValue(DEFAULT_PARAMS["background"]["bac_split"])

        # SG滤波窗口
        self.window_spin = QSpinBox()
        self.window_spin.setRange(5, 51)
        self.window_spin.setValue(DEFAULT_PARAMS["background"]["window_length"])
        self.window_spin.setSingleStep(2)

        # 多项式阶数
        self.polyorder_spin = QSpinBox()
        self.polyorder_spin.setRange(1, 10)
        self.polyorder_spin.setValue(DEFAULT_PARAMS["background"]["polyorder"])

        # 背景方差类型
        self.bac_var_combo = QComboBox()
        self.bac_var_combo.addItems(BAC_VAR_TYPES)

        param_layout.addRow("谱图类型:", self.spectrum_type_combo)
        param_layout.addRow("波长:", self.wavelength_combo)
        param_layout.addRow("低频滤波比例:", self.lfctg_spin)
        param_layout.addRow("背景点数:", self.bac_num_spin)
        param_layout.addRow("分段数:", self.bac_split_spin)
        param_layout.addRow("SG滤波窗口:", self.window_spin)
        param_layout.addRow("多项式阶数:", self.polyorder_spin)
        param_layout.addRow("方差类型:", self.bac_var_combo)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.run_btn = self.create_push_button("开始处理")
        self.run_btn.clicked.connect(self._run_background_fit)

        self.save_btn = self.create_secondary_button("保存结果")
        self.save_btn.clicked.connect(self._save_results)
        self.save_btn.setEnabled(False)

        self.reset_btn = self.create_secondary_button("重置")
        self.reset_btn.clicked.connect(self._reset)

        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.reset_btn)

        layout.addLayout(btn_layout)

        return widget

    def _create_preview_section(self):
        """创建预览区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 预览标签
        preview_label = QLabel("数据预览")
        preview_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(preview_label)

        # 预览文本
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("加载数据后将显示预览...")
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

        # 日志标签
        log_label = QLabel("运行日志")
        log_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(log_label)

        # 日志文本
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("运行日志将显示在这里...")
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

    def _select_input_file(self):
        """选择输入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择XRD数据文件", "",
            "数据文件 (*.csv *.asc *.ras *.txt *.dat *.xrdml);;Rigaku ASC (*.asc);;Rigaku RAS (*.ras);;所有文件 (*.*)"
        )

        if file_path:
            self.input_file = file_path
            self.input_file_edit.setText(file_path)
            self._load_and_preview()

    def _load_and_preview(self):
        """加载并预览数据"""
        if not self.input_file:
            return

        # 验证文件
        valid, msg = validate_data_file(self.input_file)
        if not valid:
            show_error_message("文件错误", msg, self)
            return

        # 加载数据
        success, result = load_xrd_data(self.input_file)
        if not success:
            show_error_message("加载失败", result, self)
            return

        df = result

        # 预览
        preview = f"文件: {self.input_file}\n"
        preview += f"数据点数: {len(df)}\n"
        preview += f"2θ范围: {df['two_theta'].min():.2f} - {df['two_theta'].max():.2f}\n"
        preview += f"强度范围: {df['intensity'].min():.2f} - {df['intensity'].max():.2f}\n"
        preview += "\n前5行数据:\n"
        preview += df.head().to_string()

        self.preview_text.setText(preview)
        self.log(f"已加载数据文件: {self.input_file}")

    def _run_background_fit(self):
        """运行背景扣除"""
        if not self.input_file:
            show_error_message("错误", "请先选择输入文件", self)
            return

        if not self.WPEM:
            show_error_message("错误", "PyXplore库未加载", self)
            return

        self.run_btn.setEnabled(False)
        self.log("开始背景扣除处理...")

        try:
            # 加载数据
            success, df = load_xrd_data(self.input_file)
            if not success:
                raise Exception(df)

            # 准备参数
            params = {
                'intensity_csv': df,
                'LFctg': self.lfctg_spin.value(),
                'bac_num': self.bac_num_spin.value(),
                'bac_split': self.bac_split_spin.value(),
                'window_length': self.window_spin.value(),
                'polyorder': self.polyorder_spin.value(),
                'poly_n': 6,
                'bac_var_type': self.bac_var_combo.currentText(),
                'Model': self.spectrum_type_combo.currentText(),
            }

            # 调用PyXplore
            self.background_std = self.WPEM.BackgroundFit(**params)

            self.log("背景扣除完成!")
            self.log(f"背景标准差: {self.background_std:.4f}")

            # 启用保存按钮
            self.save_btn.setEnabled(True)

            show_info_message("完成", "背景扣除处理完成!", self)

        except Exception as e:
            self.log(f"错误: {str(e)}")
            show_error_message("处理失败", str(e), self)

        finally:
            self.run_btn.setEnabled(True)

    def _save_results(self):
        """保存结果"""
        output_dir = self.get_output_dir()
        output_dir = output_dir / "background"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存去背景数据
        no_bac_file = output_dir / "no_bac_intensity.csv"
        bac_file = output_dir / "bac.csv"

        # 从PyXplore输出目录复制
        source_dir = Path("ConvertedDocuments")

        if source_dir.exists():
            import shutil

            src_no_bac = source_dir / "no_bac_intensity.csv"
            src_bac = source_dir / "bac.csv"

            if src_no_bac.exists():
                shutil.copy(src_no_bac, no_bac_file)
            if src_bac.exists():
                shutil.copy(src_bac, bac_file)

            self.log(f"结果已保存到: {output_dir}")
            show_info_message("保存成功", f"结果已保存到:\n{output_dir}", self)
        else:
            show_error_message("错误", "找不到输出文件", self)

    def _reset(self):
        """重置"""
        self.input_file = ""
        self.input_file_edit.clear()
        self.preview_text.clear()
        self.log_text.clear()
        self.save_btn.setEnabled(False)
        self.background_std = None
        self.log("已重置")

    def log(self, message):
        """添加日志"""
        self.log_text.append(f"> {message}")
