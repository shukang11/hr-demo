from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, Sequence, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column


from ._base_model import DBBaseModel


# 招聘面试记录
class AccountInterviewRecordInDB(DBBaseModel):
    __tablename__ = "account_interview_record"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="db_account_interview_record_id_seq"),
        primary_key=True,
        comment="account_interview_record id",
    )

    account_id: Mapped[Optional[int]] = mapped_column(
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

    interview_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="面试时间"
    )

    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )

    # 是否通过面试
    is_pass: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否通过面试"
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
        account_id: int,
        company_id: int,
        job_id: int,
        interview_at: datetime,
        remark: Optional[str] = None,
        is_pass: bool = False,
    ) -> None:
        self.account_id = account_id
        self.company_id = company_id
        self.job_id = job_id
        self.interview_at = interview_at
        self.is_pass = is_pass
        self.remark = remark
