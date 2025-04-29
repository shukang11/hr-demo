"""
AccountService测试模块
测试账户服务的各项功能，包括用户查询、注册和登录
"""

import pytest

from sqlalchemy.orm import Session
from services.account import (
    AccountService,
    AccountLoginError,
    AccountCreate,
)
from libs.models.account import AccountInDB
from tests.fixtures.account_data import (
    create_test_user,
    create_login_request,
    setup_sample_users,
)


class TestAccountService:
    """AccountService测试类"""

    @pytest.fixture
    def account_service(self, test_session: Session) -> AccountService:
        """创建AccountService实例"""
        return AccountService(test_session)

    @pytest.fixture
    def sample_users(self, test_session: Session) -> dict[str, AccountInDB]:
        """创建样本用户"""
        return setup_sample_users(test_session)

    def test_find_account_by_id_success(
        self, account_service: AccountService, sample_users: dict[str, AccountInDB]
    ):
        """测试成功根据ID查找用户"""
        # 获取已创建的普通用户
        normal_user = sample_users["normal"]

        # 使用ID查找用户
        found_user = account_service.find_account_by_id(normal_user.id)

        # 验证找到的用户与创建的用户是同一个
        assert found_user is not None
        assert found_user.id == normal_user.id
        assert found_user.username == normal_user.username
        assert found_user.email == normal_user.email

    def test_find_account_by_id_not_found(self, account_service: AccountService):
        """测试查找不存在的用户ID返回None"""
        non_existent_id = 999999
        found_user = account_service.find_account_by_id(non_existent_id)
        assert found_user is None

    def test_find_account_by_token_success(
        self, account_service: AccountService, test_session: Session
    ):
        """测试成功根据令牌查找用户"""
        # 创建带有令牌的用户
        user_with_token = create_test_user(
            test_session, username="token_user", with_token=True
        )
        test_session.commit()

        # 获取用户令牌
        token_value = user_with_token.token.token

        # 使用令牌查找用户
        found_user = account_service.find_account_by_token(token_value)

        # 验证找到的用户与创建的用户是同一个
        assert found_user is not None
        assert found_user.id == user_with_token.id
        assert found_user.username == user_with_token.username

    def test_find_account_by_token_not_found(self, account_service: AccountService):
        """测试查找不存在的令牌返回None"""
        non_existent_token = "non_existent_token_12345"
        found_user = account_service.find_account_by_token(non_existent_token)
        assert found_user is None

    def test_register_account_success(self, account_service: AccountService):
        """测试成功注册新账户"""
        # 注册参数
        username = "new_test_user"
        email = "newtest@example.com"
        password = "newpassword123"

        # 注册新账户
        payload = AccountCreate(
            username=username, email=email, password_hashed=password
        )
        new_account = account_service.register_account(payload)

        # 验证注册成功
        assert new_account is not None
        assert new_account.username == username
        assert new_account.email == email

    def test_register_account_duplicate_username(
        self, account_service: AccountService, sample_users: dict[str, AccountInDB]
    ):
        """测试注册重复用户名的账户失败"""
        # 尝试使用已存在的用户名注册
        existing_user = sample_users["normal"]
        print(f"# 使用已存在的用户数据: {existing_user}")
        result = account_service.register_account(
            AccountCreate(
                username=existing_user.username,
                email=existing_user.email,
                phone=existing_user.phone,
                password_hashed=existing_user.password_hashed,
            )
        )

        # 验证注册失败
        assert result is None

    def test_register_account_duplicate_email(
        self, account_service: AccountService, sample_users: dict[str, AccountInDB]
    ):
        """测试注册重复邮箱的账户失败"""
        # 尝试使用已存在的邮箱注册
        existing_user = sample_users["normal"]
        payload = AccountCreate(
            username=existing_user.username,
            email=existing_user.email,
            password_hashed="newpassword123",
        )
        result = account_service.register_account(payload)

        # 验证注册失败
        assert result is None

    def test_process_login_with_username_success(
        self, account_service: AccountService, sample_users: dict[str, AccountInDB]
    ):
        """测试使用用户名成功登录"""
        # 准备登录数据
        normal_user = sample_users["normal"]
        login_request = create_login_request(
            username=normal_user.username, password_hashed=normal_user.password_hashed
        )

        # 执行登录
        login_response = account_service.process_login(login_request)

        # 验证登录成功
        assert login_response is not None
        assert login_response.token is not None

        account = account_service.find_account_by_id(normal_user.id)

        assert account.username == normal_user.username
        assert account.email == normal_user.email

        assert account.token.token == login_response.token

    def test_process_login_with_email_success(
        self, account_service: AccountService, sample_users: dict
    ):
        """测试使用邮箱成功登录"""
        # 准备登录数据
        normal_user = sample_users["normal"]
        login_request = create_login_request(
            email=normal_user.email, password_hashed=normal_user.password_hashed
        )

        # 执行登录
        login_response = account_service.process_login(login_request)

        # 验证登录成功
        assert login_response is not None
        assert login_response.token is not None

    def test_process_login_invalid_credential(self, account_service: AccountService):
        """测试使用不存在的凭证登录失败"""
        # 准备登录数据（使用不存在的用户名）
        login_request = create_login_request(
            username="nonexistent_user", password_hashed="password123"
        )

        # 执行登录，应该抛出异常
        with pytest.raises(AccountLoginError) as exc_info:
            account_service.process_login(login_request)

        # 验证错误消息
        assert "用户名或邮箱或密码错误" in str(exc_info.value)

    def test_process_login_wrong_password(
        self, account_service: AccountService, sample_users: dict
    ):
        """测试使用错误的密码登录失败"""
        # 准备登录数据（使用错误的密码）
        normal_user = sample_users["normal"]
        login_request = create_login_request(
            username=normal_user.username, password_hashed="wrong_password"
        )

        # 执行登录，应该抛出异常
        with pytest.raises(AccountLoginError) as exc_info:
            account_service.process_login(login_request)

        # 验证错误消息
        assert "用户名或邮箱或密码错误" in str(exc_info.value)

    def test_process_login_inactive_user(
        self, account_service: AccountService, sample_users: dict
    ):
        """测试未激活的用户登录失败"""
        # 准备登录数据（使用未激活的用户）
        inactive_user = sample_users["inactive"]
        login_request = create_login_request(
            username=inactive_user.username,
            password_hashed=inactive_user.password_hashed,
        )

        # 执行登录，应该抛出异常
        with pytest.raises(AccountLoginError) as exc_info:
            account_service.process_login(login_request)

        # 验证错误消息
        assert "账户未激活" in str(exc_info.value)

    def test_update_token_for_existing_token(
        self, account_service: AccountService, test_session: Session
    ):
        """测试更新已有令牌"""
        # 创建带有令牌的用户
        user_with_token = create_test_user(
            test_session, username="token_update_user", with_token=True
        )
        test_session.commit()

        # 记住原始令牌
        original_token = user_with_token.token.token

        # 使用内部方法更新令牌
        new_token = account_service._update_account_token(user_with_token)

        # 验证令牌已更新
        assert new_token != original_token
        assert user_with_token.token.token == new_token

    def test_create_token_for_user_without_token(
        self, account_service: AccountService, test_session: Session
    ):
        """测试为没有令牌的用户创建令牌"""
        # 创建没有令牌的用户
        user_without_token = create_test_user(
            test_session, username="no_token_user", with_token=False
        )
        test_session.commit()

        # 确认用户没有令牌
        assert user_without_token.token is None

        # 使用内部方法创建令牌
        new_token = account_service._update_account_token(user_without_token)

        # 验证已创建令牌
        assert new_token is not None
        assert user_without_token.token is not None
        assert user_without_token.token.token == new_token
