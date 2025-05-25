"""
HR-Demo 桌面应用启动器
使用 PyWebView 将 Flask 应用嵌入到桌面窗口中
"""

import webview
import threading
import sys
import os
from pathlib import Path
from waitress import serve
import logging

# 添加 API 路径到 Python 路径
api_path = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_path))

from config import DesktopConfig


class DesktopApp:
    def __init__(self):
        self.flask_app = None
        self.server_thread = None
        self._setup_logging()

    def _setup_logging(self):
        """配置桌面应用日志"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def start_flask_server(self):
        """在后台线程启动 Flask 服务器"""
        try:
            # 导入并创建Flask应用
            from app import create_app

            self.flask_app = create_app(desktop_mode=True)

            # 确保必要的目录存在
            DesktopConfig.ensure_directories()

            # 使用 waitress 作为 WSGI 服务器
            self.logger.info(
                f"启动Flask服务器 {DesktopConfig.SERVER_HOST}:{DesktopConfig.SERVER_PORT}"
            )
            serve(
                self.flask_app,
                host=DesktopConfig.SERVER_HOST,
                port=DesktopConfig.SERVER_PORT,
                threads=4,
            )
        except Exception as e:
            self.logger.error(f"Flask 服务器启动失败: {e}")
            import traceback

            self.logger.error(traceback.format_exc())
            sys.exit(1)

    def wait_for_server(self):
        """等待Flask服务器启动"""
        import socket
        import time

        max_attempts = 30
        attempt = 0
        while attempt < max_attempts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(
                    (DesktopConfig.SERVER_HOST, DesktopConfig.SERVER_PORT)
                )
                sock.close()
                if result == 0:
                    self.logger.info("Flask服务器已启动")
                    return True
            except Exception:
                pass
            attempt += 1
            time.sleep(0.5)

        self.logger.error("Flask服务器启动超时")
        return False

    def run(self):
        """启动桌面应用"""
        self.logger.info(f"启动 {DesktopConfig.APP_NAME} v{DesktopConfig.APP_VERSION}")

        # 在后台线程启动 Flask 服务器
        self.server_thread = threading.Thread(
            target=self.start_flask_server, daemon=True
        )
        self.server_thread.start()

        # 等待服务器启动
        if not self.wait_for_server():
            sys.exit(1)

        # 在主线程创建并启动 PyWebView 窗口
        try:
            window = webview.create_window(
                title=DesktopConfig.APP_NAME,
                url=f"http://{DesktopConfig.SERVER_HOST}:{DesktopConfig.SERVER_PORT}",
                width=DesktopConfig.WINDOW_WIDTH,
                height=DesktopConfig.WINDOW_HEIGHT,
                min_size=(
                    DesktopConfig.WINDOW_MIN_WIDTH,
                    DesktopConfig.WINDOW_MIN_HEIGHT,
                ),
                resizable=True,
                shadow=True,
                on_top=False,
            )
            webview.start(debug=False)
        except Exception as e:
            self.logger.error(f"桌面应用启动失败: {e}")
            sys.exit(1)


if __name__ == "__main__":
    app = DesktopApp()
    app.run()
