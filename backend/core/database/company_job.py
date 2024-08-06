from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column


from ._base_model import DBBaseModel


class CompanyJobInDB(DBBaseModel):
    __tablename__ = "company_job"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="db_company_job_id_seq"),
        primary_key=True,
        comment="company job id",
    )

    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("company.id"),
        nullable=False,
        comment="company id",
    )

    job_name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="company job name"
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

    def __init__(self, job_name: str, company_id: int) -> None:
        self.job_name = job_name
        self.company_id = company_id
