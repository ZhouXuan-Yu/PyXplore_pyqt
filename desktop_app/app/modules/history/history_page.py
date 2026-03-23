# -*- coding: utf-8 -*-
"""
历史记录页面
"""

import json
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QCheckBox,
)
from PyQt5.QtCore import Qt, QSettings, QFileSystemWatcher, QTimer

from ...base_page import BasePage
from ...config import OUTPUT_DIR
from ...utils import get_desktop_history_path


class HistoryPage(BasePage):
    """历史记录页面"""

    def __init__(self, main_window=None):
        self._hist_watcher = None
        self._reload_timer = None
        super().__init__(main_window)

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 标题行：左侧标题 + 右侧刷新
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title = self.create_title_label("History Records")
        title_row.addWidget(title)
        title_row.addStretch()

        self.top_refresh_btn = QPushButton("Refresh")
        self.top_refresh_btn.setToolTip("手动刷新历史列表")
        self.top_refresh_btn.clicked.connect(self._refresh)
        title_row.addWidget(self.top_refresh_btn)
        layout.addLayout(title_row)

        # 自动刷新：监听历史 JSON / 输出目录变化
        self._settings = QSettings("PyXplore", "PyXploreDesktop")
        self.auto_refresh_check = QCheckBox("自动刷新（监听历史文件变化）")
        self.auto_refresh_check.setChecked(
            self._settings.value("history/auto_refresh", True, type=bool)
        )
        self.auto_refresh_check.toggled.connect(self._on_auto_refresh_toggled)
        layout.addWidget(self.auto_refresh_check)

        self._reload_timer = QTimer(self)
        self._reload_timer.setSingleShot(True)
        self._reload_timer.setInterval(250)
        self._reload_timer.timeout.connect(self._load_history)

        self._hist_watcher = QFileSystemWatcher(self)
        self._hist_watcher.fileChanged.connect(self._on_fs_changed)
        self._hist_watcher.directoryChanged.connect(self._on_fs_changed)
        self._apply_auto_refresh_watcher()

        # 历史记录表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Time", "Type", "Files", "Success", "Output Directory"])
        # 避免路径被省略成 "D:..."：不用 Stretch 均分整表，输出列占剩余宽度并允许换行
        self.history_table.setTextElideMode(Qt.ElideNone)
        self.history_table.setWordWrap(True)
        hdr = self.history_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.Stretch)
        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(1, 140)
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
        return get_desktop_history_path()

    def _schedule_reload(self):
        """防抖刷新（避免短时间内多次写入触发多次读盘）"""
        if self.auto_refresh_check.isChecked() and self._reload_timer:
            self._reload_timer.start()

    def _on_fs_changed(self, _path=""):
        self._schedule_reload()

    def _on_auto_refresh_toggled(self, checked):
        self._settings.setValue("history/auto_refresh", checked)
        self._apply_auto_refresh_watcher()
        if checked:
            self._load_history()

    def _apply_auto_refresh_watcher(self):
        """根据设置挂载/卸载文件系统监视"""
        if not self._hist_watcher:
            return
        paths = self._hist_watcher.files() + self._hist_watcher.directories()
        for p in paths:
            self._hist_watcher.removePath(p)
        if not self.auto_refresh_check.isChecked():
            return
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        d = str(OUTPUT_DIR)
        if self._hist_watcher.addPath(d):
            pass
        hf = self._get_history_file()
        if hf.exists():
            self._hist_watcher.addPath(str(hf))

    def showEvent(self, event):
        super().showEvent(event)
        # 切换到本页时同步一次（防止漏监听到的事件）
        self._load_history()
        if self.auto_refresh_check.isChecked():
            self._apply_auto_refresh_watcher()

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
        # Windows：保存 JSON 后 QFileSystemWatcher 有时会丢失对文件的监视
        if self.auto_refresh_check.isChecked() and self._hist_watcher:
            hf = self._get_history_file()
            hs = str(hf)
            if hf.exists() and hs not in self._hist_watcher.files():
                self._hist_watcher.addPath(hs)

    def _refresh_history_table(self, records):
        """刷新历史记录表格"""
        self.history_table.setRowCount(len(records))
        for i, rec in enumerate(records):
            self.history_table.setItem(i, 0, QTableWidgetItem(rec.get("time", "")))
            self.history_table.setItem(i, 1, QTableWidgetItem(rec.get("mode", "")))
            self.history_table.setItem(i, 2, QTableWidgetItem(str(rec.get("total", ""))))
            self.history_table.setItem(i, 3, QTableWidgetItem(str(rec.get("success", ""))))
            path_str = rec.get("base_dir") or ""
            dir_item = QTableWidgetItem(str(path_str))
            dir_item.setForeground(Qt.darkBlue)
            dir_item.setToolTip(str(path_str))  # 悬停可见完整路径
            self.history_table.setItem(i, 4, dir_item)
        self.history_table.resizeRowsToContents()

    def _refresh(self):
        """刷新历史记录"""
        self._load_history()
        # Windows 上 JSON 改写后有时需重新监视该文件
        if self.auto_refresh_check.isChecked():
            self._apply_auto_refresh_watcher()

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
