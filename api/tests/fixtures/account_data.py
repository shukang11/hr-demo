"""
账户测试数据模块，提供创建测试账户的函数和固定的测试数据。
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from libs.helper import get_sha256
from libs.models.account import AccountInDB, AccountTokenInDB
from services.account._schema import LoginRequest


def create_test_user(
    session: Session,
    username: str = "test_user",
    email: str = "test@example.com",
    password: str = "password123",
    full_name: str = "Test User",
    is_admin: bool = False,
    is_active: bool = True,
    with_token: bool = False,
) -> AccountInDB:
    """
    创建测试用户并添加到数据库

    Args:
        session: 数据库会话
        username: 用户名
        email: 邮箱
        password: 密码（将被自动哈希）
        full_name: 全名
        is_admin: 是否为管理员
        is_active: 是否激活账户
        with_token: 是否创建关联的令牌

    Returns:
        AccountInDB: 创建的用户对象
    """
    user = AccountInDB(
        username=username,
        email=email,
        password=get_sha256(password),
        full_name=full_name,
        is_active=is_active,
        is_admin=is_admin,
        last_login_at=datetime.now() if is_active else None,
    )
    session.add(user)
    session.flush()  # 生成ID

    if with_token:
        # 创建测试令牌
        token = AccountTokenInDB(
            account=user,
            account_id=user.id,
            token=f"test_token_{user.id}_{username}",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(token)
        session.flush()

    return user


ADMIN_USER = {
    "username": "admin_user",
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Admin User",
    "is_admin": True,
    "is_active": True,
}

NORMAL_USER = {
    "username": "normal_user",
    "email": "user@example.com",
    "password": "user123",
    "full_name": "Normal User",
    "is_admin": False,
    "is_active": True,
}

INACTIVE_USER = {
    "username": "inactive_user",
    "email": "inactive@example.com",
    "password": "inactive123",
    "full_name": "Inactive User",
    "is_admin": False,
    "is_active": False,
}

TEST_USER = {
    "username": "test_user",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User",
    "is_admin": False,
    "is_active": True,
}

# 预定义的测试用户数据
SAMPLE_USERS = [
    ADMIN_USER,
    NORMAL_USER,
    INACTIVE_USER,
    TEST_USER,
]


def create_login_request(
    username: Optional[str] = None,
    email: Optional[str] = None,
    password_hashed: str = "password123",
) -> LoginRequest:
    """
    创建登录请求对象

    Args:
        username: 用户名（可选）
        email: 邮箱（可选）
        password: 密码

    Returns:
        LoginRequest: 登录请求对象
    """
    return LoginRequest(username=username, email=email, password_hashed=password_hashed)


def setup_sample_users(session: Session) -> Dict[str, AccountInDB]:
    """
    创建样本用户数据并添加到数据库

    Args:
        session: 数据库会话

    Returns:
        Dict[str, AccountInDB]: 键为用户类型，值为用户对象的字典
    """
    users = {}
    for user_data in SAMPLE_USERS:
        user = create_test_user(session, **user_data)
        # 使用用户名前缀作为键（例如：admin_user -> admin）
        key = user_data["username"].split("_")[0]
        users[key] = user

    session.commit()
    return users
