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
from core.database import AdministratorInDB, CompanyInDB, DepartmentInDB, CompanyJobInDB


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
        # DBBaseModel.metadata.drop_all(engine)

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
def secret_key() -> str:
    return settings.SECRET_KEY


@pytest.fixture
def normal_company(session, login_administrator: AdministratorInDB) -> CompanyInDB:
    name = "test_normal_company"
    description = "test_normal_company_description"
    from core.database import CompanyStatus
    from core.controller.company import CompanyManager, InsertCompanyPayload

    payload = InsertCompanyPayload(
        name=name,
        description=description,
        status=CompanyStatus.ACTIVE,
        admin_id=login_administrator.id,
    )
    controller = CompanyManager(session)

    company = controller.create_company(payload=payload)
    session.commit()
    return company


def normal_department_1(session, normal_company: CompanyInDB) -> DepartmentInDB:
    name = "test_normal_department_1"
    from core.controller.company import CompanyManager, InsertDepartmentPayload

    payload = InsertDepartmentPayload(
        name=name,
        company_id=normal_company.id,
    )
    controller = CompanyManager(session)

    department = controller.insert_department(payload=payload)
    session.commit()
    return department


def normal_department_2(session, normal_company: CompanyInDB) -> DepartmentInDB:
    name = "test_normal_department_2"
    from core.controller.company import CompanyManager, InsertDepartmentPayload

    payload = InsertDepartmentPayload(
        name=name,
        company_id=normal_company.id,
    )
    controller = CompanyManager(session)

    department = controller.insert_department(payload=payload)
    session.commit()
    return department


def job_hr_in_normal_company(session, normal_company: CompanyInDB) -> CompanyJobInDB:
    name = "test_hr_job"
    description = "test_hr_job_description"
    from core.controller.company import CompanyManager, InsertCompanyJobPayload

    payload = InsertCompanyJobPayload(
        company_id=normal_company.id,
        job_name=name,
        description=description,
    )
    controller = CompanyManager(session)

    job = controller.insert_company_job(payload=payload)
    session.commit()
    return job


def job_cook_in_normal_company(session, normal_company: CompanyInDB) -> CompanyJobInDB:
    name = "test_cook_job"
    description = "test_cook_job_description"
    from core.controller.company import CompanyManager, InsertCompanyJobPayload

    payload = InsertCompanyJobPayload(
        company_id=normal_company.id,
        job_name=name,
        description=description,
    )
    controller = CompanyManager(session)

    job = controller.insert_company_job(payload=payload)
    session.commit()
    return job


@pytest.fixture
def login_administrator(session, secret_key) -> AdministratorInDB:
    phone = "12345678901"
    email = "login_account@email.com"
    username = "login_account"
    password_origin = "123456"
    from core.controller.account import AccountManager, InsertAccountPayload

    controller = AccountManager(session)

    account = AdministratorInDB.find_by_username(session, username)
    if not account:
        reg_req = InsertAccountPayload(
            username=username,
            phone=phone,
            email=email,
            password=password_origin,
        )
        account = controller.insert_administrator(reg_req, secret_key)
        session.commit()
    return account
