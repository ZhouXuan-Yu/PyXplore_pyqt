# -*- coding: utf-8 -*-
"""
历史记录页面
"""

import json, datetime, subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt
from ...base_page import BasePage
from ...config import OUTPUT_DIR


class HistoryPage(BasePage):
    """历史记录页面"""

    def __init__(self, main_window=None):
        super().__init__(main_window)

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = self.create_title_label("History Records")
        layout.addWidget(title)

        # 历史记录表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Time", "Type", "Files", "Success", "Output Directory"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(1, 120)
        self.history_table.setColumnWidth(2, 60)
        self.history_table.setColumnWidth(3, 60)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.itemDoubleClicked.connect(self._open_history_dir)
        layout.addWidget(self.history_table)

        # 按钮区域
        btn_layout = QHBoxLayout()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)

        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self._clear_history)

        open_dir_btn = QPushButton("Open Output Directory")
        open_dir_btn.clicked.connect(self._open_output_dir)

        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(open_dir_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # 加载历史记录
        self._load_history()

    def _get_history_file(self):
        """获取历史记录文件路径"""
        return OUTPUT_DIR / "batch_history.json"

    def _load_history(self):
        """从JSON加载历史记录"""
        hist_file = self._get_history_file()
        if hist_file.exists():
            try:
                with open(hist_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                self._refresh_history_table(records)
            except Exception:
                self._refresh_history_table([])
        else:
            self._refresh_history_table([])

    def _refresh_history_table(self, records):
        """刷新历史记录表格"""
        self.history_table.setRowCount(len(records))
        for i, rec in enumerate(records):
            self.history_table.setItem(i, 0, QTableWidgetItem(rec.get("time", "")))
            self.history_table.setItem(i, 1, QTableWidgetItem(rec.get("mode", "")))
            self.history_table.setItem(i, 2, QTableWidgetItem(str(rec.get("total", ""))))
            self.history_table.setItem(i, 3, QTableWidgetItem(str(rec.get("success", ""))))
            dir_item = QTableWidgetItem(rec.get("base_dir", ""))
            dir_item.setForeground(Qt.darkBlue)
            self.history_table.setItem(i, 4, dir_item)

    def _refresh(self):
        """刷新历史记录"""
        self._load_history()

    def _clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(
            self, "Confirm", "Are you sure you want to clear all history records?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            hist_file = self._get_history_file()
            if hist_file.exists():
                hist_file.unlink()
            self.history_table.setRowCount(0)

    def _open_history_dir(self, item):
        """双击历史记录打开对应目录"""
        row = item.row()
        dir_col = self.history_table.item(row, 4)
        if dir_col and dir_col.text():
            try:
                subprocess.Popen(['explorer', dir_col.text()])
            except Exception:
                pass

    def _open_output_dir(self):
        """打开输出根目录"""
        try:
            subprocess.Popen(['explorer', str(OUTPUT_DIR)])
        except Exception:
            pass
