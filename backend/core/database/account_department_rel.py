from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Sequence
from sqlalchemy.orm import Mapped, mapped_column


from ._base_model import DBBaseModel


# 我们通过这个表来表示部门和员工的关系
# 例如 一个用户可能在多个部门工作
# 一个部门可能有多个用户
class DepartmentMapAccountInDB(DBBaseModel):
    __tablename__ = "account_department_rel"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence(start=1, increment=1, name="db_account_department_rel_id_seq"),
        primary_key=True,
        comment="account_department_rel id",
    )

    department_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("department.id"),
        nullable=False,
        comment="department id",
    )

    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.id"),
        nullable=False,
        comment="account id",
    )
    # 职位
    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("company_job.id"),
        nullable=False,
        comment="job id",
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

    def __init__(self, department_id: int, account_id: int, job_id: int) -> None:
        self.department_id = department_id
        self.account_id = account_id
        self.job_id = job_id
