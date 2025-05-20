from typing import TYPE_CHECKING, Optional
from datetime import datetime
from extensions.ext_database import db
from .base import BaseModel
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from .company import CompanyInDB
    from .employee_position import EmployeePositionInDB  # 修正导入


class PositionInDB(BaseModel):
    """职位信息数据库模型
    存储职位信息及其与公司的关系

    属性:
        name (str): 职位名称，必填
        company_id (int): 公司ID，必填
        remark (str): 备注信息，可选
        company (CompanyInDB): 关联的公司对象
        employee_positions (list): 该职位关联的员工-职位列表
    """

    __tablename__ = "position"  # 表名

    name: Mapped[str] = db.Column(
        db.String(64),
        nullable=False,  # 不允许为空，职位必须有名称
        comment="职位名称",
    )
    company_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False,  # 不允许为空，职位必须关联到一个公司
        comment="所属公司ID",
    )
    remark: Mapped[Optional[str]] = db.Column(
        db.String(255),
        nullable=True,  # 允许为空，备注是可选的
        comment="备注信息",
    )

    # 关系定义
    company: Mapped["CompanyInDB"] = db.relationship(
        "CompanyInDB",
        back_populates="positions",  # 与CompanyInDB中的positions属性相对应
    )  # type: ignore
    employee_positions: Mapped[list["EmployeePositionInDB"]] = db.relationship(
        "EmployeePositionInDB",
        back_populates="position",  # 与EmployeePositionInDB中的position属性相对应
    )  # type: ignore

    def __init__(
        self,
        name: str,
        company_id: int,
        remark: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.company_id = company_id
        self.remark = remark
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
