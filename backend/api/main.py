# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

__all__ = ["create_app"]

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from .routes import init_app as routes_init_app

    # see how many versions, if zero, run db create all tables
    migrate_count = os.system("python -m alembic history")
    if migrate_count == 0:
        print("migrate_count == 0")
        from core.database._base_model import DBBaseModel

        # create all tables
        from core.database._session import engine

        DBBaseModel.metadata.create_all(bind=engine)
    else:
        # run migration
        migrate_result = os.system("python -m alembic upgrade head")
        if migrate_result != 0:
            print("migrate failed")

    routes_init_app(app=app)

    return app


app = create_app()
