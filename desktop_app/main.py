# PyXplore Desktop - 应用入口

import sys
import os
from pathlib import Path

# 添加src目录到Python路径，以便导入PyXplore库
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

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
