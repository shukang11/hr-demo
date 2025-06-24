"""
桌面应用配置文件
"""

import sys
from pathlib import Path


class DesktopConfig:
    """桌面应用配置"""

    # 应用基础信息
    APP_NAME = "HR管理系统"
    APP_VERSION = "1.0.0"

    # 服务器配置
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5001

    # 窗口配置
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600

    # 路径配置
    # 检测是否在 PyInstaller 打包环境中运行
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # PyInstaller 环境：使用可执行文件所在目录
        BASE_DIR = Path(sys.executable).parent
        # 系统资源目录（只读）
        STATIC_DIR = BASE_DIR / "static"
        # 用户数据目录（可写）
        WORK_DIR = BASE_DIR / "data"
        LOGS_DIR = WORK_DIR / "logs"
        UPLOADS_DIR = WORK_DIR / "uploads"
        API_DIR = WORK_DIR / "api"  # API配置文件存放在用户数据区
    else:
        # 开发环境：使用脚本文件所在目录，保持原有结构
        BASE_DIR = Path(__file__).parent
        WORK_DIR = BASE_DIR
        STATIC_DIR = BASE_DIR / "static"
        API_DIR = BASE_DIR.parent / "api"
        LOGS_DIR = BASE_DIR / "logs"
        UPLOADS_DIR = BASE_DIR / "uploads"

    # 数据库配置（桌面版使用本地SQLite）
    # 无论开发还是打包环境，数据库都放在 data 目录下
    if getattr(sys, "frozen", False):
        DATABASE_PATH = WORK_DIR / "hr_desktop.db"
    else:
        DATABASE_PATH = BASE_DIR / "data" / "hr_desktop.db"

    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        # 用户数据目录
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

        # 在打包环境中，创建API目录用于存放配置文件
        if getattr(sys, "frozen", False):
            cls.API_DIR.mkdir(parents=True, exist_ok=True)

        # 注意：STATIC_DIR 是系统资源目录，不应该在运行时创建或修改
