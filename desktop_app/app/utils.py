# -*- coding: utf-8 -*-
"""
工具函数模块
提供通用工具函数
"""

import os
import sys
import json
import logging
import re
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
from .config import PROJECT_ROOT, OUTPUT_DIR


def setup_logger(name, log_file=None, level=logging.INFO):
    """设置日志记录器"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_project_logger(module_name):
    """获取项目日志记录器"""
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"{module_name}_{datetime.now().strftime('%Y%m%d')}.log"
    return setup_logger(module_name, str(log_file))


def validate_file_exists(file_path):
    """验证文件是否存在"""
    if not file_path:
        return False, "未选择文件"

    path = Path(file_path)
    if not path.exists():
        return False, f"文件不存在: {file_path}"

    return True, ""


def validate_cif_file(file_path):
    """验证CIF文件"""
    valid, msg = validate_file_exists(file_path)
    if not valid:
        return False, msg

    path = Path(file_path)
    if path.suffix.lower() not in ['.cif', '.CIF']:
        return False, f"不是CIF文件: {path.suffix}"

    return True, ""


def validate_data_file(file_path):
    """验证数据文件"""
    valid, msg = validate_file_exists(file_path)
    if not valid:
        return False, msg

    path = Path(file_path)
    suf = path.suffix.lower()
    if suf == ".raw":
        return (
            False,
            ".raw 是仪器原始二进制文件，PyXplore Desktop 无法直接读取。"
            "请在 PDXL / SmartLab 中将该测量另存为 *.asc 或两列 CSV，再导入。",
        )
    if suf == ".ras":
        # .ras 已有 _load_rigaku_ras() 完整支持，正常放行
        return True, ""
    if suf not in [".csv", ".txt", ".dat", ".xrdml", ".asc", ".ras"]:
        return False, f"不支持的文件格式: {path.suffix}"

    return True, ""


def load_csv_data(file_path, has_header=True):
    """加载CSV数据"""
    try:
        if has_header:
            df = pd.read_csv(file_path)
        else:
            df = pd.read_csv(file_path, header=None)

        # 转换为numpy数组
        data = df.values
        return True, data, df.columns.tolist()

    except Exception as e:
        return False, str(e), []


def save_csv_data(file_path, data, columns=None):
    """保存CSV数据"""
    try:
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(file_path, index=False)
        return True, ""

    except Exception as e:
        return False, str(e)


def _load_rigaku_ras(file_path):
    """
    读取理学 RAS 格式（SmartLab 等仪器导出）：
    数据位于 *RAS_INT_START ... *RAS_INT_END 之间，三列格式
    "2theta intensity weight"，取前两列。
    """
    try:
        text = Path(file_path).read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return False, f"读取 RAS 文件失败: {e}"

    lines = text.splitlines()
    in_data = False
    rows = []
    for line in lines:
        if "*RAS_INT_START" in line:
            in_data = True
            continue
        if "*RAS_INT_END" in line:
            break
        if not in_data:
            continue
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                rows.append([float(parts[0]), float(parts[1])])
            except ValueError:
                continue

    if not rows:
        return False, "RAS 文件中未找到强度数据（*RAS_INT_START / *RAS_INT_END 区域）"

    df = pd.DataFrame(rows, columns=["two_theta", "intensity"])
    return True, df


def _load_rigaku_smartlab_asc(file_path):
    """
    读取理学 SmartLab 导出的 ASCII（*.asc）：根据 *START/*STOP/*STEP/*COUNT 与数据区生成两列。
    """
    text = Path(file_path).read_text(encoding="utf-8", errors="replace")
    start = stop = step = None
    count = None
    for line in text.splitlines():
        if re.match(r"^\*START\s*=", line):
            start = float(line.split("=", 1)[1].strip())
        elif re.match(r"^\*STOP\s*=", line):
            stop = float(line.split("=", 1)[1].strip())
        elif re.match(r"^\*STEP\s*=", line):
            step = float(line.split("=", 1)[1].strip())
        elif re.match(r"^\*COUNT\s*=", line):
            count = int(float(line.split("=", 1)[1].strip()))

    if start is None or stop is None or count is None:
        return False, "不是可识别的 Rigaku ASC（需含 *START、*STOP、*COUNT 等标记）"

    in_data = False
    vals = []
    for line in text.splitlines():
        if re.match(r"^\*COUNT\s*=", line):
            in_data = True
            continue
        if not in_data:
            continue
        if line.startswith("*"):
            if line.strip() == "*END":
                break
            continue
        for m in re.findall(
            r"-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", line
        ):
            vals.append(float(m))

    n = min(len(vals), count)
    if n == 0:
        return False, "Rigaku ASC 中未解析到强度数据"
    vals = vals[:n]
    two_theta = np.linspace(start, stop, n)
    df = pd.DataFrame({"two_theta": two_theta, "intensity": vals})
    return True, df


def load_xrd_data(file_path):
    """加载XRD数据文件"""
    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if suffix == '.csv':
            df = pd.read_csv(file_path, header=None, names=['two_theta', 'intensity'])
        elif suffix == ".asc":
            return _load_rigaku_smartlab_asc(file_path)
        elif suffix == ".ras":
            return _load_rigaku_ras(file_path)
        elif suffix == '.dat':
            digital_pattern = re.compile(r'[0-9.]+')
            intensity = []

            with open(file_path, 'r') as xrdfid:
                first_line = xrdfid.readline()
                tmp_list = digital_pattern.findall(first_line)

                if len(tmp_list) >= 3:
                    start = float(tmp_list[0])
                    step = float(tmp_list[1])

                    while tmp_list:
                        tmp_list = digital_pattern.findall(xrdfid.readline())
                        for i in tmp_list:
                            try:
                                intensity.append(float(i))
                            except ValueError:
                                pass

                    two_theta = np.arange(start, start + step * len(intensity), step)
                    df = pd.DataFrame({'two_theta': two_theta[:len(intensity)], 'intensity': intensity})
                else:
                    return False, "无效的DAT文件格式"
        else:
            return False, f"不支持的文件格式: {suffix}"

        return True, df

    except Exception as e:
        return False, str(e)


def generate_output_filename(prefix, extension='csv', timestamp=True):
    """生成输出文件名"""
    if timestamp:
        time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{time_str}.{extension}"
    else:
        return f"{prefix}.{extension}"


def get_output_path(prefix, extension='csv', subdir=None):
    """获取输出文件路径"""
    if subdir:
        output_dir = OUTPUT_DIR / subdir
    else:
        output_dir = OUTPUT_DIR

    output_dir.mkdir(exist_ok=True)

    filename = generate_output_filename(prefix, extension)
    return output_dir / filename


def show_info_message(title, message, parent=None):
    """显示信息对话框"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def show_error_message(title, message, parent=None):
    """显示错误对话框"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def show_warning_message(title, message, parent=None):
    """显示警告对话框"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def show_question_message(title, message, parent=None):
    """显示确认对话框，返回True或False"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    return msg.exec_() == QMessageBox.Yes


def select_file(title, file_filter="所有文件 (*.*)", parent=None):
    """选择文件对话框"""
    file_path, _ = QFileDialog.getOpenFileName(parent, title, "", file_filter)
    return file_path


def select_files(title, file_filter="所有文件 (*.*)", parent=None):
    """选择多个文件对话框"""
    file_paths, _ = QFileDialog.getOpenFileNames(parent, title, "", file_filter)
    return file_paths


def select_directory(title, parent=None):
    """选择目录对话框"""
    dir_path = QFileDialog.getExistingDirectory(parent, title)
    return dir_path


def save_file_dialog(title, default_name="", file_filter="所有文件 (*.*)", parent=None):
    """保存文件对话框"""
    file_path, _ = QFileDialog.getSaveFileName(
        parent, title, default_name, file_filter
    )
    return file_path


def format_number(value, decimals=4):
    """格式化数字"""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_list(items, max_display=5):
    """格式化列表显示"""
    if not items:
        return "无"

    if len(items) <= max_display:
        return ", ".join(str(item) for item in items)

    return ", ".join(str(item) for item in items[:max_display]) + "..."


def parse_2theta_range(text):
    """解析2theta范围文本"""
    try:
        parts = text.replace(',', ' ').split()
        if len(parts) >= 2:
            return float(parts[0]), float(parts[1])
    except Exception:
        pass
    return None, None


def parse_lattice_constants(text):
    """解析晶格常数文本"""
    try:
        parts = text.replace(',', ' ').split()
        if len(parts) >= 6:
            return [float(p) for p in parts[:6]]
    except Exception:
        pass
    return None


def dict_to_json(data, file_path):
    """字典转JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, ""
    except Exception as e:
        return False, str(e)


def json_to_dict(file_path):
    """JSON文件转字典"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return True, data
    except Exception as e:
        return False, str(e)


def import_pyXplore():
    """Import PyXplore library from src directory as a package"""
    try:
        import sys
        from pathlib import Path

        # Get the project root
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        # Import as src.WPEM module (relative import)
        import src.WPEM as WPEM
        return True, WPEM
    except ModuleNotFoundError as e:
        # Check if it's a missing dependency
        missing_module = str(e).replace("No module named ", "").strip("'\"")
        return False, f"Missing dependency: {missing_module}. Please install it."
    except Exception as e:
        return False, str(e)
