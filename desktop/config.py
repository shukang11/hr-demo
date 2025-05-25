"""
桌面应用配置文件
"""

import os
from pathlib import Path


class DesktopConfig:
    """桌面应用配置"""

    # 应用基础信息
    APP_NAME = "HR管理系统"
    APP_VERSION = "1.0.0"

    # 服务器配置
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5000

    # 窗口配置
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600

    # 路径配置
    BASE_DIR = Path(__file__).parent
    STATIC_DIR = BASE_DIR / "static"
    API_DIR = BASE_DIR.parent / "api"

    # 数据库配置（桌面版使用本地SQLite）
    DATABASE_PATH = BASE_DIR / "data" / "hr_desktop.db"

    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        cls.STATIC_DIR.mkdir(exist_ok=True)
        cls.DATABASE_PATH.parent.mkdir(exist_ok=True)
