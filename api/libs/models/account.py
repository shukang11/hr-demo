from datetime import datetime
from typing import Optional, TYPE_CHECKING
from flask_login import UserMixin
from sqlalchemy.orm import Mapped
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    SMALLINT,
    UniqueConstraint,
)  # Import ForeignKey and UniqueConstraint if needed for table args
from extensions.ext_database import db
from .base import BaseModel
from libs.helper import getmd5

if TYPE_CHECKING:
    # 引入 AccountCompanyInDB 用于类型提示，避免循环导入
    from .company import CompanyInDB

    from .account_company import AccountCompanyInDB


class AccountInDB(BaseModel, UserMixin):
    """账户数据库模型
    存储系统用户的基本信息、认证凭证和状态。
    继承自 BaseModel (提供基础字段如 id, created_at, updated_at) 和 UserMixin (Flask-Login 集成)。

    Attributes:
        username (str): 用户名，用于登录，必须唯一且不为空。
        email (str): 电子邮箱，用于联系和可能的登录/重置密码，必须唯一且不为空。
        phone (str): 手机号码，可选。
        gender (Optional[int]): 性别，0-未知, 1-男, 2-女，可选。
        password (str): 存储加密后的用户密码哈希值，不为空。
        is_active (bool): 账户是否激活，默认为 True。未激活账户无法登录。
        last_login_at (Optional[datetime]): 用户最后一次成功登录的时间，可选。
        token (Optional[AccountTokenInDB]): 与账户关联的 API 令牌对象 (一对一关系)。
        companies (list[CompanyInDB]): 账户所属或管理的公司列表 (通过 account_company 表建立的多对多关系)。
    """

    __tablename__ = "accounts"
    # 表注释
    __table_args__ = {"comment": "系统账户信息表"}

    username: Mapped[str] = Column(
        String(64), unique=True, nullable=False, comment="用户名，唯一"
    )
    email: Mapped[str] = Column(
        String(255), unique=True, nullable=False, comment="电子邮箱，唯一"
    )
    phone: Mapped[Optional[str]] = Column(
        String(20), nullable=True, comment="手机号码"
    )  # Made explicitly nullable=True for clarity

    gender: Mapped[int] = Column(
        SMALLINT,
        nullable=True,  # 允许为空，性别是可选的
        default=0,
        comment="性别，0-未知，1-男，2-女",
    )
    password_hashed: Mapped[str] = Column(
        String(255), nullable=False, comment="密码哈希值"
    )
    is_active: Mapped[bool] = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="账户是否激活 (True: 激活, False: 禁用)",
    )  # Added nullable=False for clarity
    last_login_at: Mapped[Optional[datetime]] = Column(
        DateTime, nullable=True, comment="最后登录时间"
    )  # Made explicitly nullable=True for clarity

    # Relationships
    # 定义与 AccountTokenInDB 的一对一关系
    # uselist=False 表示这是一个一对一关系
    # back_populates="account" 指定在 AccountTokenInDB 模型中反向关联的属性名
    # cascade="all, delete-orphan" 表示当 AccountInDB 对象被删除时，关联的 AccountTokenInDB 对象也会被删除
    token: Mapped[Optional["AccountTokenInDB"]] = db.relationship(
        "AccountTokenInDB",
        uselist=False,
        back_populates="account",
        cascade="all, delete-orphan",
    )

    # 添加与AccountCompanyInDB的关系
    account_companies: Mapped[list["AccountCompanyInDB"]] = db.relationship(
        "AccountCompanyInDB",
        back_populates="account",
        cascade="all, delete-orphan",
        overlaps="companies",  # 添加这个参数
    )
    # 定义与 CompanyInDB 的多对多关系，通过 account_company 表
    # secondary 参数指定了连接（中间）表
    # back_populates 指定了在 CompanyInDB 模型中反向关联的属性名 (accounts)
    companies: Mapped[list["CompanyInDB"]] = db.relationship(
        "CompanyInDB",
        secondary="account_company",  # 指定中间表名
        back_populates="accounts",  # 指向 CompanyInDB.accounts
        cascade="all, delete",  # 根据需要调整级联操作，通常不需要 delete-orphan
        overlaps="account_companies",  # 添加这个参数
    )

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        phone: Optional[str] = None,
        gender: Optional[int] = None,
        is_active: Optional[bool] = True,
        last_login_at: Optional[datetime] = None,
    ) -> None:
        """初始化账户对象

        Args:
            username (str): 用户名，唯一且不为空。
            email (str): 电子邮箱，唯一且不为空。
            password (str): 密码，未加密的明文密码。
            phone (Optional[str]): 手机号码，可选。

        """
        super().__init__()
        self.username = username
        self.email = email
        self.password_hashed = password
        self.phone = phone
        self.gender = gender or 0  # 默认性别为未知
        self.is_active = is_active
        self.last_login_at = last_login_at
        self.token = None

    def make_new_token_value(self, salt: str) -> str:
        """生成一个新的、唯一的令牌字符串值。
        通常用于创建或刷新 API 令牌。

        Args:
            salt (str): 一个随机字符串（盐值），用于增加生成令牌的复杂度，防止预测。

        Returns:
            str: 基于账户信息、当前时间和盐值生成的 MD5 哈希值，作为令牌字符串。
        """
        token_str = f"{self.id}:{self.username}:{datetime.now().timestamp()}:{salt}"
        return getmd5(token_str)

    def get_token(self) -> Optional[str]:
        """获取当前账户关联的有效令牌字符串。

        Returns:
            Optional[str]: 如果存在关联的令牌对象，则返回令牌字符串；否则返回 None。
        """
        # 检查 self.token 是否存在，因为关系是 Optional
        if self.token:
            return self.token.token
        return None


class AccountTokenInDB(BaseModel):
    """账户令牌数据库模型
    存储与用户账户关联的 API 访问令牌。

    Attributes:
        account_id (int): 关联的账户 ID，外键指向 `accounts` 表的 `id` 字段，唯一且不为空。
        token (str): 实际的令牌字符串，唯一且不为空。
        account (AccountInDB): 与 `AccountInDB` 模型建立的一对一反向关系。
    """

    __tablename__ = "account_tokens"
    # 表注释
    __table_args__ = (
        # 确保 account_id 是唯一的，强制一对一关系
        UniqueConstraint("account_id", name="uq_account_tokens_account_id"),
        {"comment": "账户 API 访问令牌表"},
    )

    # 使用 ForeignKey 明确指定外键约束
    account_id: Mapped[int] = Column(
        Integer,
        db.ForeignKey("accounts.id"),
        nullable=False,
        unique=True,
        comment="关联的账户ID (accounts.id)，唯一",
    )
    token: Mapped[str] = Column(
        String(255), nullable=False, unique=True, comment="API 访问令牌字符串，唯一"
    )

    # Relationships
    # 定义与 AccountInDB 的一对一反向关系
    # back_populates="token" 指定在 AccountInDB 模型中对应的关系属性名
    account: Mapped["AccountInDB"] = db.relationship(
        "AccountInDB", back_populates="token"
    )
