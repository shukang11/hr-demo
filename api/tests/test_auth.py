import json

from flask.testing import FlaskClient


def test_login_success(client: FlaskClient, test_user: dict):
    """测试成功登录场景"""
    # 准备登录数据
    login_data = {
        "username": test_user["username"],
        "password_hashed": test_user["password_hashed"],
    }

    # 发送登录请求
    response = client.post(
        "/api/auth/login", data=json.dumps(login_data), content_type="application/json"
    )

    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)

    # 验证响应结构
    assert "data" in data
    assert "context" in data
    assert data["context"]["status"] == 200

    # 验证token
    assert "token" in data["data"]
    assert len(data["data"]["token"]) > 0


def test_login_invalid_request(client: FlaskClient):
    """测试无效的请求数据"""
    # 缺少密码字段
    invalid_data = {"username": "testuser"}

    response = client.post(
        "/api/auth/login",
        data=json.dumps(invalid_data),
        content_type="application/json",
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    print(f"Invalid request data: {data}")
    assert data["context"]["message"] == "无效的请求数据"


def test_login_wrong_password(client: FlaskClient, test_user: dict):
    """测试密码错误的情况"""
    login_data = {"username": "test_user", "password": "wrongpassword"}

    response = client.post(
        "/api/auth/login", data=json.dumps(login_data), content_type="application/json"
    )

    assert response.status_code >= 400


def test_login_nonexistent_user(client: FlaskClient):
    """测试不存在的用户登录"""
    login_data = {"username": "nonexistent", "password": "password123"}

    response = client.post(
        "/api/auth/login", data=json.dumps(login_data), content_type="application/json"
    )

    assert response.status_code >= 400
