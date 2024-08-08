import pytest  # noqa: F401
from sqlalchemy.orm import Session
from core.controller.account import (
    AccountManager,
    InsertAccountPayload,
    LoginAccountPayload,
)
from core.controller.company import (
    InsertCompanyPayload,
    InsertDepartmentPayload,
    InsertCompanyJobPayload,
)
from core.controller.company import CompanyManager
from core.database.administrator import AdministratorInDB
from core.database.company import CompanyInDB


def setup_module(module):
    print("setup_module      module:%s" % module.__name__)


def test_insert_company(
    session: Session, login_administrator: AdministratorInDB
) -> None:
    req = InsertCompanyPayload(
        name="test",
        description="test",
        admin_id=login_administrator.id,
    )
    manager = CompanyManager(session)
    company = manager.insert_company(req)
    assert company.name == "test"


def test_department_company(
    session: Session,
    login_administrator: AdministratorInDB,
) -> None:
    req = InsertCompanyPayload(
        name="test",
        description="test",
        admin_id=login_administrator.id,
    )
    manager = CompanyManager(session)
    company = manager.insert_company(req)
    assert company.name == "test"

    req = InsertDepartmentPayload(
        name="test",
        description="test",
        company_id=company.id,
    )
    department = manager.insert_department(req)
    assert department.name == "test"

    req = InsertCompanyJobPayload(
        job_name="test",
        description="test",
        company_id=company.id,
        department_id=department.id,
    )
    job = manager.insert_company_job(req)
    assert job.job_name == "test"
