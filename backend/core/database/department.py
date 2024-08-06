from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from ._base_model import DBBaseModel
from .account_department_rel import DepartmentMapAccountInDB  # noqa: F401

if TYPE_CHECKING:
    from .account import AccountInDB


class DepartmentInDB(DBBaseModel):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="db_company_id_seq"),
        primary_key=True,
        comment="company id",
    )

    name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="company name"
    )

    # 上级部门, 如果没有上一级了，那么就是公司的第一级部门
    parent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("department.id"),
        nullable=True,
        comment="上级部门",
    )

    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("company.id"),
        nullable=False,
        comment="company id",
    )

    leader_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.id"),
        nullable=False,
        comment="部门负责人, 指向的是雇员",
    )

    # 通过 `account_department_rel` 中间表来关联
    members: Mapped[List["AccountInDB"]] = relationship(
        "AccountInDB",
        secondary="account_department_rel",
        back_populates="departments",
    )

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

    def __init__(
        self,
        name: str,
        company_id: int,
        leader_id: int,
        parent_id: Optional[int] = None,
    ) -> None:
        self.name = name
        self.company_id = company_id
        self.leader_id = leader_id
        self.parent_id = parent_id
