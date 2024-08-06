from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column


from ._base_model import DBBaseModel


class Status(Enum):
    # 未知
    UNKNOWN = "UNKNOWN"
    # 试用期
    PROBATION = "PROBATION"
    # 正式员工
    FORMAL = "FORMAL"
    # 离职
    RESIGN = "RESIGN"


# 我们通过这个表来表示公司和员工的关系
# 例如员工是何时加入公司的，试用期是多久, 合同是多久，离职时间等
class CompanyMapAccountInDB(DBBaseModel):
    __tablename__ = "account_company_rel"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="db_account_company_rel_id_seq"),
        primary_key=True,
        comment="account_company_rel id",
    )

    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("company.id"),
        nullable=False,
        comment="company id",
    )

    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.id"),
        nullable=False,
        comment="account id",
    )

    status: Mapped[Status] = mapped_column(
        String(64), nullable=False, default=Status.UNKNOWN, comment="员工状态"
    )

    # 合约开始时间
    contract_start_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="合约开始时间"
    )
    # 合同到期
    contract_end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="合同到期"
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
        /,
        company_id: int,
        account_id: int,
        status: Status = Status.UNKNOWN,
        contract_start_at: Optional[datetime] = None,
        contract_end_at: Optional[datetime] = None,
    ) -> None:
        self.company_id = company_id
        self.account_id = account_id
        self.status = status
        self.contract_start_at = contract_start_at
        self.contract_end_at = contract_end_at
