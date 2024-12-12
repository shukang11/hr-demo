import json
from unittest.mock import patch, MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from apis.auth import bp as auth_bp
from extensions.ext_database import db
from models.account import AccountInDB, AccountTokenInDB
from schema.user import LoginResponse, UserInResponse



def test_login_success(client: FlaskClient, test_user: AccountInDB):
    """测试成功登录场景"""
    # 准备登录数据
    login_data = {
        "username": "test_user",
        "password": "password123"
    }

    # 发送登录请求
    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )

    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # 验证响应结构
    assert "data" in data
    assert "context" in data
    assert data["context"]["status"] == 200
    assert data["context"]["message"] == "登录成功"
    
    # 验证返回的用户数据
    user_data = data["data"]["user"]
    assert user_data["username"] == test_user.username
    assert user_data["email"] == test_user.email
    assert user_data["full_name"] == test_user.full_name
    assert user_data["is_admin"] == test_user.is_admin
    
    # 验证token
    assert "token" in data["data"]
    assert len(data["data"]["token"]) > 0


def test_login_invalid_request(client: FlaskClient):
    """测试无效的请求数据"""
    # 缺少密码字段
    invalid_data = {
        "username": "testuser"
    }

    response = client.post(
        "/api/auth/login",
        data=json.dumps(invalid_data),
        content_type="application/json"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["context"]["message"] == "无效的请求数据"


def test_login_wrong_password(client: FlaskClient, test_user: AccountInDB):
    """测试密码错误的情况"""
    login_data = {
        "username": "test_user",
        "password": "wrongpassword"
    }

    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )

    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["context"]["message"] == "用户名或密码错误"


def test_login_inactive_user(client: FlaskClient, test_user: AccountInDB):
    """测试已禁用账户的登录"""
    # 将用户设置为禁用状态
    test_user.is_active = False
    db.session.commit()

    login_data = {
        "username": "test_user",
        "password": "password123"
    }

    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )

    assert response.status_code == 403
    data = json.loads(response.data)
    assert data["context"]["message"] == "账户已被禁用"


def test_login_nonexistent_user(client: FlaskClient):
    """测试不存在的用户登录"""
    login_data = {
        "username": "nonexistent",
        "password": "password123"
    }

    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )

    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["context"]["message"] == "用户名或密码错误"


@patch('apis.auth.login_user')
def test_login_session_management(mock_login_user: MagicMock, client: FlaskClient, test_user: AccountInDB):
    """测试登录会话管理"""
    login_data = {
        "username": "test_user",
        "password": "password123"
    }

    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )

    assert response.status_code == 200
    
    # 验证 flask_login.login_user 被调用
    mock_login_user.assert_called_once_with(test_user)
    
    # 验证用户token被创建
    user_token = AccountTokenInDB.query.filter_by(account_id=test_user.id).first()
    assert user_token is not None
    assert user_token.token == json.loads(response.data)["data"]["token"] 