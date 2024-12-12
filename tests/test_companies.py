import json
import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from models.account import AccountInDB
from models.company import CompanyInDB


def test_create_company_success(client: FlaskClient, test_user: AccountInDB, test_session: Session):
    """测试成功创建公司场景"""
    # 准备创建公司的数据
    company_data = {
        "name": "Test Company",
        "description": "A test company"
    }

    # 发送创建公司请求
    response = client.post(
        "/api/companies",
        data=json.dumps(company_data),
        content_type="application/json"
    )

    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # 验证响应结构
    assert "data" in data
    assert "context" in data
    assert data["context"]["status"] == 200
    assert data["context"]["message"] == "公司创建成功"
    
    # 验证返回的公司数据
    company_data_response = data["data"]
    assert company_data_response["name"] == company_data["name"]
    assert company_data_response["description"] == company_data["description"]
    assert company_data_response["owner_id"] == test_user.id
    
    # 验证数据库中的公司记录
    company = test_session.query(CompanyInDB).filter_by(name=company_data["name"]).first()
    assert company is not None
    assert company.owner_id == test_user.id
    assert company.name == company_data["name"]
    assert company.description == company_data["description"]


def test_create_company_invalid_request(client: FlaskClient, test_user: AccountInDB):
    """测试无效的请求数据"""
    # 缺少必需的name字段
    invalid_data = {
        "description": "A test company"
    }

    response = client.post(
        "/api/companies",
        data=json.dumps(invalid_data),
        content_type="application/json"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["context"]["message"] == "无效的请求数据"


def test_create_company_unauthorized(client: FlaskClient):
    """测试未登录用户创建公司"""
    company_data = {
        "name": "Test Company",
        "description": "A test company"
    }

    response = client.post(
        "/api/companies",
        data=json.dumps(company_data),
        content_type="application/json"
    )

    assert response.status_code == 401
    data = json.loads(response.data)
    assert "未登录" in data["context"]["message"]


def test_create_company_duplicate_name(client: FlaskClient, test_user: AccountInDB, test_session: Session):
    """测试创建同名公司"""
    # 先创建一个公司
    existing_company = CompanyInDB(
        name="Test Company"
    )
    test_session.add(existing_company)
    test_session.commit()

    # 尝试创建同名公司
    company_data = {
        "name": "Test Company",
    }

    response = client.post(
        "/api/companies",
        data=json.dumps(company_data),
        content_type="application/json"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "已存在" in data["context"]["message"] 