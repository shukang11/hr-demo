import pytest  # noqa: F401
from sqlalchemy.orm import Session
from core.controller.account import (
    AccountManager,
    InsertAccountPayload,
    LoginAccountPayload,
)
from core.database import AdministratorInDB


def setup_module(module):
    print("setup_module      module:%s" % module.__name__)


def test_create_account(session: Session) -> None:
    req = InsertAccountPayload(
        username="test",
        phone="12345678901",
        email="test@email.com",
        password="123456",
    )
    manager = AccountManager(session)
    account = manager.insert_administrator(req, session)
    assert account.username == "test"
    assert account.phone == "12345678901"
    assert account.email == "test@email.com"


def test_login_account(
    session: Session, login_administrator: AdministratorInDB
) -> None:
    assert login_administrator.token.value is not None
    req = LoginAccountPayload(
        email=login_administrator.email,
        password=login_administrator.password,
    )
    manager = AccountManager(session)
    account = manager.login_administrator(req, session)

    assert account.username == login_administrator.username
    assert account.phone == login_administrator.phone
    assert account.email == login_administrator.email


def test_find_account(session: Session, login_administrator: AdministratorInDB) -> None:
    account = AdministratorInDB.find_by_username(session, login_administrator.username)
    assert account.username == login_administrator.username
    assert account.phone == login_administrator.phone
    assert account.email == login_administrator.email

    account = AdministratorInDB.find_by_id(session, login_administrator.id)
    assert account.username == login_administrator.username
    assert account.phone == login_administrator.phone
    assert account.email == login_administrator.email

    account = AdministratorInDB.find_by_token(session, login_administrator.token.value)
    assert account.username == login_administrator.username
    assert account.phone == login_administrator.phone
    assert account.email == login_administrator.email
