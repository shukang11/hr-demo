import os
from typing import Optional

from flask import Flask, make_response, request
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

    if desktop_mode:
        # 桌面模式特殊配置
        from pathlib import Path

        desktop_path = Path(__file__).parent.parent / "desktop"

        # 配置静态文件路径
        app.static_folder = str(desktop_path / "static")
        app.static_url_path = ""

        # 桌面模式使用本地数据库
        desktop_db_path = desktop_path / "data" / "hr_desktop.db"
        desktop_db_path.parent.mkdir(exist_ok=True)

        # 桌面模式不需要CORS
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

    app.config.from_object(config)

    # 桌面模式数据库配置需要在config加载后设置
    if desktop_mode:
        from pathlib import Path

        desktop_path = Path(__file__).parent.parent / "desktop"
        desktop_db_path = desktop_path / "data" / "hr_desktop.db"
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{desktop_db_path}"

    # 设置 secret_key，这对于会话功能是必需的
    # 如果配置中已有密钥，则使用配置中的，否则生成一个随机密钥
    if not app.secret_key:
        app.secret_key = config.SECRET_KEY

    init_extensions(app)
    register_blueprints(app)
    register_commands(app)

    # 桌面模式添加SPA路由支持
    if desktop_mode:

        @app.route("/")
        def serve_frontend():
            """服务前端应用"""
            return app.send_static_file("index.html")

        @app.route("/<path:path>")
        def serve_static_files(path: str):
            """服务静态文件和SPA路由"""
            try:
                # 尝试服务静态文件
                return app.send_static_file(path)
            except Exception:
                # 对于SPA路由，返回index.html
                return app.send_static_file("index.html")

    return app


app = create_app()
# celery = app.extensions["celery"]

if app.config["TESTING"]:
    print("App is running in TESTING mode")


if __name__ == "__main__":
    # 修改端口为 5001
    app.run(host="0.0.0.0", port=5001, debug=True)
