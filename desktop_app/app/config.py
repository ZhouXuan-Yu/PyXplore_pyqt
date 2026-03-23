# PyXplore Desktop 配置文件

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 源代码路径
SRC_PATH = PROJECT_ROOT.parent / "src"

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 临时目录
TEMP_DIR = PROJECT_ROOT / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# 支持的X射线波长
XRAY_WAVELENGTHS = {
    "CuKa": 1.54184,
    "CuKa1": 1.540593,
    "CuKa2": 1.544414,
    "CuKb1": 1.39222,
    "MoKa": 0.71073,
    "MoKa1": 0.70930,
    "MoKa2": 0.71359,
    "MoKb1": 0.63229,
    "CoKa": 1.79026,
    "CoKa1": 1.78896,
    "CoKa2": 1.79285,
    "CoKb1": 1.63079,
    "CrKa": 2.29100,
    "CrKa1": 2.28970,
    "CrKa2": 2.29361,
    "CrKb1": 2.08487,
    "FeKa": 1.93735,
    "FeKa1": 1.93604,
    "FeKa2": 1.93998,
    "FeKb1": 1.75661,
    "AgKa": 0.560885,
    "AgKa1": 0.559421,
    "AgKa2": 0.563813,
    "AgKb1": 0.497082,
}

# 支持的光谱类型
SPECTRUM_TYPES = ["XRD", "Raman", "XPS"]

# 支持的背景方差类型
BAC_VAR_TYPES = ["constant", "polynomial", "multivariate gaussian"]

# 默认参数
DEFAULT_PARAMS = {
    "background": {
        "LFctg": 0.5,
        "bac_split": 5,
        "window_length": 17,
        "polyorder": 3,
        "poly_n": 6,
    },
    "cif_preprocess": {
        "wavelength": "CuKa",
        "two_theta_range": (10, 90),
        "show_unitcell": False,
        "cal_extinction": True,
    },
    "xrd_simulation": {
        "wavelength": "CuKa",
        "two_theta_range": (10, 90, 0.01),
        "SuperCell": False,
        "PeriodicArr": [3, 3, 3],
        "PeakWidth": True,
    },
    "xrd_refinement": {
        "bta": 0.8,
        "bta_threshold": 0.5,
        "iter_max": 40,
        "cpu": 4,
    },
    "amorphous": {
        "mix_component": 3,
        "sigma2_coef": 0.5,
        "max_iter": 5000,
    },
    "xps": {
        "bta": 0.8,
        "iter_max": 40,
    },
    "exafs": {
        "power": 2,
        "distance": 5,
        "k_point": 8,
    },
}

# 界面颜色配置
COLORS = {
    "primary": "#1E3A5F",      # 深蓝 - 主色调
    "secondary": "#4A90D9",   # 浅蓝 - 次要色
    "accent": "#FF8C00",      # 橙色 - 强调色
    "background": "#F5F5F5",  # 浅灰 - 背景色
    "text": "#333333",        # 深灰 - 文字色
    "success": "#28A745",     # 绿色 - 成功色
    "error": "#DC3545",      # 红色 - 错误色
    "warning": "#FFC107",     # 黄色 - 警告色
}

# 字体配置
FONTS = {
    "title": {"size": 14, "bold": True},
    "body": {"size": 12, "bold": False},
    "caption": {"size": 10, "bold": False},
}
