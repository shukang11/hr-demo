import json
import pytest
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from sqlalchemy.orm import Session
from configs import shared_config, AppConfig
from app import create_app
from extensions.ext_database import db
from libs.helper import get_sha256
from services.account import AccountService, AccountSchema, AccountCreate
from libs.schema.http import ResponseSchema
from tests.fixtures.account_data import TEST_USER

# We should install the package in development mode instead of modifying sys.path
# Run: pip install -e . from the api directory


@pytest.fixture
def app_config() -> AppConfig:
    """创建测试应用配置"""
    shared_config.DEBUG = True
    shared_config.TESTING = True
    shared_config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    shared_config.SQLALCHEMY_ECHO = False
    shared_config.SECRET_KEY = "test-secret-key"
    return shared_config


@pytest.fixture
def app() -> Flask:
    """创建测试应用实例"""
    app = create_app()
    app.secret_key = "test-secret-key"
    return app


@pytest.fixture
def client(app: Flask, test_session: Session) -> FlaskClient:
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """创建测试命令行运行器"""
    return app.test_cli_runner()


@pytest.fixture
def test_session(app: Flask) -> Generator[Session, None, None]:
    """初始化测试数据库"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_user(
    client: Flask,
    test_session: Session,
) -> AccountSchema:
    """创建测试用户"""

    service = AccountService(session=test_session)
    test_user = TEST_USER
    account = service._find_account_by_login_credential(
        test_user["username"], get_sha256(test_user["password"])
    )

    if not account:
        # 如果用户不存在，创建一个新用户
        _ = service.register_account(
            AccountCreate(
                username=test_user["username"],
                email=test_user["email"],
                password_hashed=get_sha256(test_user["password"]),
                full_name=test_user["full_name"],
            )
        )

    req = {
        "username": test_user["username"],
        "password_hashed": get_sha256(test_user["password"]),
    }
    response = client.post(
        "/api/auth/login",
        json=req,
        content_type="application/json",
    )

    info = client.get(
        "/api/auth/info",
        headers={"Authorization": f"Bearer {response.json['data']['token']}"},
    )

    assert info.status_code == 200
    return AccountSchema.model_validate(info.json["data"])
