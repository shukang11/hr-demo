from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from libs.helper import getmd5
from libs.models.account import AccountInDB, AccountTokenInDB
from ._shcema import LoginRequest, LoginResponse, UserInResponse
from sqlalchemy import select, or_  # 导入 or_ 用于组合查询条件
from sqlalchemy.orm import joinedload


class AccountService:
    """账户服务类

    封装了与账户相关的核心业务逻辑，如认证、注册和信息查询。
    """

    session: Session

    def __init__(self, session: Session) -> None:
        """初始化账户服务

        Args:
            session (Session): SQLAlchemy 数据库会话对象。
        """
        self.session = session

    def find_account_by_id(self, id: int) -> Optional[AccountInDB]:
        """根据账户 ID 查找账户信息 (包含令牌)

        Args:
            id (int): 账户的唯一标识符 (AccountInDB.id)。

        Returns:
            Optional[AccountInDB]: 找到的账户数据库模型对象 (预加载 token)，如果未找到则返回 None。
        """
        session = self.session
        stmt = (
            select(AccountInDB)
            .options(joinedload(AccountInDB.token))  # 预加载 token 关系
            .where(AccountInDB.id == id)
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    def find_account_by_token(self, token: str) -> Optional[AccountInDB]:
        """根据 API 令牌查找关联的账户信息 (包含令牌)

        Args:
            token (str): 要查找的 API 令牌字符串 (AccountTokenInDB.token)。

        Returns:
            Optional[AccountInDB]: 找到的账户数据库模型对象 (预加载 token)，如果未找到则返回 None。
        """
        session = self.session
        stmt = (
            select(AccountInDB)
            .join(AccountInDB.token)
            .options(joinedload(AccountInDB.token))
            .where(AccountTokenInDB.token == token)
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    def _find_account_by_login_credential(
        self, credential: str, password: str
    ) -> Optional[AccountInDB]:
        """【私有】根据登录凭证（用户名或邮箱）和密码查找账户 (包含令牌)"""
        hashed_password = getmd5(password)
        session = self.session
        stmt = (
            select(AccountInDB)
            .options(joinedload(AccountInDB.token))  # 预加载 token
            .where(
                or_(
                    AccountInDB.username == credential, AccountInDB.email == credential
                ),
                AccountInDB.password == hashed_password,
            )
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    def register_account(
        self,
        username: str,
        password: str,
        email: str,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        is_admin: bool = False,
        gender: Optional[int] = None,
    ) -> Tuple[Optional[AccountInDB], Optional[str]]:
        """注册新账户

        检查用户名和邮箱是否已被占用，如果未被占用则创建新账户。

        Args:
            username (str): 新账户的用户名。
            password (str): 新账户的原始密码。
            email (str): 新账户的电子邮箱。
            full_name (Optional[str]): 新账户的全名。
            phone (Optional[str]): 新账户的手机号。
            is_admin (bool): 新账户是否为管理员。
            gender (Optional[int]): 新账户的性别。

        Returns:
            Tuple[Optional[AccountInDB], Optional[str]]:
            - AccountInDB: 成功创建的账户对象；如果失败则为 None。
            - str: 创建失败时的错误信息；如果成功则为 None。
        """
        session = self.session
        # 检查用户名或邮箱是否已存在
        stmt_exists = select(AccountInDB.id).where(
            or_(AccountInDB.username == username, AccountInDB.email == email)
        )
        existing_user_id = session.execute(stmt_exists).scalar_one_or_none()
        if existing_user_id:
            # 可以更具体地判断是用户名还是邮箱冲突，但通常返回统一错误
            return None, "用户名或邮箱已被注册"

        account = AccountInDB(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            gender=gender,
            is_admin=is_admin,
            is_active=True,  # 新账户默认为激活状态
            password=getmd5(password),
        )

        session.add(account)
        try:
            session.flush()  # 尝试写入数据库以捕获唯一约束等错误，并获取 ID
            return account, None
        except Exception as _e:
            # 捕获可能的数据库层面的错误（虽然理论上上面的检查已覆盖唯一性）
            session.rollback()  # 出错时回滚
            # log e
            return None, "创建账户时发生错误"

    def _update_account_token(self, account: AccountInDB) -> str:
        """【私有】更新或创建账户的令牌。

        Args:
            account (AccountInDB): 需要更新令牌的账户对象。

        Returns:
            str: 新的或更新后的令牌字符串。
        """
        # 盐值生成逻辑移到内部
        salt = f"token_{datetime.now().timestamp()}"
        new_token_value = account.make_new_token_value(salt=salt)

        if account.token:
            account.token.token = new_token_value
            account.token.updated_at = datetime.now()  # 更新令牌更新时间
        else:
            token = AccountTokenInDB(account=account, token=new_token_value)
            self.session.add(token)
        # flush 会在 process_login 结束时或更高层级处理
        # self.session.flush()
        return new_token_value

    def process_login(
        self, login_data: LoginRequest
    ) -> Tuple[Optional[LoginResponse], Optional[str], int]:
        """处理用户登录请求

        验证用户凭证，检查账户状态，更新令牌和最后登录时间，并返回登录响应或错误信息。

        Args:
            login_data (LoginRequest): 包含登录凭证（用户名/邮箱）和密码的请求数据模型。

        Returns:
            Tuple[Optional[LoginResponse], Optional[str], int]:
            - LoginResponse: 登录成功时，包含令牌和用户信息的响应对象；失败时为 None。
            - str: 登录失败时的错误信息；成功时为 None。
            - int: HTTP 状态码 (200 表示成功, 400 表示请求错误, 401 表示认证失败, 403 表示禁止访问)。
        """
        credential = login_data.username or login_data.email
        if not credential:
            return None, "用户名或邮箱不能为空", 400

        # 使用私有方法查找用户
        user = self._find_account_by_login_credential(credential, login_data.password)

        if not user:
            return None, "用户名/邮箱或密码错误", 401

        if not user.is_active:
            return None, "账户已被禁用", 403

        # 登录成功，更新令牌和最后登录时间
        # 使用私有方法更新/创建令牌
        token_value = self._update_account_token(user)
        user.last_login_at = datetime.now()
        # 注意：事务提交应在调用此方法之后，在请求处理的更高层级完成
        # self.session.commit()

        response_data = LoginResponse(
            token=token_value,
            user=UserInResponse(
                id=str(user.id),
                username=user.username,
                email=user.email,
                full_name=user.full_name or "",
                is_admin=user.is_admin,
            ),
        )

        return response_data, None, 200
