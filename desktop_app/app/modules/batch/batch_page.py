# -*- coding: utf-8 -*-
"""
批量处理模块页面
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QProgressBar, QComboBox, QGroupBox, QFormLayout,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from ...base_page import BasePage
from ...config import OUTPUT_DIR, DEFAULT_PARAMS, SPECTRUM_TYPES, BAC_VAR_TYPES
from ...utils import (
    select_files,
    select_directory,
    show_error_message,
    show_info_message,
    load_xrd_data,
    append_desktop_history,
    format_wpem_missing_message,
)


class BatchWorker(QThread):
    """批量处理工作线程"""
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    file_done = pyqtSignal(int, str, str)  # (row_index, status, result_dir)

    def __init__(self, files, mode, params, WPEM, base_output_dir=None):
        super().__init__()
        self.files = files
        self.mode = mode
        self.params = params
        self.WPEM = WPEM
        self.base_output_dir = Path(base_output_dir) if base_output_dir else OUTPUT_DIR
        self._stop = False

    def run(self):
        try:
            total = len(self.files)
            for i, f in enumerate(self.files):
                if self._stop:
                    return
                self.progress.emit(int((i + 1) / total * 100))

                fname = Path(f)
                fname_stem = fname.stem
                work_dir = str(self.base_output_dir / fname_stem)
                Path(work_dir).mkdir(parents=True, exist_ok=True)

                # 标记处理中
                self.file_done.emit(i, "处理中", "")

                if self.mode == "批量背景扣除":
                    self.log.emit(f"处理: {fname.name}  →  {fname_stem}/")
                    ok, df_or_msg = load_xrd_data(f)
                    if not ok:
                        self.log.emit(f"  [跳过] {fname.name}: {df_or_msg}")
                        self.file_done.emit(i, "跳过", "")
                        continue
                    params = {
                        'intensity_csv': df_or_msg,
                        'LFctg': self.params.get('LFctg', 0.5),
                        'bac_num': self.params.get('bac_num', None),
                        'bac_split': self.params.get('bac_split', 5),
                        'window_length': self.params.get('window_length', 17),
                        'polyorder': self.params.get('polyorder', 3),
                        'poly_n': self.params.get('poly_n', 6),
                        'bac_var_type': self.params.get('bac_var_type', 'constant'),
                        'Model': self.params.get('Model', 'XRD'),
                        'work_dir': work_dir,
                    }
                    self.WPEM.BackgroundFit(**params)
                    self.log.emit(f"  完成: {fname_stem}/")
                    self.file_done.emit(i, "完成", work_dir)

                elif self.mode == "批量CIF预处理":
                    self.log.emit(f"解析: {fname.name}")
                    self.WPEM.CIFpreprocess(
                        filepath=str(fname),
                        work_dir=str(Path(work_dir) / "CIFpreprocess"),
                    )
                    self.file_done.emit(i, "完成", work_dir)

                elif self.mode == "批量XRD模拟":
                    self.log.emit(f"模拟: {fname.name}")
                    self.WPEM.XRDsimulate(
                        filepath=str(fname),
                        work_dir=str(Path(work_dir) / "XRDsimulate"),
                    )
                    self.file_done.emit(i, "完成", work_dir)

            if not self._stop:
                self.finished.emit(True, "批量处理完成")
        except Exception as e:
            # 发生异常时标记当前行为失败
            self.file_done.emit(i, "失败", "")
            self.finished.emit(False, str(e))

    def stop(self):
        self._stop = True


class BatchPage(BasePage):
    """批量处理页面"""

    def __init__(self, main_window=None):
        self.file_list = []
        self.worker = None
        super().__init__(main_window)

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = self.create_title_label("批量处理")
        layout.addWidget(title)

        # 模式选择
        mode_group = self.create_section_group("处理模式")
        mode_layout = QHBoxLayout()

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "批量背景扣除",
            "批量CIF预处理",
            "批量XRD模拟"
        ])

        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)

        mode_layout.addWidget(QLabel("处理类型:"))
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # 批量输出目录
        out_group = self.create_section_group("输出设置")
        out_layout = QHBoxLayout()
        self.out_dir_edit = QLineEdit()
        self.out_dir_edit.setReadOnly(True)
        self.out_dir_edit.setText(str(OUTPUT_DIR))
        out_dir_btn = QPushButton("浏览...")
        out_dir_btn.clicked.connect(self._select_output_dir)
        out_layout.addWidget(QLabel("输出目录:"))
        out_layout.addWidget(self.out_dir_edit, 1)
        out_layout.addWidget(out_dir_btn)
        out_group.setLayout(out_layout)
        layout.addWidget(out_group)

        # 参数设置（批量背景扣除）
        self.batch_param_group = self.create_section_group("参数设置")
        self.batch_param_layout = QFormLayout()

        self.batch_model_combo = QComboBox()
        self.batch_model_combo.addItems(SPECTRUM_TYPES)
        self.batch_model_combo.setCurrentText("XRD")

        self.batch_lfctg_spin = QDoubleSpinBox()
        self.batch_lfctg_spin.setRange(0.01, 1.0)
        self.batch_lfctg_spin.setValue(DEFAULT_PARAMS["background"]["LFctg"])
        self.batch_lfctg_spin.setSingleStep(0.05)
        self.batch_lfctg_spin.setDecimals(2)

        self.batch_bac_num_spin = QSpinBox()
        self.batch_bac_num_spin.setRange(10, 1000)
        self.batch_bac_num_spin.setValue(100)

        self.batch_bac_split_spin = QSpinBox()
        self.batch_bac_split_spin.setRange(2, 20)
        self.batch_bac_split_spin.setValue(DEFAULT_PARAMS["background"]["bac_split"])

        self.batch_window_spin = QSpinBox()
        self.batch_window_spin.setRange(5, 51)
        self.batch_window_spin.setValue(DEFAULT_PARAMS["background"]["window_length"])
        self.batch_window_spin.setSingleStep(2)

        self.batch_polyorder_spin = QSpinBox()
        self.batch_polyorder_spin.setRange(1, 10)
        self.batch_polyorder_spin.setValue(DEFAULT_PARAMS["background"]["polyorder"])

        self.batch_bac_var_combo = QComboBox()
        self.batch_bac_var_combo.addItems(BAC_VAR_TYPES)

        self.batch_param_layout.addRow("谱图类型:", self.batch_model_combo)
        self.batch_param_layout.addRow("低频滤波比例:", self.batch_lfctg_spin)
        self.batch_param_layout.addRow("背景点数:", self.batch_bac_num_spin)
        self.batch_param_layout.addRow("分段数:", self.batch_bac_split_spin)
        self.batch_param_layout.addRow("SG滤波窗口:", self.batch_window_spin)
        self.batch_param_layout.addRow("多项式阶数:", self.batch_polyorder_spin)
        self.batch_param_layout.addRow("方差类型:", self.batch_bac_var_combo)

        self.batch_param_group.setLayout(self.batch_param_layout)
        layout.addWidget(self.batch_param_group)

        # 绑定模式切换事件（放在参数组创建之后）
        self._on_mode_changed(0)

        # 文件列表
        file_group = self.create_section_group("文件列表")
        file_layout = QVBoxLayout()

        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(["文件名", "路径", "状态", "结果目录"])
        self.file_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.file_table.setColumnWidth(2, 80)   # 状态列稍窄
        self.file_table.setColumnWidth(3, 200)  # 结果目录列宽一些
        file_layout.addWidget(self.file_table)

        btn_layout = QHBoxLayout()

        add_btn = QPushButton("添加文件")
        add_btn.clicked.connect(self._add_files)

        add_dir_btn = QPushButton("从目录添加")
        add_dir_btn.clicked.connect(self._add_from_directory)

        clear_btn = QPushButton("清空列表")
        clear_btn.clicked.connect(self._clear_files)

        remove_btn = QPushButton("移除选中")
        remove_btn.clicked.connect(self._remove_selected)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(add_dir_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()

        file_layout.addLayout(btn_layout)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # 日志
        log_group = self.create_section_group("处理日志")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
                min-height: 150px;
            }
        """)
        log_layout.addWidget(self.log_text)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 按钮
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.start_btn = self.create_push_button("开始批量处理")
        self.start_btn.clicked.connect(self._start_batch)

        self.stop_btn = self.create_secondary_button("停止")
        self.stop_btn.clicked.connect(self._stop_batch)
        self.stop_btn.setEnabled(False)

        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.stop_btn)

        layout.addLayout(action_layout)

    def _add_files(self):
        """添加文件"""
        mode = self.mode_combo.currentIndex()
        if mode == 0:
            filter_str = "数据文件 (*.csv *.asc *.ras *.txt *.dat *.xrdml);;Rigaku ASC (*.asc);;Rigaku RAS (*.ras);;所有文件 (*.*)"
        elif mode == 1:
            filter_str = "CIF文件 (*.cif);;所有文件 (*.*)"
        else:
            filter_str = "CIF文件 (*.cif);;所有文件 (*.*)"

        files, _ = QFileDialog.getOpenFileNames(self, "选择文件", "", filter_str)

        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                self._add_file_to_table(f)

    def _add_from_directory(self):
        """从目录添加"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if not dir_path:
            return

        mode = self.mode_combo.currentIndex()
        if mode == 0:
            patterns = ["*.csv", "*.asc", "*.ras", "*.txt", "*.dat", "*.xrdml"]
        else:
            patterns = ["*.cif"]

        import glob
        for pattern in patterns:
            for f in Path(dir_path).glob(pattern):
                if str(f) not in self.file_list:
                    self.file_list.append(str(f))
                    self._add_file_to_table(str(f))

    def _add_file_to_table(self, file_path):
        """添加文件到表格"""
        path = Path(file_path)
        row = self.file_table.rowCount()
        self.file_table.insertRow(row)
        self.file_table.setItem(row, 0, QTableWidgetItem(path.name))
        self.file_table.setItem(row, 1, QTableWidgetItem(file_path))
        status_item = QTableWidgetItem("等待处理")
        status_item.setToolTip("等待处理")
        self.file_table.setItem(row, 2, status_item)
        self.file_table.setItem(row, 3, QTableWidgetItem(""))

    def _on_file_done(self, row, status, result_dir):
        """单个文件处理完成回调"""
        if row < self.file_table.rowCount():
            item = QTableWidgetItem(status)
            if status == "完成":
                item.setForeground(Qt.darkGreen)
                item.setToolTip(result_dir)
            elif status == "跳过":
                item.setForeground(Qt.darkYellow)
            elif status == "处理中":
                item.setForeground(Qt.blue)
            elif status == "失败":
                item.setForeground(Qt.red)
            self.file_table.setItem(row, 2, item)
            if result_dir:
                dir_item = QTableWidgetItem(result_dir)
                dir_item.setForeground(Qt.darkBlue)
                self.file_table.setItem(row, 3, dir_item)

    def _clear_files(self):
        """清空文件列表"""
        self.file_list.clear()
        self.file_table.setRowCount(0)

    def _remove_selected(self):
        """移除选中项"""
        selected = self.file_table.currentRow()
        if selected >= 0:
            self.file_list.pop(selected)
            self.file_table.removeRow(selected)

    def _select_output_dir(self):
        """选择批量输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录", str(OUTPUT_DIR))
        if dir_path:
            self.out_dir_edit.setText(dir_path)

    def _on_mode_changed(self, index):
        """模式切换时显示/隐藏参数区"""
        self.batch_param_group.setVisible(index == 0)

    def _collect_params(self):
        """收集当前页面参数"""
        mode = self.mode_combo.currentIndex()
        if mode == 0:
            return {
                'LFctg': self.batch_lfctg_spin.value(),
                'bac_num': self.batch_bac_num_spin.value(),
                'bac_split': self.batch_bac_split_spin.value(),
                'window_length': self.batch_window_spin.value(),
                'polyorder': self.batch_polyorder_spin.value(),
                'poly_n': 6,
                'bac_var_type': self.batch_bac_var_combo.currentText(),
                'Model': self.batch_model_combo.currentText(),
            }
        return {}

    def _start_batch(self):
        """开始批量处理"""
        if not self.file_list:
            show_error_message("错误", "请先添加文件", self)
            return

        if not self.WPEM:
            show_error_message("错误", format_wpem_missing_message(self), self)
            return

        mode = self.mode_combo.currentText()
        self.log(f"开始{mode}...")

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # 收集参数
        params = self._collect_params()

        # 创建工作线程
        # 在主线程先切换 Matplotlib 后端为 Agg，避免子线程中 plt.show() 卡死
        import matplotlib
        matplotlib.use('Agg')

        self.worker = BatchWorker(
            self.file_list,
            self.mode_combo.currentText(),
            params,
            self.WPEM,
            base_output_dir=self.out_dir_edit.text(),
        )

        self.worker.progress.connect(self._on_progress)
        self.worker.log.connect(self._on_log)
        self.worker.finished.connect(self._on_finished)
        self.worker.file_done.connect(self._on_file_done)

        self.worker.start()

    def _stop_batch(self):
        """停止批量处理"""
        if self.worker:
            self.worker.stop()
            self.log("批量处理已停止")

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _on_progress(self, value):
        """进度更新"""
        self.progress_bar.setValue(value)

    def _on_log(self, message):
        """日志更新"""
        self.log_text.append(f"> {message}")

    def _on_finished(self, success, message):
        """处理完成"""
        # 统计成功数，写入历史文件
        success_count = sum(
            1 for r in range(self.file_table.rowCount())
            if self.file_table.item(r, 2).text() == "完成"
        )
        append_desktop_history(
            self.mode_combo.currentText(),
            self.out_dir_edit.text(),
            total=len(self.file_list),
            success=success_count,
            files=self.file_list,
        )

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)

        if success:
            self.log(f"批量处理完成! ({success_count}/{len(self.file_list)} 成功)")
            show_info_message("完成", f"批量处理完成!\n{success_count}/{len(self.file_list)} 成功", self)
        else:
            self.log(f"错误: {message}")
            show_error_message("错误", message, self)

    def log(self, message):
        self.log_text.append(f"> {message}")