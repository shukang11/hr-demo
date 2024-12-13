from enum import StrEnum
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from flask_login import UserMixin
from sqlalchemy.orm import Mapped
from extensions.ext_database import db
from .base import BaseModel
from libs.helper import getmd5

if TYPE_CHECKING:
    from models.company import AccountCompanyInDB

class AccountGender(StrEnum):
    """账户性别"""
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class AccountInDB(BaseModel, UserMixin):
    """账户数据库模型
    存储系统账户信息，用于身份认证和授权

    Attributes:
        username (str): 用户名，唯一
        email (str): 电子邮箱，唯一
        phone (str): 手机号码
        password (str): 密码哈希值
        full_name (str): 用户全名
        is_active (bool): 是否激活
        is_admin (bool): 是否为系统管理员
        last_login_at (datetime): 最后登录时间
        token (AccountTokenInDB): 关联的账户令牌
        companies (list): 用户管理的公司列表
    """
    __tablename__ = 'accounts'

    username: Mapped[str] = db.Column(db.String(64), unique=True, nullable=False)
    email: Mapped[str] = db.Column(db.String(255), unique=True, nullable=False)
    phone: Mapped[str] = db.Column(db.String(20))
    gender: Mapped[AccountGender] = db.Column(db.String(10), nullable=True)
    password: Mapped[str] = db.Column(db.String(255), nullable=False)
    full_name: Mapped[Optional[str]] = db.Column(db.String(255), nullable=True)
    is_active: Mapped[bool] = db.Column(db.Boolean, default=True)
    is_admin: Mapped[bool] = db.Column(db.Boolean, default=False)
    last_login_at: Mapped[Optional[datetime]] = db.Column(db.DateTime)

    # Relationships
    token: Mapped[Optional['AccountTokenInDB']] = db.relationship('AccountTokenInDB', uselist=False, back_populates='account', cascade='all, delete-orphan')
    companies: Mapped[list['AccountCompanyInDB']] = db.relationship('AccountCompanyInDB', back_populates='account')

    def make_new_token_value(self, salt: str) -> str:
        """生成新的令牌值

        Args:
            salt (str): 盐值，用于增加令牌的随机性

        Returns:
            str: 生成的令牌值
        """
        token_str = f"{self.id}:{self.username}:{datetime.now().timestamp()}:{salt}"
        return getmd5(token_str)
    
    def get_token(self) -> str:
        """获取账户令牌

        Returns:
            str: 账户令牌
        """
        return self.token.token


class AccountTokenInDB(BaseModel):
    """账户令牌数据库模型
    存储账户的身份认证令牌

    Attributes:
        account_id (int): 关联的账户ID
        token (str): 令牌值
        account (AccountInDB): 关联的账户对象
    """
    __tablename__ = 'account_tokens'

    account_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, unique=True)
    token: Mapped[str] = db.Column(db.String(255), nullable=False, unique=True)

    # Relationships
    account: Mapped['AccountInDB'] = db.relationship('AccountInDB', back_populates='token')

