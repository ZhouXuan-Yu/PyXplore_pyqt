#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyXplore Desktop - 构建脚本（跨平台）

使用方法:
    python build.py              # 执行完整打包
    python build.py clean        # 仅清理构建目录
    python build.py rebuild       # 强制重新打包
    python build.py check        # 检查依赖是否完整
    python build.py install-deps # 仅安装依赖
"""

import sys
import os
import subprocess
import shutil
import argparse
from pathlib import Path

# ==================== 配置 ====================
ROOT_DIR = Path(__file__).parent
DESKTOP_APP_DIR = ROOT_DIR / "desktop_app"
SRC_DIR = ROOT_DIR / "src"
SPEC_FILE = ROOT_DIR / "PyXplore_Desktop.spec"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

# 依赖列表
REQUIRED_PACKAGES = [
    "PyQt5>=5.15.0",
    "numpy>=1.21.0",
    "scipy>=1.7.0",
    "matplotlib>=3.4.0",
    "pandas>=1.3.0",
    "sympy>=1.8.0",
    "scikit-learn>=0.24.0",
    "PyWavelets>=1.3.0",
    "tqdm>=4.62.0",
    "plotly>=5.0.0",
    "monty>=2.0.0",
    "pymatgen>=2020.0.0",
    "ase>=3.20.0",
    "pyinstaller>=5.0",
]


def run_cmd(cmd, check=True, capture=False):
    """运行命令并输出"""
    print(f"    $ {' '.join(str(c) for c in cmd)}")
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"    [失败] {result.stderr}")
            sys.exit(1)
        return result
    else:
        result = subprocess.run(cmd)
        if check and result.returncode != 0:
            sys.exit(1)
        return result


def check_python():
    """检查 Python 版本"""
    print("[1/5] 检查 Python 环境...")
    version = sys.version_info
    print(f"    Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("    [错误] 需要 Python 3.8+")
        sys.exit(1)
    print("    Python OK")


def check_dependencies():
    """检查并安装依赖"""
    print("\n[2/5] 检查依赖...")

    missing = []
    for pkg in REQUIRED_PACKAGES:
        name = pkg.split(">")[0].split("=")[0].strip()
        try:
            __import__(name)
            print(f"    {name:30s} OK")
        except ImportError:
            print(f"    {name:30s} 缺失")
            missing.append(pkg)

    if missing:
        print(f"\n    发现 {len(missing)} 个缺失依赖，正在安装...")
        for pkg in missing:
            print(f"    安装: {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

    # 单独检查 PyInstaller
    try:
        import PyInstaller
        print(f"    PyInstaller OK")
    except ImportError:
        print(f"    PyInstaller 缺失，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def clean():
    """清理构建目录"""
    print("\n[清理] 删除旧构建目录...")

    for path in [DIST_DIR, BUILD_DIR]:
        if path.exists():
            print(f"    删除: {path}")
            shutil.rmtree(path, ignore_errors=True)

    # 删除 .spec 自动生成的 build/ dist/（如果在根目录）
    for name in ["build", "dist"]:
        p = ROOT_DIR / name
        if p.exists():
            print(f"    删除: {p}")
            shutil.rmtree(p, ignore_errors=True)

    # 清理 __pycache__
    for p in ROOT_DIR.rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)
    for p in ROOT_DIR.rglob("*.pyc"):
        p.unlink(missing_ok=True)

    print("    清理完成!")


def prebuild_check():
    """构建前检查"""
    print("\n[3/5] 构建前检查...")

    # 检查 spec 文件
    if not SPEC_FILE.exists():
        print(f"    [错误] 未找到 spec 文件: {SPEC_FILE}")
        print("    请确认 PyXplore_Desktop.spec 存在于项目根目录")
        sys.exit(1)
    print(f"    spec 文件: {SPEC_FILE}")

    # 检查入口文件
    main_py = DESKTOP_APP_DIR / "main.py"
    if not main_py.exists():
        print(f"    [错误] 未找到入口文件: {main_py}")
        sys.exit(1)
    print(f"    入口文件: {main_py}")

    # 检查 src 目录
    if not SRC_DIR.exists():
        print(f"    [错误] 未找到源码目录: {SRC_DIR}")
        sys.exit(1)
    print(f"    源码目录: {SRC_DIR}")

    print("    检查完成!")


def build(mode="build", clean_first=True):
    """执行打包"""
    print("\n[4/5] 开始打包...")

    if clean_first:
        clean()

    print(f"    模式: {mode}")
    print(f"    spec: {SPEC_FILE}")

    # 切换到项目根目录执行
    old_cwd = os.getcwd()
    try:
        os.chdir(ROOT_DIR)

        cmd = [sys.executable, "-m", "PyInstaller", str(SPEC_FILE), "--clean", "--noconfirm"]

        if mode == "onefile":
            cmd.append("--onefile")
        elif mode == "onedir":
            cmd.append("--onedir")

        print(f"    运行: {' '.join(str(c) for c in cmd)}")
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print("\n    [错误] 打包失败!")
            print("    常见问题排查:")
            print("      1. 内存不足 → 关闭其他程序或使用 --onedir 模式")
            print("      2. 权限不足 → 以管理员身份运行")
            print("      3. 缺少依赖 → 运行 python build.py install-deps")
            sys.exit(1)

    finally:
        os.chdir(old_cwd)

    print("    打包完成!")


def postbuild():
    """构建后处理"""
    print("\n[5/5] 构建后处理...")

    # 查找生成的 exe
    exe_name = "PyXplore_Desktop"
    dist_exe = DIST_DIR / exe_name / f"{exe_name}.exe"

    if dist_exe.exists():
        size_mb = dist_exe.stat().st_size / (1024 * 1024)
        print(f"    可执行文件: {dist_exe}")
        print(f"    文件大小: {size_mb:.1f} MB")
    else:
        # 可能生成了单文件模式
        possible = list(DIST_DIR.glob(f"{exe_name}*/*.exe")) + list(DIST_DIR.glob(f"{exe_name}*.exe"))
        if possible:
            print(f"    可执行文件: {possible[0]}")
        else:
            print("    [警告] 未找到 .exe 文件")

    # 检查 output 目录是否在 dist 中
    output_in_dist = DIST_DIR / exe_name / "output"
    if not output_in_dist.exists():
        print(f"    创建输出目录: {output_in_dist}")
        output_in_dist.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("  打包成功!")
    print("=" * 60)
    print(f"\n  输出目录: {DIST_DIR / exe_name}")
    print(f"\n  运行方式:")
    print(f"    双击运行: {dist_exe}")
    print(f"  或在终端:  {dist_exe}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="PyXplore Desktop 构建脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python build.py              完整打包
  python build.py clean         仅清理
  python build.py rebuild       强制重新打包
  python build.py onefile       单文件打包
  python build.py check         检查依赖
  python build.py install-deps  仅安装依赖
        """
    )
    parser.add_argument("mode", nargs="?", default="build",
                        choices=["build", "clean", "rebuild", "onefile", "onedir", "check", "install-deps"],
                        help="构建模式 (默认: build)")
    parser.add_argument("--no-clean", action="store_true",
                        help="跳过清理步骤")
    parser.add_argument("--keep-cache", action="store_true",
                        help="保留 PyInstaller 缓存")

    args = parser.parse_args()

    mode = args.mode

    # 打印横幅
    print("\n" + "=" * 60)
    print("  PyXplore Desktop - Build Script")
    print("=" * 60)
    print(f"  模式: {mode}")
    print(f"  Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print()

    if mode == "clean":
        clean()
        return

    if mode == "check":
        check_python()
        check_dependencies()
        prebuild_check()
        print("\n    所有检查通过!")
        return

    if mode == "install-deps":
        check_dependencies()
        print("\n    依赖安装完成!")
        return

    # 构建模式
    check_python()
    check_dependencies()
    prebuild_check()
    build(mode=mode, clean_first=not args.no_clean and mode != "rebuild")
    postbuild()


if __name__ == "__main__":
    main()
