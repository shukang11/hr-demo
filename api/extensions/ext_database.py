from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    import libs.models  # noqa: F401

    db.init_app(app)
