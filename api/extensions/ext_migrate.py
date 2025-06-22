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

    # 桌面模式下跳过migrate初始化，因为桌面模式不需要迁移
    if app.config.get("DESKTOP_MODE", False):
        app.logger.info("桌面模式：跳过flask_migrate初始化")
        return

    flask_migrate.Migrate(app, db)
