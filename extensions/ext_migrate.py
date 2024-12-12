from typing import TYPE_CHECKING

import flask_migrate

if TYPE_CHECKING:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy


def init_app(app: "Flask", db: "SQLAlchemy") -> None:
    """初始化数据库迁移扩展

    Args:
        app (Flask): Flask应用实例
        db (SQLAlchemy): SQLAlchemy数据库实例
    """
    flask_migrate.Migrate(app, db)
