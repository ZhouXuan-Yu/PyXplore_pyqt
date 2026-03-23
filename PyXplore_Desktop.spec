# -*- coding: utf-8 -*-
"""
PyXplore Desktop - PyInstaller Build Specification
打包目标: dist\PyXplore_Desktop\  可直接双击运行，无需目标机器安装任何依赖

已知问题：
- CPU 不支持 AVX/AVX2，TensorFlow 的 .pyd 加载会崩溃（exit code 3221225477）
- 解决方案：
  1. PYI_DISABLE_ANALYSIS_SUBPROCESS=1 阻止子进程分析二进制依赖
  2. 完全排除 tensorflow/keras/m3gnet 相关的动态分析（它们只在 src/Extinction/ 可选使用）
  3. desktop_app 不使用 TensorFlow，打包时排除不影响功能
"""

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import glob

# ==================== 必须在所有 PyInstaller 导入之前设置 ====================
# CPU 不支持 AVX/AVX2，禁用二进制分析的子进程模式
# 原因：TensorFlow .pyd 加载需要 AVX，子进程加载时会崩溃（exit code 3221225477）
# 注意：此变量必须在 import PyInstaller 之前设置才生效
os.environ.setdefault("PYI_DISABLE_ANALYSIS_SUBPROCESS", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

block_cipher = None

# ==================== 路径配置 ====================
ROOT_DIR = Path(__file__).parent.resolve() if "__file__" in dir() else Path.cwd().resolve()
DESKTOP_APP_DIR = ROOT_DIR / "desktop_app"
SRC_DIR = ROOT_DIR / "src"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

# ==================== 辅助函数 ====================

def _venv_site_packages():
    """返回 venv_build 的 site-packages 路径"""
    for parent in (ROOT_DIR / "venv_build", ROOT_DIR / "venv_build" / "Lib"):
        sp = parent / "Lib" / "site-packages"
        if sp.exists():
            return sp
        pyver = f"python{sys.version_info.major}{sys.version_info.minor}"
        sp2 = parent / pyver / "site-packages"
        if sp2.exists():
            return sp2
    return None

def _collect_vc_redist_binaries():
    """收集 Visual C++ Redistributable DLL"""
    vc_dlls = []
    search_dirs = [
        str(ROOT_DIR / "venv_build"),
        os.environ.get("SYSTEMROOT", "C:\\Windows") + "\\System32",
    ]
    dll_patterns = [
        "vcruntime140*.dll", "vcruntime140_1*.dll",
        "msvcp140*.dll", "msvcp140_1*.dll", "msvcp140_2*.dll",
        "concrt140.dll", "vccorlib140.dll",
        "mkl_intel_thread*.dll", "mkl_core*.dll", "mkl_blas*.dll",
        "libiomp5md.dll", "tbb*.dll",
    ]
    found = set()
    for d in search_dirs:
        if not d or not Path(d).exists():
            continue
        for pat in dll_patterns:
            for dll in glob.glob(os.path.join(d, pat)):
                key = Path(dll).name.lower()
                if key not in found:
                    found.add(key)
                    vc_dlls.append((dll, "."))
    return vc_dlls

# ==================== 收集依赖 ====================
sp = _venv_site_packages()

pyqt5_datas = collect_data_files("PyQt5")
pyqt5_qt_datas = collect_data_files("PyQt5.Qt")
pyqt5_plugins_datas = collect_data_files("PyQt5.QtPlugins")

mpl_datas = collect_data_files("matplotlib")
mpl_mpl_data = collect_data_files("matplotlib.mpl-data")

numpy_datas = collect_data_files("numpy")
numpy_mkl_datas = []
if sp:
    for mkl_pat in [
        sp / "numpy" / "mkl_common" / "*.dll",
        sp / "numpy" / "_mkl__init__*.pyd",
    ]:
        for dll in glob.glob(str(mkl_pat)):
            base = Path(dll).name
            if not any(base in str(x) for x in numpy_mkl_datas):
                numpy_mkl_datas.append((dll, "numpy"))

pymatgen_datas = collect_data_files("pymatgen")
# 手动指定 pymatgen 子模块，避免 collect_submodules 触发 TensorFlow
pymatgen_core_imports = [
    "pymatgen", "pymatgen.core", "pymatgen.core.structure", "pymatgen.core.lattice",
    "pymatgen.core.operations", "pymatgen.core.periodic_table", "pymatgen.core.composition",
    "pymatgen.core.interface", "pymatgen.core.interface_ctx",
    "pymatgen.io", "pymatgen.io.cif", "pymatgen.io.vasp", "pymatgen.io.ase",
    "pymatgen.util", "pymatgen.symmetry", "pymatgen.symmetry.analyzer",
    "pymatgen.applications", "pymatgen.analysis", "pymatgen.analysis.diffraction",
]

scipy_datas = collect_data_files("scipy")

sklearn_datas = collect_data_files("sklearn")
sklearn_binaries = []
if sp:
    for dll in glob.glob(str(sp / "sklearn" / ".libs" / "*.dll")):
        sklearn_binaries.append((dll, "sklearn/.libs"))

h5py_datas = collect_data_files("h5py")
h5py_binaries = []
if sp:
    for dll in glob.glob(str(sp / "h5py" / ".libs" / "*.dll")):
        h5py_binaries.append((dll, "h5py/.libs"))

plotly_datas = collect_data_files("plotly")
kaleido_datas = collect_data_files("kaleido")

ase_datas = collect_data_files("ase")
ase_binaries = []
if sp:
    for dll in glob.glob(str(sp / "ase" / ".libs" / "*.dll")):
        ase_binaries.append((dll, "ase/.libs"))

lxml_datas = collect_data_files("lxml")
PIL_datas = collect_data_files("PIL")

# TensorFlow 不打包：CPU 不支持 AVX，子进程加载 .pyd 会崩溃
# desktop_app 不使用 TensorFlow，M3GNet 弛豫功能可选
tensorflow_datas = collect_data_files("tensorflow")

vc_redist_binaries = _collect_vc_redist_binaries()

# ==================== 隐藏导入（不包含 tensorflow/keras/m3gnet） ====================
hiddenimports = [
    # PyQt5
    "PyQt5", "PyQt5.Qt", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets", "PyQt5.sip",
    # NumPy
    "numpy", "numpy.core", "numpy.core._multiarray_umath",
    "numpy.linalg._umath_linalg", "numpy.linalg._blas",
    "numpy.fft._pocketfft", "numpy.random._common", "numpy.random._bounded_integers",
    "numpy.random._mt19937", "numpy.random._philox", "numpy.random._pcg64",
    "numpy.random._sfc64",
    # SciPy
    "scipy", "scipy.special", "scipy.special._orthogonal", "scipy.special.wofz",
    "scipy.special.spherical_jn", "scipy.linalg", "scipy.linalg._fblas",
    "scipy.linalg._flapack", "scipy.integrate", "scipy.optimize", "scipy.interpolate",
    "scipy.optimize._trlib", "scipy.optimize._lbfgsb", "scipy.optimize._cobyla",
    "scipy.signal", "scipy.signal._sigtools", "scipy.stats",
    # Matplotlib
    "matplotlib", "matplotlib.backends", "matplotlib.backends.backend_qt5agg",
    "matplotlib.backends.backend_agg", "mpl_toolkits.mplot3d", "mpl_toolkits.mplot3d.art3d",
    "matplotlib.figure", "matplotlib.pyplot", "matplotlib.cm", "matplotlib.colors",
    "matplotlib.ticker", "matplotlib.legend", "matplotlib.transforms", "matplotlib.patches",
    "matplotlib.path", "matplotlib.collections", "matplotlib.markers", "matplotlib.lines",
    "matplotlib.text", "matplotlib.container", "matplotlib.style", "matplotlib.gridspec",
    "matplotlib.axis", "matplotlib.projections", "matplotlib.projections.polar",
    "matplotlib.animation", "matplotlib.widgets",
    # Pandas
    "pandas", "pandas._libs.tslibs.timestamps", "pandas._libs.tslibs.np_datetime",
    "pandas._libs.hashtable", "pandas._libs.lib", "pandas._libs.missing",
    "pandas._libs.arrays", "pandas._libs.window", "pandas._libs.parsers",
    "pandas._libs.join", "pandas.core.arrays", "pandas.core.frame",
    "pandas.core.series", "pandas.core.indexing", "pandas.core.reshape",
    # SymPy
    "sympy", "sympy.core", "sympy.core.symbol", "sympy.core.numbers", "sympy.core.arith",
    "sympy.functions", "sympy.functions.elementary", "sympy.functions.special",
    "sympy.logic", "sympy.polys", "sympy.plotting", "sympy.printing", "sympy.utilities",
    # pymatgen（手动指定，避免 collect_submodules 触发 TensorFlow）
    *pymatgen_core_imports,
    # spglib
    "spglib", "spglib.utils",
    # scikit-learn
    "sklearn", "sklearn.utils", "sklearn.tree", "sklearn.ensemble",
    "sklearn.linear_model", "sklearn.metrics", "sklearn.preprocessing",
    "sklearn.gaussian_process", "sklearn.model_selection", "sklearn.decomposition",
    "sklearn.cluster",
    # PyWavelets
    "PyWavelets", "pywt",
    # ASE
    "ase", "ase.io", "ase.io.vasp", "ase.atoms", "ase.calculators",
    "ase.constraints", "ase.optimize", "ase.md",
    # h5py
    "h5py", "h5py._errors", "h5py._objects", "h5py._sync",
    # plotly / kaleido
    "plotly", "plotly.graph_objects", "plotly.subplots", "plotly.io",
    "plotly.express", "kaleido",
    # tqdm / monty
    "tqdm", "tqdm.auto", "tqdm.utils", "monty", "monty.json", "monty.os",
    # image / IO
    "PIL", "PIL.Image", "PIL._imaging", "PIL._imagingtk",
    "skimage", "skimage.transform", "skimage.filters",
    "lxml", "lxml.etree", "lxml.objectify",
    # standard library
    "unittest", "unittest.mock",
    "xml.etree.ElementTree", "json", "threading", "queue",
    "datetime", "weakref", "gc", "ctypes", "struct", "pickle",
    "copy", "inspect", "pathlib", "shutil", "warnings", "platform",
    "subprocess", "concurrent.futures", "tempfile", "io", "hashlib",
    "urllib", "urllib.request", "urllib.error", "fnmatch", "glob",
    "re", "math", "csv", "logging", "textwrap",
]

# 仓库内计算核心包 src（排除 Extinction 目录，因为其中的 Relaxer.py 顶层导入 m3gnet）
try:
    _syspath_root = str(ROOT_DIR)
    if _syspath_root not in sys.path:
        sys.path.insert(0, _syspath_root)
    _src_mods = collect_submodules(
        "src",
        filter=lambda n: (
            ".tests" not in n
            and not n.endswith(".tests")
            # 排除 Extinction 目录：其中的 Relaxer.py 顶层导入 m3gnet → tensorflow → 崩溃
            and not n.startswith("src.Extinction")
        ),
    )
    hiddenimports.extend(_src_mods)
except Exception as _exc:
    print(f"[spec] collect_submodules('src'): {_exc}")
    hiddenimports.extend(["src", "src.WPEM"])

# 手动添加 src.Extinction 中不涉及 TensorFlow 的模块（XRDpre.py 本身不导入 tensorflow）
hiddenimports += [
    "src.Extinction.XRDpre",
    "src.Extinction.CifReader",
    "src.Extinction.wyckoff",
]

# 去重（保持顺序）
seen, unique_hidden = [], []
for h in hiddenimports:
    if h not in seen:
        seen.append(h)
        unique_hidden.append(h)
hiddenimports = unique_hidden

# ==================== 数据文件 ====================
datas = [
    *pyqt5_datas, *pyqt5_qt_datas, *pyqt5_plugins_datas,
    *mpl_datas, *mpl_mpl_data,
    *numpy_datas,
    *pymatgen_datas,
    *scipy_datas, *sklearn_datas,
    *h5py_datas,
    *plotly_datas, *kaleido_datas,
    *ase_datas,
    *lxml_datas, *PIL_datas,
    *tensorflow_datas,
    (str(SRC_DIR), "src"),
    (str(DESKTOP_APP_DIR / "resources"), "resources"),
]

# ==================== 二进制文件 ====================
binaries = [
    *numpy_mkl_datas,
    *sklearn_binaries,
    *h5py_binaries,
    *ase_binaries,
    *vc_redist_binaries,
]

# ==================== 排除模块 ======================
excludes = [
    "pytest", "doctest", "test",
    "sphinx", "sphinxcontrib", "readme", "docs",
    "IPython", "jupyter", "notebook", "nbconvert",
    "fonttools",
    "PySide2", "PySide6",
    # 排除 tensorflow/keras 相关，避免 PyInstaller 分析时崩溃
    # desktop_app 不使用，src.Extinction 的 TensorFlow 功能可选
    "tensorflow", "keras",
]

# ==================== 运行时钩子 ====================
_rthooks_dir = ROOT_DIR / "PyInstaller" / "rthooks"
_rthooks_dir.mkdir(parents=True, exist_ok=True)

_runtime_hook_content = (
    "import sys\n"
    "import os\n"
    "from pathlib import Path\n"
    "\n"
    "meipass = getattr(sys, '_MEIPASS', None)\n"
    "if meipass:\n"
    "    meipass_path = Path(meipass)\n"
    "    if str(meipass_path) not in sys.path:\n"
    "        sys.path.insert(0, str(meipass_path))\n"
    "    internal = meipass_path / '_internal'\n"
    "    if internal.exists() and str(internal) not in sys.path:\n"
    "        sys.path.insert(0, str(internal))\n"
    "    exe_dir = Path(sys.executable).parent\n"
    "    if str(exe_dir) not in sys.path:\n"
    "        sys.path.insert(0, str(exe_dir))\n"
    "\n"
    "    os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')\n"
    "    os.environ.setdefault('TF_ENABLE_ONEDNN_OPTS', '0')\n"
)

_runtime_hook_file = _rthooks_dir / "pysrc_hook.py"
_runtime_hook_file.write_text(_runtime_hook_content, encoding="utf-8")

runtime_hooks = [str(_runtime_hook_file)]

# ==================== 分析选项 ====================
DIST_DIR.mkdir(exist_ok=True)
BUILD_DIR.mkdir(exist_ok=True)

a = Analysis(
    [str(DESKTOP_APP_DIR / "main.py")],
    pathex=[
        str(ROOT_DIR),
        str(DESKTOP_APP_DIR),
        str(SRC_DIR),
        str(ROOT_DIR / "venv_build"),
        str(ROOT_DIR / "venv_build" / "Library" / "bin"),
    ],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=None,
    hooksconfig={},
    runtime_hooks=runtime_hooks,
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name=APP_NAME.replace(" ", "_"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version=None,
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME.replace(" ", "_"),
)
