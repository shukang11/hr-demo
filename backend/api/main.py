# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

__all__ = ["create_app"]

load_dotenv()


def create_tables_if_dev():
    from core.database._session import engine
    from core.database._base_model import DBBaseModel
    from core import database  # noqa: F401

    try:
        # 查看所有的表
        from sqlalchemy import inspect

        insp = inspect(engine)
        print(insp.get_table_names())
        meta = DBBaseModel.metadata
        meta.drop_all(bind=engine)
        meta.create_all(bind=engine)
        print(f"meta: {meta}")
        print("Tables created successfully on: ", os.getenv("SQLALCHEMY_DATABASE_URL"))
    except Exception as e:
        print(f"Error creating tables: {e}")


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    create_tables_if_dev()

    from .routes import init_app as routes_init_app

    routes_init_app(app=app)

    return app


app = create_app()
