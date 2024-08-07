import pytest  # noqa: F401
from sqlalchemy.orm import Session
from core.controller.account import (
    create_account,
    CreateAccountPayload,
    login_user,
    LoginAccountPayload,
)
from core.database.account import AccountInDB


def setup_module(module):
    print("setup_module      module:%s" % module.__name__)


def test_create_account(session: Session) -> None:
    req = CreateAccountPayload(
        username="test",
        phone="12345678901",
        email="test@email.com",
        password="123456",
    )
    account = create_account(req, session)
    assert account.username == "test"
    assert account.phone == "12345678901"
    assert account.email == "test@email.com"


def test_login_account(session: Session, login_account: AccountInDB) -> None:
    assert login_account.token.token is not None
    req = LoginAccountPayload(
        email=login_account.username,
        password=login_account.password,
    )
    account = login_user(req, session)

    assert account.username == login_account.username
    assert account.phone == login_account.phone
    assert account.email == login_account.email


def test_find_account(session: Session, login_account: AccountInDB) -> None:
    account = AccountInDB.find_by_username(session, login_account.username)
    assert account.username == login_account.username
    assert account.phone == login_account.phone
    assert account.email == login_account.email

    account = AccountInDB.find_by_id(session, login_account.id)
    assert account.username == login_account.username
    assert account.phone == login_account.phone
    assert account.email == login_account.email

    account = AccountInDB.find_by_token(session, login_account.token.token)
    assert account.username == login_account.username
    assert account.phone == login_account.phone
    assert account.email == login_account.email
