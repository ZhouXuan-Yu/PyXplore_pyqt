# -*- coding: utf-8 -*-
"""
基础页面类
所有功能模块页面的基类
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .config import COLORS, FONTS


class BasePage(QWidget):
    """基础页面类"""

    # 信号：开始处理时发出
    processing_started = pyqtSignal()
    # 信号：处理完成时发出
    processing_finished = pyqtSignal(bool, str)
    # 信号：更新日志时发出
    log_updated = pyqtSignal(str)

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.logger = None
        self.WPEM = None

        # 初始化
        self._init_logger()
        self._init_wpem()
        self._init_ui()

    def _init_logger(self):
        """初始化日志记录器"""
        if self.main_window:
            self.logger = self.main_window.logger

    def _init_wpem(self):
        """初始化PyXplore库"""
        if self.main_window:
            self.WPEM = self.main_window.get_wpem()

    def _init_ui(self):
        """初始化UI - 子类实现"""
        raise NotImplementedError("子类必须实现 _init_ui 方法")

    def record_operation_history(self, mode, base_dir, total=1, success=1, files=None):
        """
        写入一条操作历史（与批量处理共用 batch_history.json）。
        各功能模块在成功完成主要计算后调用。
        """
        from .utils import append_desktop_history

        append_desktop_history(
            mode,
            base_dir,
            total=total,
            success=success,
            files=files,
        )

    def create_title_label(self, text):
        """创建标题标签"""
        label = QLabel(text)
        font = QFont()
        font.setPointSize(FONTS["title"]["size"])
        font.setBold(FONTS["title"]["bold"])
        label.setFont(font)
        label.setStyleSheet(f"color: {COLORS['text']}; margin: 10px 0;")
        return label

    def create_section_group(self, title):
        """创建分组框"""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        return group

    def create_form_layout(self):
        """创建表单布局"""
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setFormAlignment(Qt.AlignLeft)
        layout.setSpacing(10)
        return layout

    def create_button_layout(self, buttons=None):
        """创建按钮布局"""
        layout = QHBoxLayout()
        layout.addStretch()

        if buttons:
            for btn in buttons:
                layout.addWidget(btn)

        return layout

    def create_push_button(self, text, handler=None):
        """创建按钮"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary']};
            }}
            QPushButton:disabled {{
                background-color: #ccc;
            }}
        """)
        if handler:
            btn.clicked.connect(handler)
        return btn

    def create_secondary_button(self, text, handler=None):
        """创建次要按钮"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: {COLORS['primary']};
                border: 1px solid {COLORS['primary']};
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #f0f0f0;
            }}
        """)
        if handler:
            btn.clicked.connect(handler)
        return btn

    def log(self, message):
        """记录日志"""
        if self.logger:
            self.logger.info(message)
        self.log_updated.emit(message)

    def show_error(self, title, message):
        """显示错误"""
        from .utils import show_error_message
        show_error_message(title, message, self)

    def show_info(self, title, message):
        """显示信息"""
        from .utils import show_info_message
        show_info_message(title, message, self)

    def get_output_dir(self):
        """获取输出目录"""
        from .config import OUTPUT_DIR
        return OUTPUT_DIR
