from copy import copy
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from core.database._base_model import DBBaseModel
from api.main import app
from core.utils.settings import settings
from core.database.account import AccountInDB


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def ac() -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="https://test") as c:
        yield c


@pytest.fixture(scope="session")
def setup_db() -> Generator:
    sync_url = copy(settings.SQLALCHEMY_DATABASE_URL)
    engine = create_engine(sync_url)
    conn = engine.connect()
    try:
        conn.execute(text("DROP TABLE IF EXISTS test_table"))
    except SQLAlchemyError:
        pass
    finally:
        conn.close()

    conn = engine.connect()
    conn.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY)"))
    conn.close()

    yield

    conn = engine.connect()
    try:
        conn.execute(text("DROP TABLE IF EXISTS test_table"))
    except SQLAlchemyError:
        pass
    conn.close()
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db(setup_db: Generator) -> Generator:
    sync_url = copy(settings.SQLALCHEMY_DATABASE_URL)
    engine = create_engine(sync_url)

    with engine.begin():
        DBBaseModel.metadata.drop_all(engine)
        DBBaseModel.metadata.create_all(engine)
        yield
        DBBaseModel.metadata.drop_all(engine)

    engine.dispose()


@pytest.fixture
def session() -> Generator:
    # https://github.com/sqlalchemy/sqlalchemy/issues/5811#issuecomment-756269881
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    with engine.begin() as conn:
        with conn.begin_nested():
            SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=conn,
                future=True,
            )

            session = SessionLocal()

            yield session

    engine.dispose()


@pytest.fixture
def login_account(session) -> AccountInDB:
    phone = "12345678901"
    email = "login_account@email.com"
    username = "login_account"
    password_origin = "123456"
    from core.controller.account import create_account, CreateAccountPayload

    account = AccountInDB.find_by_username(session, username)
    if not account:
        reg_req = CreateAccountPayload(
            username=username,
            phone=phone,
            email=email,
            password=password_origin,
        )
        account = create_account(reg_req, session)
        session.commit()
    return account
