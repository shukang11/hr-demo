from enum import StrEnum
from typing import TYPE_CHECKING
from extensions.ext_database import db
from .base import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, MappedColumn

if TYPE_CHECKING:
    from .company import CompanyInDB
    from .account import AccountInDB


class AccountCompanyRole(StrEnum):
    """账户-公司关联角色
    定义了账户在公司中所扮演的角色类型。

    Attributes:
        OWNER (str): 公司所有者，拥有最高权限。
        ADMIN (str): 公司管理员，拥有管理权限。
        USER (str): 普通用户，拥有基本操作权限。
    """

    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"


class AccountCompanyInDB(BaseModel):
    """账户-公司关联数据库模型
    存储账户与公司的多对多关系，并定义账户在每个公司中的角色。
    这个模型是连接 `accounts` 表和 `company` 表的中间表。

    Attributes:
        account_id (int): 账户ID，外键关联到 `accounts` 表的 `id` 字段，不可为空。
        company_id (int): 公司ID，外键关联到 `company` 表的 `id` 字段，不可为空。
        role (AccountCompanyRole): 用户在该公司中的角色，使用 `AccountCompanyRole` 枚举类型，存储为字符串，不可为空。
        account (AccountInDB): 与 `AccountInDB` 模型建立的多对一关系，通过 `account_id` 关联。
                               `back_populates="companies"` 指定了在 `AccountInDB` 模型中反向关联的属性名。
        company (CompanyInDB): 与 `CompanyInDB` 模型建立的多对一关系，通过 `company_id` 关联。

    Constraints:
        UniqueConstraint("account_id", "company_id", name="uix_account_company"):
            确保每个账户在同一个公司中只有一个唯一的关联记录（即一个账户在一个公司只能有一个角色）。
    """

    __tablename__ = "account_company"

    account_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("accounts.id"),
        nullable=False,
        comment="账户ID，关联 accounts.id",
    )
    company_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("company.id"),
        nullable=False,
        comment="公司ID，关联 company.id",
    )
    role: Mapped[AccountCompanyRole] = MappedColumn(
        String(32), nullable=False, comment="账户在该公司中的角色 (owner, admin, user)"
    )

    # Relationships
    # 定义与 AccountInDB 的多对一关系
    # back_populates 指向 AccountInDB 模型中名为 'account_companies' 的关系属性
    account: Mapped["AccountInDB"] = db.relationship(
        "AccountInDB",
        back_populates="account_companies",
        overlaps="accounts,companies",  # 添加这个参数
    )  # type: ignore
    # 定义与 CompanyInDB 的多对一关系
    # back_populates 指向 CompanyInDB 模型中名为 'account_companies' 的关系属性
    company: Mapped["CompanyInDB"] = db.relationship(
        "CompanyInDB",
        back_populates="account_companies",
        overlaps="accounts,companies",  # 添加这个参数
    )  # type: ignore

    # 表级约束
    __table_args__ = (
        # 账户ID和公司ID的组合必须唯一，确保一个账户在一个公司只有一个角色
        UniqueConstraint("account_id", "company_id", name="uix_account_company"),
        {"comment": "账户与公司的关联表，定义账户在公司中的角色"},  # 添加表注释
    )

    def __init__(
        self,
        account_id: int,
        company_id: int,
        role: AccountCompanyRole,
    ) -> None:
        """初始化账户-公司关联模型

        Args:
            account_id (int): 账户ID
            company_id (int): 公司ID
            role (AccountCompanyRole): 账户在公司中的角色
        """
        super().__init__()
        self.account_id = account_id
        self.company_id = company_id
        self.role = role
