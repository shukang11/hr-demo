import pytest
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from sqlalchemy.orm import Session
from configs import shared_config, AppConfig
from app_factory import create_app
from extensions.ext_database import db
from models.account import AccountInDB
from libs.helper import getmd5

   
@pytest.fixture
def app_config() -> AppConfig:
    """创建测试应用配置"""
    shared_config.DEBUG = True
    shared_config.TESTING = True
    shared_config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    shared_config.SQLALCHEMY_ECHO = False
    shared_config.SECRET_KEY = 'test-secret-key'
    return shared_config

@pytest.fixture
def app() -> Flask:
    """创建测试应用实例"""
    app = create_app()
    app.secret_key = 'test-secret-key'
    return app


@pytest.fixture
def client(app: Flask, init_database: Session) -> FlaskClient:
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """创建测试命令行运行器"""
    return app.test_cli_runner()


@pytest.fixture
def init_database(app: Flask) -> Generator[Session, None, None]:
    """初始化测试数据库"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_user(init_database: Session) -> AccountInDB:
    """创建测试用户"""
    user = AccountInDB(
        username='test_user',
        email='test@example.com',
        password=getmd5('password123'),
        full_name='Test User',
        is_active=True,
        is_admin=False
    )
    init_database.session.add(user)
    init_database.session.commit()
    return user