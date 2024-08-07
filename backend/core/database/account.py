from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import SMALLINT, DateTime, ForeignKey, Integer, Sequence, String, select
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship

from core.utils import getmd5

from ._base_model import DBBaseModel

from .account_department_rel import DepartmentMapAccountInDB  # noqa: F401

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from .department import DepartmentInDB


class UserStatus(IntEnum):
    # 状态 0 正常 1 禁用
    NORMAL = 0
    DISABLE = 1


class AccountTokenInDB(DBBaseModel):
    __tablename__ = "account_token"

    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.id"),
        nullable=False,
        primary_key=True,
        comment="account token id",
    )
    token: Mapped[str] = mapped_column(String(32), nullable=False, comment="token")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    def __init__(self, user_id: int, token: str) -> None:
        self.user_id = user_id
        self.token = token

    def __repr__(self):
        return f"<AccountToken(user_id='{self.user_id}', token='{self.token}')>"


class AccountInDB(DBBaseModel):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="db_account_id_sep"),
        primary_key=True,
        comment="account id",
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="用户名"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(11), nullable=True, comment="手机号"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="邮箱"
    )
    password: Mapped[str] = mapped_column(String(32), nullable=False, comment="密码")
    status: Mapped[UserStatus] = mapped_column(
        SMALLINT, nullable=False, default=0, comment="状态 0 正常 1 禁用"
    )
    create_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, comment="创建时间"
    )
    update_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    token: Mapped[Optional[AccountTokenInDB]] = relationship(
        "AccountTokenInDB", backref="account", uselist=False
    )

    # 通过 `account_department_rel` 中间表来关联
    departments: Mapped[List["DepartmentInDB"]] = relationship(
        "DepartmentInDB",
        secondary="account_department_rel",
        back_populates="members",
    )

    def __init__(
        self,
        phone: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.username = username
        self.email = email
        self.phone = phone
        self.password = password

    @classmethod
    def find_by_username(
        cls, session: "Session", username: str
    ) -> Optional["AccountInDB"]:
        stmt = select(cls).where(cls.username == username)
        result = session.scalar(stmt)
        return result

    @classmethod
    def find_by_id(cls, session: "Session", user_id: int) -> Optional["AccountInDB"]:
        stmt = select(cls).where(cls.id == user_id)
        result = session.scalar(stmt)
        return result

    @classmethod
    def find_by_token(cls, session: "Session", token: str) -> Optional["AccountInDB"]:
        stmt = (
            select(cls)
            .join(AccountTokenInDB, cls.id == AccountTokenInDB.account_id)
            .options(joinedload(cls.token))
            .where(AccountTokenInDB.token == token)
        )
        result = session.scalar(stmt)
        return result

    def __repr__(self):
        return f"<Account(id='{self.id}', username='{self.username}')>"

    def make_new_token(self, salt: str) -> str:
        raw = f"{self.id}{self.password}{salt}"
        md5_value = getmd5(raw)
        return md5_value
