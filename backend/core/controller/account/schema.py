from typing import Optional
from pydantic import BaseModel, Field

from core.database import UserStatus


class AccountSchema(BaseModel):
    """
    AccountSchema类表示账户数据的模式。

    属性:
        id (Optional[int]): 账户的ID。
        username (Optional[str]): 账户的用户名。
        phone (Optional[str]): 账户的电话号码。
        email (Optional[str]): 账户的电子邮件地址。
        status (Optional[UserStatus]): 账户的状态。
    """

    id: Optional[int]
    username: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    status: Optional[UserStatus]


class InsertAccountPayload(BaseModel):
    """
    创建账户的载荷模型。

    属性:
    - id (Optional[int]): 账户的ID。
    - username (Optional[str]): 用户名，可选，长度在4到64之间。
    - phone (Optional[str]): 手机号码，可选，长度为11。
    - email (Optional[str]): 电子邮件，可选，长度在6到100之间。
    - password (str): 密码，长度在6到32之间。
    """

    id: Optional[int] = Field(None, description="账户的ID")
    username: Optional[str] = Field(None, min_length=4, max_length=64)
    phone: Optional[str] = Field(None, min_length=11, max_length=11)
    email: Optional[str] = Field(None, min_length=6, max_length=100)
    password: str = Field(..., min_length=6, max_length=32)


class LoginAccountPayload(BaseModel):
    """
    登录账户的有效载荷模型。

    属性:
        email (str): 邮箱地址，长度在4到64个字符之间。
        password (str): 密码，长度在6到32个字符之间。
    """

    email: str = Field(..., min_length=4, max_length=64)
    password: str = Field(..., min_length=6, max_length=32)


class LoginAccountResp(BaseModel):
    """
    LoginAccountResp 类是用于表示登录账户响应的模型。

    属性:
        token (str): 登录账户的令牌。
        account (AccountSchema): 登录账户的信息。

    """

    token: str
    account: AccountSchema
