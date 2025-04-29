from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, or_  # 导入 or_ 用于组合查询条件
from sqlalchemy.orm import joinedload

from libs.models.account import AccountInDB, AccountTokenInDB

from ._schema import LoginRequest, LoginResponse, AccountSchema, AccountCreate
from ._error import AccountLoginError


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
        self, credential: str, password_hashed: str
    ) -> Optional[AccountInDB]:
        """【私有】根据登录凭证（用户名或邮箱）和密码查找账户 (包含令牌)"""
        session = self.session
        stmt = (
            select(AccountInDB)
            .options(joinedload(AccountInDB.token))  # 预加载 token
            .where(
                or_(
                    AccountInDB.username == credential, AccountInDB.email == credential
                ),
                AccountInDB.password_hashed == password_hashed,
            )
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    def register_account(
        self,
        register_data: AccountCreate,
    ) -> Optional[AccountSchema]:
        """注册新账户

        检查用户名和邮箱是否已被占用，如果未被占用则创建新账户。

        Args:
            register_data (AccountCreate): 注册请求数据模型，包含用户名、邮箱、密码等信息。

        Returns:
            Optional[AccountSchema]: 成功创建的账户对象；如果失败则为 None。
        """
        session = self.session
        # 检查用户名或邮箱是否已存在
        stmt_exists = select(AccountInDB.id).where(
            or_(
                AccountInDB.username == register_data.username,
                AccountInDB.email == register_data.email,
            )
        )
        existing_user_id: Optional[int] = session.execute(
            stmt_exists
        ).scalar_one_or_none()
        if existing_user_id:
            # 可以更具体地判断是用户名还是邮箱冲突，但通常返回统一错误
            return None

        account = AccountInDB(
            username=register_data.username,
            email=register_data.email,
            password=register_data.password_hashed,
            phone=register_data.phone,
        )

        session.add(account)
        try:
            session.flush()  # 尝试写入数据库以捕获唯一约束等错误，并获取 ID
            return AccountSchema.from_entity(account)  # 返回新创建的账户对象
        except Exception as _e:
            # 捕获可能的数据库层面的错误（虽然理论上上面的检查已覆盖唯一性）
            session.rollback()  # 出错时回滚
            # log e
            return None

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

    def process_login(self, login_data: LoginRequest) -> LoginResponse:
        """处理用户登录请求

        验证用户凭证，检查账户状态，更新令牌和最后登录时间，并返回登录响应或错误信息。

        Args:
            login_data (LoginRequest): 包含登录凭证（用户名/邮箱）和密码的请求数据模型。

        Returns:
            LoginResponse: 登录成功时，包含令牌和用户信息的响应对象；失败时会抛出异常。
        """
        credential = login_data.username or login_data.email
        if not credential:
            raise AccountLoginError("用户名或邮箱不能为空")

        # 使用私有方法查找用户
        user = self._find_account_by_login_credential(
            credential, login_data.password_hashed
        )

        if not user:
            raise AccountLoginError(f"用户名或邮箱或密码错误: {credential}")

        if not user.is_active:
            raise AccountLoginError("账户未激活")

        # 登录成功，更新令牌和最后登录时间
        # 使用私有方法更新/创建令牌
        token_value = self._update_account_token(user)
        user.last_login_at = datetime.now()
        # 注意：事务提交应在调用此方法之后，在请求处理的更高层级完成
        # self.session.commit()

        response_data = LoginResponse(
            token=token_value,
            user=AccountSchema.from_entity(user),
        )

        return response_data
