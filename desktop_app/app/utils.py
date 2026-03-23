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


# 桌面端历史记录（与旧版 batch_history.json 兼容，现亦写入单功能模块操作）
DESKTOP_HISTORY_FILENAME = "batch_history.json"
MAX_DESKTOP_HISTORY_RECORDS = 100


def get_desktop_history_path():
    """历史记录 JSON 路径（位于 OUTPUT_DIR）"""
    return OUTPUT_DIR / DESKTOP_HISTORY_FILENAME


def append_desktop_history(mode, base_dir, total=1, success=1, files=None):
    """
    追加一条桌面操作历史（新记录在前），供「历史记录」页展示。

    :param mode: 类型描述（如「批量背景扣除」「XRD精修」）
    :param base_dir: 输出/工作目录（str 或 Path）
    :param total: 任务涉及文件数或子任务数
    :param success: 成功数量
    :param files: 可选，相关输入文件路径列表
    """
    hist_file = get_desktop_history_path()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if hist_file.exists():
        try:
            with open(hist_file, "r", encoding="utf-8") as f:
                records = json.load(f)
            if not isinstance(records, list):
                records = []
        except Exception:
            records = []
    else:
        records = []

    file_list = None
    if files is not None:
        file_list = [str(Path(f)) for f in files if f]

    records.insert(
        0,
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": str(mode),
            "total": int(total),
            "success": int(success),
            "base_dir": str(Path(base_dir)) if base_dir else "",
            "files": file_list,
        },
    )
    records = records[:MAX_DESKTOP_HISTORY_RECORDS]
    with open(hist_file, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


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


def _iter_frozen_bundle_roots():
    """
    PyInstaller 运行时可能的路径根（须包含小写包目录 src/）。
    - onedir：通常 _MEIPASS 与 exe 所在目录相同
    - 部分环境依赖会放在 exe 同级的 _internal/
    """
    roots = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        roots.append(Path(meipass))
    exe_dir = Path(sys.executable).resolve().parent
    roots.append(exe_dir)
    internal = exe_dir / "_internal"
    if internal.is_dir():
        roots.append(internal)
    seen, out = set(), []
    for r in roots:
        try:
            key = str(r.resolve())
        except OSError:
            key = str(r)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def import_pyXplore():
    """
    加载 PyWPEM 计算核心。

    必须通过 **大小写一致** 的包名 ``src.WPEM`` 导入（对应仓库 ``src/WPEM.py``）。
    在 Linux/macOS 上 ``Src`` / ``wpem`` 等错误大小写会导致导入失败。
    """
    import importlib

    try:
        if getattr(sys, "frozen", False):
            chosen = None
            for root in _iter_frozen_bundle_roots():
                # 必须存在 src/WPEM.py；包目录名须为小写 src（与 import 语句一致）
                candidate = root / "src" / "WPEM.py"
                if candidate.is_file():
                    chosen = root
                    break
            if chosen is None:
                searched = ", ".join(str(r) for r in _iter_frozen_bundle_roots())
                return (
                    False,
                    "未找到 src/WPEM.py。已搜索: "
                    + searched
                    + "。请确认 PyInstaller spec 的 datas 含 (SRC_DIR, \"src\")，且文件夹名为小写 src。",
                )
            root_s = str(chosen.resolve())
            if root_s not in sys.path:
                sys.path.insert(0, root_s)
            importlib.invalidate_caches()
            import src.WPEM as WPEM  # noqa: F401

            return True, WPEM

        # 开发环境：仓库根目录（含包 src/）须在 sys.path
        project_root = Path(__file__).resolve().parent.parent.parent
        pr = str(project_root)
        if pr not in sys.path:
            sys.path.insert(0, pr)
        dev_wpem = project_root / "src" / "WPEM.py"
        if not dev_wpem.is_file():
            return (
                False,
                f"开发环境未找到 {dev_wpem}（请从仓库根目录运行，且勿改动 src/WPEM.py 大小写）。",
            )
        importlib.invalidate_caches()
        import src.WPEM as WPEM  # noqa: F401

        return True, WPEM
    except ModuleNotFoundError as e:
        missing_module = str(e).replace("No module named ", "").strip("'\"")
        return (
            False,
            f"导入 src.WPEM 时缺少模块: {missing_module}。"
            f"请 pip 安装依赖；若已打包请在 spec 的 hiddenimports 中补充。原始信息: {e}",
        )
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def format_wpem_missing_message(widget):
    """
    WPEM 未就绪时的用户提示（含底层异常，便于区分「找不到 src」与「缺依赖」）。
    """
    mw = getattr(widget, "main_window", None) if widget is not None else None
    detail = getattr(mw, "wpem_import_error", None) if mw else None
    lines = [
        "未能加载核心计算库。",
        "说明：桌面端名称「PyXplore」仅为产品名；计算代码即本仓库中的 Python 包 src.WPEM（路径 src/WPEM.py），",
        "并非单独的 pip 包「PyXplore」。",
        "若使用打包版，请确认程序目录下存在文件夹 src 且内含 WPEM.py（大小写与仓库一致）。",
    ]
    if detail:
        lines.extend(["", "加载失败详情：", str(detail)])
    return "\n".join(lines)
