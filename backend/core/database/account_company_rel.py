from enum import Enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, Sequence, String, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship


from ._base_model import DBBaseModel

if TYPE_CHECKING:
    from .account import AccountInDB


class ContractType(Enum):
    # 未知
    UNKNOWN = "UNKNOWN"
    # 试用期
    PROBATION = "PROBATION"
    # 正式员工
    FORMAL = "FORMAL"
    # 离职
    RESIGN = "RESIGN"


class ContractTypeType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if isinstance(value, ContractType):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return ContractType(value)
        return value


class CompanyMapAccountContractInDB(DBBaseModel):
    # 我们通过这个表来表示公司和员工的合约关系
    # 员工可能和公司签订了合约，合约有开始时间和结束时间
    # 如果员工离职，那么合约就会结束
    # 可能会有多个合约，因为员工可能会续签合约
    __tablename__ = "account_company_contract_rel"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="db_account_company_contract_rel_id_seq"),
        primary_key=True,
        comment="account_company_contract_rel id",
    )

    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.id"),
        nullable=False,
        comment="account id",
    )

    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("company.id"),
        nullable=False,
        comment="company id",
    )

    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("company_job.id"),
        nullable=False,
        comment="job id",
    )

    company_map_account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account_company_rel.id"),
        nullable=False,
        comment="company_map_account id",
    )

    contract_type: Mapped[ContractType] = mapped_column(
        ContractTypeType(), nullable=False, comment="合约类型"
    )

    contract_start_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="合约开始时间"
    )

    contract_end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="合约结束时间"
    )

    def __init__(
        self,
        /,
        contract_type: ContractType,
        account_id: int,
        company_id: int,
        job_id: int,
        contract_start_at: Optional[datetime] = None,
        contract_end_at: Optional[datetime] = None,
    ) -> None:
        self.contract_type = contract_type
        self.account_id = account_id
        self.company_id = company_id
        self.job_id = job_id
        self.contract_start_at = contract_start_at
        self.contract_end_at = contract_end_at


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

    contracts: Mapped[List[CompanyMapAccountContractInDB]] = relationship(
        "CompanyMapAccountContractInDB",
        backref="company_map_account",
        cascade="all, delete-orphan",
        lazy="select",
    )

    account: Mapped["AccountInDB"] = relationship(
        "AccountInDB",
        lazy="select",
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
    ) -> None:
        self.company_id = company_id
        self.account_id = account_id
