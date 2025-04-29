from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator
from libs.models import AccountInDB


class Gender(int, Enum):
    """性别枚举类

    定义了用户的性别选项。
    """

    UNKNOWN = 0
    # 男性
    FEMALE = 1
    # 女性
    MALE = 2


class AccountBase(BaseModel):
    """用户基础信息模型

    包含用户的基本属性，用作其他用户相关模型的基类。
    对应数据库模型 `AccountInDB` 的核心字段。
    """

    username: str = Field(..., description="用户名，对应 AccountInDB.username")
    email: EmailStr = Field(..., description="电子邮箱，对应 AccountInDB.email")
    phone: Optional[str] = Field(None, description="手机号码，对应 AccountInDB.phone")
    gender: Gender = Field(
        ...,
        default_factory=lambda: Gender.UNKNOWN,
        description="用户性别，对应 AccountInDB.gender",
    )


class AccountCreate(AccountBase):
    """用户创建模型

    用于创建新用户时的请求数据验证。
    继承自 `AccountBase`，并添加了密码字段。
    """

    password_hashed: str = Field(
        ...,
        min_length=6,
        description="用户密码[哈希值]，至少6个字符，对应 AccountInDB.password (创建时需要)",
    )


class AccountUpdate(BaseModel):
    """用户更新模型

    用于更新用户信息时的请求数据验证，所有字段都是可选的。
    允许部分更新用户的属性。
    """

    username: Optional[str] = Field(
        None, description="用户名，对应 AccountInDB.username"
    )
    email: Optional[EmailStr] = Field(
        None, description="电子邮箱，对应 AccountInDB.email"
    )


class AccountSchema(AccountBase):
    """用户响应模型

    用于序列化返回给客户端的用户信息，不包含敏感信息（如密码）。
    继承自 `AccountBase`，并添加了用户 ID。
    """

    id: str | int = Field(
        ..., description="用户唯一标识符，对应 AccountInDB.id (通常转为字符串)"
    )

    @classmethod
    def from_entity(cls, entity: "AccountInDB") -> "AccountSchema":
        """从数据库实体转换为响应模型"""
        return cls(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            gender=entity.gender,
            phone=entity.phone,
        )


class LoginRequest(BaseModel):
    """登录请求模型

    用于验证用户登录请求的数据。
    允许使用用户名或邮箱进行登录。
    """

    username: Optional[str] = Field(None, description="用户名，与邮箱至少提供一个")
    email: Optional[EmailStr] = Field(
        None, description="电子邮箱，与用户名至少提供一个"
    )
    password_hashed: str = Field(
        ...,
        min_length=6,
        description="密码（已哈希 sha256），对应 AccountInDB.password (需要验证)",
    )

    @model_validator(mode="before")
    def check_username_or_email(cls, values: dict) -> dict:
        """验证用户名或邮箱至少有一个不为空"""
        username = values.get("username")
        email = values.get("email")
        if not username and not email:
            raise ValueError("用户名和邮箱不能同时为空")
        # 注意：实际登录逻辑中需要根据提供的是用户名还是邮箱来查询数据库
        return values


class LoginResponse(BaseModel):
    """登录响应模型

    包含登录成功后返回的认证令牌和用户信息。
    """

    token: str = Field(..., description="用户认证令牌，对应 AccountTokenInDB.token")
