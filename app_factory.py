import os

from configs import shared_config

if not shared_config.DEBUG:
    from gevent import monkey

    monkey.patch_all()

from extensions import ext_compress, ext_database, ext_logging, ext_login, ext_migrate

from flask import Flask
from flask_cors import CORS
from commands import register_commands

from extensions.ext_database import db


def create_flask_app_with_configs() -> Flask:
    app = Flask(__name__)

    app.config.from_object(shared_config)

    # populate configs into system environment variables
    for key, value in app.config.items():
        if isinstance(value, str):
            os.environ[key] = value
        elif isinstance(value, int | float | bool):
            os.environ[key] = str(value)
        elif value is None:
            os.environ[key] = ""
    return app


def create_app() -> Flask:
    app = create_flask_app_with_configs()
    initialize_extensions(app)
    register_blueprints(app)
    register_commands(app)

    return app


def initialize_extensions(app):
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    ext_compress.init_app(app)
    ext_database.init_app(app)
    ext_logging.init_app(app)
    ext_login.init_app(app)
    ext_migrate.init_app(app, db)
    CORS(app)

# register blueprint routers
def register_blueprints(app: Flask):
    from apis import init_app

    init_app(app)