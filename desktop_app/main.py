# PyXplore Desktop - 应用入口

import sys
import os
from pathlib import Path

# ==================== PyInstaller 冻结环境适配 ====================
# 判断是否处于打包后的运行环境
if getattr(sys, 'frozen', False):
    # 打包后：_MEIPASS 下有 src/ 包（与仓库一致），需把 _MEIPASS 加入 path 才能 import src.WPEM
    BUNDLE_DIR = Path(sys._MEIPASS)
    if str(BUNDLE_DIR) not in sys.path:
        sys.path.insert(0, str(BUNDLE_DIR))
    APP_ROOT = Path(sys.executable).parent
else:
    # 开发调试环境
    BUNDLE_DIR = None
    # 须将「仓库根目录」加入 path，才能 import src.WPEM（包名为 src，不是把 src 目录本身当根）
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from app.main_window import MainWindow
from app.config import COMBO_BOX_STYLE


def main():
    """应用程序主入口"""
    # 创建应用实例
    app = QApplication(sys.argv)
    app.setApplicationName("PyXplore Desktop")
    app.setOrganizationName("PyXplore")
    app.setOrganizationDomain("github.com/Bin-Cao/PyWPEM")

    # 设置应用样式
    app.setStyle('Fusion')
    # 下拉列表选中项：绿色文字，避免白底白字
    app.setStyleSheet(COMBO_BOX_STYLE)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 进入事件循环
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
