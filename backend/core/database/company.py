from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column


from ._base_model import DBBaseModel


class CompanyStatus(Enum):
    # 存续
    ACTIVE = "ACTIVE"
    # 公司注销
    INACTIVE = "INACTIVE"
    # 异常
    EXCEPTION = "EXCEPTION"


class CompanyInDB(DBBaseModel):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="db_company_id_seq"),
        primary_key=True,
        comment="company id",
    )

    name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="company name"
    )

    admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.id"),
        nullable=False,
        comment="最高管理员, 企业的创建者， 这里指向的是自然人",
    )

    status: Mapped[CompanyStatus] = mapped_column(
        String(64), nullable=False, default=CompanyStatus.ACTIVE, comment="公司 状态"
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

    def __init__(self, name: str, admin_id: int) -> None:
        self.name = name
        self.admin_id = admin_id
