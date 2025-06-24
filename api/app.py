import os
import sys
from pathlib import Path
from typing import Optional

from flask import Flask
from flask_cors import CORS

from configs import shared_config, AppConfig
from extensions import ext_database, ext_login, ext_migrate, ext_logging
from extensions.ext_database import db

if not shared_config.DEBUG:
    from gevent import monkey

    monkey.patch_all()
os.environ["TZ"] = "UTC"


def init_extensions(app: Flask) -> None:
    ext_database.init_app(app)
    ext_login.init_app(app)
    ext_logging.init_app(app)
    ext_migrate.init_app(app, db)


def auto_migrate_database(app: Flask) -> None:
    """自动运行数据库迁移（仅在开发环境和Web模式）"""
    # 桌面模式下跳过自动迁移，使用直接创建表的方式
    if app.config.get("DESKTOP_MODE", False):
        app.logger.info("桌面模式：跳过自动迁移，使用直接创建表")
        return

    if not app.config.get("AUTO_MIGRATE_DB", False):
        return

    if not app.config.get("DEBUG", False):
        app.logger.info("跳过自动迁移：非开发环境")
        return

    try:
        import flask_migrate
        # Path 已在顶部导入

        # 检查是否存在迁移文件夹
        migrations_path = Path(app.root_path) / "migrations"
        if not migrations_path.exists():
            app.logger.warning("迁移文件夹不存在，跳过自动迁移")
            return

        app.logger.info("开始自动数据库迁移...")

        # 在应用上下文中运行迁移
        with app.app_context():
            try:
                # 尝试运行迁移
                flask_migrate.upgrade()
                app.logger.info("数据库迁移完成")
            except Exception as upgrade_error:
                app.logger.warning(f"迁移升级失败: {upgrade_error}")
                # 如果迁移失败，可能是第一次运行，尝试初始化
                try:
                    flask_migrate.stamp()
                    app.logger.info("数据库迁移标记完成")
                except Exception as stamp_error:
                    app.logger.error(f"数据库迁移标记失败: {stamp_error}")

    except ImportError:
        app.logger.error("flask_migrate 未安装，无法自动迁移数据库")
    except Exception as e:
        app.logger.error(f"自动数据库迁移失败: {e}")


def register_blueprints(app: Flask) -> None:
    from routes import init_app as init_apis

    init_apis(app)
    return None


def register_commands(app) -> None:
    from commands import register_commands

    register_commands(app)


