from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from extensions.ext_database import db
from libs.helper import getmd5
from models.account import AccountInDB, AccountTokenInDB
from schema.user import LoginRequest, LoginResponse, UserInResponse
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class AccountService:

    session: Session

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_account_by_id(self, id: int) -> Optional[AccountInDB]:
        session = self.session
        stmt = (
            select(AccountInDB)
            .options(joinedload(AccountInDB.token))
            .where(AccountInDB.id == id)
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    def is_account_exists(self, username: str) -> bool:
        session = self.session
        stmt = select(AccountInDB).where(AccountInDB.username == username)
        user = session.execute(stmt).scalar_one_or_none()
        return user is not None

    def find_account_by_token(self, token: str) -> Optional[AccountInDB]:
        session = self.session
        stmt = (
            select(AccountInDB)
            .options(joinedload(AccountInDB.token))
            .where(AccountTokenInDB.token == token)
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    def find_account_by_login(self, username: str, password: str) -> Optional[AccountInDB]:
        """根据用户名和密码查找账户
        
        Args:
            username: 用户名
            password: 原始密码（未加密）
            
        Returns:
            Optional[AccountInDB]: 找到的账户对象或None
        """
        hashed_password = getmd5(password)
        session = self.session
        stmt = (
            select(AccountInDB)
            .options(joinedload(AccountInDB.token))
            .where(
                AccountInDB.username == username,
                AccountInDB.password == hashed_password,
            )
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    def create_account_token(self, user_id: int, token: str) -> AccountTokenInDB:
        user_token = AccountTokenInDB(account_id=user_id, token=token)
        session = self.session
        session.add(user_token)
        session.flush()
        return user_token

    def get_account_token(self, account: AccountInDB, salt: str) -> str:
        """获取账户的令牌，如不存在则创建新令牌
        
        Args:
            account: 账户对象
            salt: 令牌盐值
            
        Returns:
            str: 令牌字符串
        """
        if account.token:
            return account.token.token
        session = self.session
        new_token = account.make_new_token_value(salt=salt)
        account_token = AccountTokenInDB(account_id=account.id, token=new_token)
        session.add(account_token)
        session.flush()
        return new_token

    def create_account_if_counld(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> AccountInDB:
        account = AccountInDB()
        account.username = username
        if email:
            account.email = email
        if phone:
            account.phone = phone

        password_hashed = getmd5(password)
        account.password = password_hashed
        session = self.session
        session.add(account)
        session.flush()
        return account

    def update_account_token(self, account: AccountInDB, salt: str) -> str:
        """更新账户的令牌
        
        Args:
            account: 账户对象
            salt: 令牌盐值
            
        Returns:
            str: 新的令牌字符串
        """
        new_token = account.make_new_token_value(salt=salt)
        if account.token:
            account.token.token = new_token
        else:
            token = AccountTokenInDB(account=account, token=new_token)
            self.session.add(token)
        self.session.flush()
        return new_token

    def process_login(self, login_data: LoginRequest) -> Tuple[Optional[LoginResponse], Optional[str], int]:
        """处理登录请求
        
        Args:
            login_data: 登录请求数据
            
        Returns:
            Tuple[Optional[LoginResponse], Optional[str], int]: 
            - LoginResponse: 登录成功时的响应数据
            - str: 错误信息
            - int: HTTP状态码
        """
        # 查找并验证用户
        user = self.find_account_by_login(login_data.username, login_data.password)
        if not user:
            return None, "用户名或密码错误", 401

        # 检查账户状态
        if not user.is_active:
            return None, "账户已被禁用", 403

        # 更新令牌和登录时间
        token_value = self.update_account_token(user, "login")
        user.last_login_at = datetime.now()
        db.session.commit()

        # 构建响应数据
        response_data = LoginResponse(
            token=token_value,
            user=UserInResponse(
                id=str(user.id),
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_admin=user.is_admin
            )
        )

        return response_data, None, 200
