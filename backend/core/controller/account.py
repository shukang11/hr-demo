from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from core.database import AccountInDB, UserStatus
from core.utils.settings import settings
from core.utils import getmd5


class UserSchema(BaseModel):
    """
    UserSchema class represents the schema for user data.

    Attributes:
        id (Optional[int]): The ID of the user.
        username (Optional[str]): The username of the user.
        phone (Optional[str]): The phone number of the user.
        email (Optional[str]): The email address of the user.
        status (Optional[UserStatus]): The status of the user.
    """

    id: Optional[int]
    username: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    status: Optional[UserStatus]


class RegisterUser(BaseModel):
    username: str = Field(..., min_length=4, max_length=64)
    phone: Optional[str] = Field(..., min_length=11, max_length=11)
    email: Optional[str] = Field(..., min_length=6, max_length=100)
    password: str = Field(..., min_length=6, max_length=32)


def register_user(create_user: RegisterUser, session: Session) -> AccountInDB:
    hashed_password = getmd5(create_user.password)
    # 是否已存在
    exsits_stmt = (
        select(AccountInDB)
        .options(joinedload(AccountInDB.token))
        .where(AccountInDB.username == create_user.username)
    )
    is_exsits = session.scalar(exsits_stmt)
    if is_exsits:
        raise ValueError("用户名已存在")

    # 创建用户
    user = AccountInDB(
        phone=create_user.phone,
        username=create_user.username,
        email=create_user.email,
        password=hashed_password,
    )
    session.add(user)
    return user


class LoginUser(BaseModel):
    username: str = Field(..., min_length=4, max_length=64)
    password: str = Field(..., min_length=6, max_length=32)


class LoginResp(BaseModel):
    token: str
    user: UserSchema


def login_user(login_user: LoginUser, session: Session) -> AccountInDB:
    """
    验证用户，通过检查提供的登录凭据与数据库中的凭据进行比对。

    参数:
        login_user (LoginUser): 用户的登录凭据。
        session (Session): 数据库会话。

    返回:
        AccountInDB: 验证通过的用户。

    异常:
        ValueError: 如果用户名或密码不正确。
    """
    hashed_password = login_user.password
    stmt = (
        select(AccountInDB)
        .options(joinedload(AccountInDB.token))
        .where(
            AccountInDB.username == login_user.username,
            AccountInDB.password == hashed_password,
        )
    )
    result = session.execute(stmt)

    user = result.scalar()

    if not user:
        raise ValueError("用户名或密码错误")

    # 更新用户token

    new_token = user.make_new_token(settings.SECRET_KEY)
    user.token.token = new_token
    session.add(user)

    return user


def user_count(session: Session) -> int:
    count_stmt = select(func.count()).with_only_columns(AccountInDB)
    result = session.execute(count_stmt)
    count = result.scalar()
    return count