def create_app(
    specific_config: Optional[AppConfig] = None, desktop_mode: bool = False
) -> Flask:
    app = Flask(__name__)
    config = specific_config or shared_config

    # 首先设置基础配置
    app.config.from_object(config)

    if desktop_mode:
        # 桌面模式特殊配置
        # sys 和 Path 已在顶部导入

        # 设置桌面模式标志（必须在初始化扩展之前）
        app.config["DESKTOP_MODE"] = True

        # 检测是否在 PyInstaller 打包环境中运行
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            # PyInstaller 环境：使用可执行文件所在目录
            desktop_path = Path(sys.executable).parent
            # 系统资源目录（前端静态文件）
            static_path = desktop_path / "static"
            # 用户数据目录
            data_path = desktop_path / "data"
            print(f"[DEBUG] PyInstaller mode - executable path: {sys.executable}")
            print(f"[DEBUG] PyInstaller mode - desktop_path: {desktop_path}")
            print(f"[DEBUG] PyInstaller mode - static_path: {static_path}")
            print(f"[DEBUG] PyInstaller mode - data_path: {data_path}")
        else:
            # 开发环境：使用相对路径，保持原有结构
            desktop_path = Path(__file__).parent.parent / "desktop"
            static_path = desktop_path / "static"
            data_path = desktop_path / "data"
            print(f"[DEBUG] Development mode - desktop_path: {desktop_path}")
            print(f"[DEBUG] Development mode - static_path: {static_path}")
            print(f"[DEBUG] Development mode - data_path: {data_path}")

        # 配置静态文件路径
        print(f"[DEBUG] Static path: {static_path}")
        print(f"[DEBUG] Static path exists: {static_path.exists()}")

        # 检查关键文件是否存在
        index_html = static_path / "index.html"
        assets_dir = static_path / "assets"
        print(f"[DEBUG] index.html exists: {index_html.exists()}")
        print(f"[DEBUG] assets directory exists: {assets_dir.exists()}")

        if assets_dir.exists():
            assets_files = list(assets_dir.glob("*"))
            print(f"[DEBUG] Assets files count: {len(assets_files)}")
            if len(assets_files) > 0:
                print(
                    f"[DEBUG] Sample assets files: {[f.name for f in assets_files[:5]]}"
                )

        app.static_folder = str(static_path)
        app.static_url_path = ""

        # 确保数据目录存在
        try:
            data_path.mkdir(parents=True, exist_ok=True)
            print("[DEBUG] Successfully created/verified data directory")
        except Exception as e:
            print(f"[DEBUG] Failed to create data directory: {e}")

        # 检查静态文件目录（系统资源，应该已存在）
        if not static_path.exists():
            print(f"[DEBUG] Warning: Static directory does not exist: {static_path}")
        else:
            print(f"[DEBUG] Static directory found: {static_path}")
            import tempfile

            data_path = Path(tempfile.gettempdir()) / "hr_desktop_data"
            data_path.mkdir(exist_ok=True)
            print(f"[DEBUG] Using temp directory: {data_path}")

        desktop_db_path = data_path / "hr_desktop.db"
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{desktop_db_path}"

        # 桌面模式也需要CORS配置，因为浏览器仍会进行跨域检查
        CORS(
            app,
            origins=["http://localhost:5001", "http://127.0.0.1:5001"],
            allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
            methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            supports_credentials=True,
        )
        app.logger.info("桌面模式启动")
    else:
        # Web模式CORS配置
        CORS(
            app,
            origins=["http://localhost:1420", "http://127.0.0.1:1420"],
            allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
            methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            supports_credentials=True,
        )

    # 添加全局 OPTIONS 请求处理器
    # @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    # @app.route('/<path:path>', methods=['OPTIONS'])
    # def handle_options(path):
    #     response = make_response()
    #     response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    #     response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    #     response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    #     response.headers.add('Access-Control-Allow-Credentials', 'true')
    #     response.headers.add('Access-Control-Max-Age', '3600')
    #     return response

    # 设置 secret_key，这对于会话功能是必需的
    # 如果配置中已有密钥，则使用配置中的，否则生成一个随机密钥
    if not app.secret_key:
        app.secret_key = config.SECRET_KEY

    init_extensions(app)
    register_blueprints(app)
    register_commands(app)

    # 自动数据库迁移（仅在开发环境和Web模式）
    auto_migrate_database(app)

    # 桌面模式需要手动创建表
    if desktop_mode:
        with app.app_context():
            try:
                db.create_all()
                app.logger.info("桌面模式：数据库表创建完成")
            except Exception as e:
                app.logger.error(f"桌面模式：数据库表创建失败: {e}")

    # 桌面模式添加SPA路由支持
    if desktop_mode:

        @app.route("/")
        def serve_frontend():
            """服务前端应用"""
            try:
                return app.send_static_file("index.html")
            except Exception as e:
                app.logger.error(f"Failed to serve index.html: {e}")
                return f"Error serving frontend: {e}", 500

        @app.route("/<path:path>")
        def serve_static_files(path: str):
            """服务静态文件和SPA路由"""
            try:
                # 打印请求的文件路径用于调试
                app.logger.debug(f"Requesting static file: {path}")

                # 检查文件是否存在
                static_file_path = Path(app.static_folder) / path
                if static_file_path.exists():
                    app.logger.debug(f"Serving existing file: {path}")
                    return app.send_static_file(path)
                else:
                    app.logger.debug(
                        f"File not found, serving index.html for SPA route: {path}"
                    )
                    # 对于SPA路由，返回index.html
                    return app.send_static_file("index.html")
            except Exception as e:
                app.logger.error(f"Error serving static file {path}: {e}")
                return f"Error serving file {path}: {e}", 404

    return app


# 只在Web模式下创建默认app实例
# 桌面模式下应该明确调用 create_app(desktop_mode=True)
if __name__ != "__main__":
    # 如果是被其他模块导入，则不自动创建app实例
    # 让调用方明确指定参数
    pass
else:
    # 如果是直接运行此文件，则创建Web模式的app
    app = create_app()

# celery = app.extensions["celery"] if 'app' in locals() else None

if __name__ == "__main__":
    app = create_app()
    if app.config["TESTING"]:
        print("App is running in TESTING mode")
    # 修改端口为 5001
    app.run(host="0.0.0.0", port=5001, debug=True)
