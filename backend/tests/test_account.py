import pytest  # noqa Ruff: noqa: F401
from sqlalchemy.orm import Session
from core.controller.account import register_user, RegisterUser


def setup_module(module):
    print("setup_module      module:%s" % module.__name__)


def test_create_account(session: Session) -> None:
    req = RegisterUser(
        username="test",
        phone="12345678901",
        email="test@email.com",
        password="123456",
    )
    account = register_user(req, session)
    assert account.username == "test"
