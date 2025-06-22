"""
HR-Demo 桌面应用启动器
使用 PyWebView 将 Flask 应用嵌入到桌面窗口中
"""

import sys
import logging
import traceback
import time
import requests
import webview
import threading
from pathlib import Path
from waitress import serve  # 新增导入

# 添加 API 路径到 Python 路径
# 这行必须在尝试从 api 包导入任何内容之前
if getattr(sys, "frozen", False):
    # 打包环境：API代码已经被打包到可执行文件中
    # 但我们仍需要确保配置路径正确
    from config import DesktopConfig

    api_path = DesktopConfig.API_DIR
else:
    # 开发环境：使用相对路径
    api_path = Path(__file__).parent.parent / "api"

if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))

# --- 项目相关导入 ---
# 尝试将这些导入放在 sys.path 修改之后
from app import create_app  # type: ignore # noqa: E402

# 延迟导入模型，避免在 Flask 应用创建前初始化数据库模型
# from api.libs.models.account import AccountInDB  # noqa: E402
from extensions.ext_database import db  # db 是 SQLAlchemy 实例   # noqa: E402

# from api.services.account import AccountService  # noqa: E402
# from api.services.account._schema import AccountCreate, LoginRequest  # noqa: E402
from libs.helper import get_sha256  # noqa: E402

from config import DesktopConfig  # noqa: E402

# --- 默认凭据 ---
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD_PLAINTEXT = "admin123"
DEFAULT_EMAIL = "admin@example.com"


class DesktopApp:
    def __init__(self):
        # 在初始化时创建 Flask app 实例，以确保 app_context 在后续方法中可用
        self.flask_app = create_app(desktop_mode=True)
        self.server_thread = None
        self.window = None
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
            DesktopConfig.ensure_directories()
            self.logger.info(
                f"启动Flask服务器 {DesktopConfig.SERVER_HOST}:{DesktopConfig.SERVER_PORT}"
            )
            serve(
                self.flask_app,  # 使用 self.flask_app
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
        max_attempts = 30
        attempt = 0
        while attempt < max_attempts:
            try:
                response = requests.get(
                    f"http://{DesktopConfig.SERVER_HOST}:{DesktopConfig.SERVER_PORT}/api/health",
                    timeout=1,
                )
                if response.status_code == 200:
                    self.logger.info("Flask服务器已成功启动")
                    return True
            except requests.ConnectionError:
                self.logger.debug(
                    f"等待服务器启动... 尝试 {attempt + 1}/{max_attempts}"
                )
            except Exception as e:
                self.logger.warning(f"等待服务器时发生错误: {e}")
            attempt += 1
            time.sleep(0.5)

        self.logger.error("Flask服务器启动超时")
        return False

    def run(self):
        """启动桌面应用"""
        self.logger.info(f"启动 {DesktopConfig.APP_NAME} v{DesktopConfig.APP_VERSION}")

        # Flask app 实例已在 __init__ 中创建

        self.server_thread = threading.Thread(
            target=self.start_flask_server, daemon=True
        )
        self.server_thread.start()

        if not self.wait_for_server():
            self.logger.error("Flask 服务器启动失败. Exiting.")  # 添加日志
            sys.exit(1)

        jwt_token_for_frontend = self._ensure_default_user_and_get_token()

        try:
            self.logger.info("Creating PyWebView window...")

            # 创建窗口加载完成后的回调函数
            def on_window_loaded():
                if jwt_token_for_frontend:
                    self.logger.info(
                        "Window loaded, injecting JWT into frontend localStorage..."
                    )
                    try:
                        js_code = f"""
                            localStorage.setItem('jwt_token', '{jwt_token_for_frontend}');
                            localStorage.setItem('username', '{DEFAULT_USERNAME}');
                            console.log('JWT Token injected successfully');
                        """
                        self.window.evaluate_js(js_code)
                        self.logger.info("JWT injection completed")
                    except Exception as e:
                        self.logger.error(f"Failed to inject JWT: {e}")

            self.window = webview.create_window(
                title=DesktopConfig.APP_NAME,
                url=f"http://{DesktopConfig.SERVER_HOST}:{DesktopConfig.SERVER_PORT}",
                width=DesktopConfig.WINDOW_WIDTH,
                height=DesktopConfig.WINDOW_HEIGHT,
                min_size=(
                    DesktopConfig.WINDOW_MIN_WIDTH,
                    DesktopConfig.WINDOW_MIN_HEIGHT,
                ),
                resizable=getattr(DesktopConfig, "WINDOW_RESIZABLE", True),
                shadow=True,
                on_top=False,
            )

            self.logger.info("Starting PyWebView event loop...")
            webview.start(
                debug=getattr(DesktopConfig, "DEBUG", False), func=on_window_loaded
            )

        except Exception as e:
            self.logger.error(f"PyWebView 窗口创建或启动失败: {e}")  # 完善日志
            self.logger.error(traceback.format_exc())  # 记录完整堆栈
            sys.exit(1)  # 确保异常时退出

        self.logger.info("Application closed.")  # 添加日志

    def _ensure_default_user_and_get_token(self) -> str | None:
        """
        确保默认用户存在，如果不存在则创建，并为其生成 JWT。
        如果数据库非空或发生错误，则返回 None。
        """
        if not self.flask_app:
            self.logger.error("Flask app not initialized. Cannot ensure default user.")
            return None
        try:
            with self.flask_app.app_context():
                # 在 Flask 应用上下文中导入模型，避免重复定义表
                from libs.models.account import AccountInDB  # noqa: E402
                from services.account import AccountService  # noqa: E402
                from services.account._schema import AccountCreate, LoginRequest  # noqa: E402

                self.logger.info("Checking for existing users in the database...")
                if db.session.query(AccountInDB.id).first() is None:
                    self.logger.info(
                        f"No users found. Creating default user '{DEFAULT_USERNAME}'..."
                    )

                    hashed_password = get_sha256(DEFAULT_PASSWORD_PLAINTEXT)

                    account_data = AccountCreate(
                        username=DEFAULT_USERNAME,
                        email=DEFAULT_EMAIL,
                        password_hashed=hashed_password,
                    )

                    # AccountService 需要一个 SQLAlchemy Session, 而不是 scoped_session
                    # db.session 是一个 scoped_session，直接调用它会返回当前线程的 Session
                    account_service = AccountService(
                        session=db.session()
                    )  # 调用以获取实际 Session
                    created_account_schema = account_service.register_account(
                        account_data
                    )

                    if not created_account_schema:
                        self.logger.error(
                            f"Failed to register default user '{DEFAULT_USERNAME}'. Service returned None."
                        )
                        db.session.rollback()
                        return None

                    db.session.commit()
                    self.logger.info(
                        f"Default user '{DEFAULT_USERNAME}' (ID: {created_account_schema.id}) created successfully."
                    )
                    resp = account_service.process_login(
                        login_data=LoginRequest(
                            email=created_account_schema.email,
                            password_hashed=hashed_password,
                        )
                    )
                    return resp.token
                else:
                    self.logger.info(
                        "Users already exist in the database. Skipping default user creation and auto-login."
                    )
                    return None
        except Exception as e:
            self.logger.error(
                f"Error during default user initialization or token generation: {e}",
                exc_info=True,
            )
            if (
                hasattr(db, "session") and db.session.is_active
            ):  # 检查 db.session 是否存在且活跃
                db.session.rollback()
            return None


if __name__ == "__main__":
    app = DesktopApp()
    app.run()
