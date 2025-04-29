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


def create_app(specific_config: Optional[AppConfig] = None) -> Flask:
    app = Flask(__name__)
    config = specific_config or shared_config

    # 增强 CORS 配置，解决预检请求问题
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
    
    # 设置 secret_key，这对于会话功能是必需的
    # 如果配置中已有密钥，则使用配置中的，否则生成一个随机密钥
    if not app.secret_key:
        app.secret_key = config.SECRET_KEY

    init_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app


app = create_app()
# celery = app.extensions["celery"]

if app.config["TESTING"]:
    print("App is running in TESTING mode")


if __name__ == "__main__":
    # 修改端口为 5001
    app.run(host="0.0.0.0", port=5001, debug=True)
