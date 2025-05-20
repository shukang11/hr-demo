from typing import TYPE_CHECKING, Optional
from datetime import date, datetime  # 添加日期导入
from sqlalchemy import Integer, String, ForeignKey, Date
from sqlalchemy.orm import Mapped, MappedColumn
from extensions.ext_database import db
from .base import BaseModel

if TYPE_CHECKING:
    from .company import CompanyInDB
    from .employee import EmployeeInDB
    from .department import DepartmentInDB
    from .position import PositionInDB  # 添加缺失的导入


class EmployeePositionInDB(BaseModel):
    """Employee-Position association database model
    员工-职位关联数据库模型
    存储员工和职位之间的多对多关系以及附加信息

    Attributes:
        employee_id (int): 员工ID，必填
        company_id (int): 公司ID，必填
        department_id (int): 部门ID，必填
        position_id (int): 职位ID，必填
        start_date (date): 入职时间，可为空
        end_date (date): 离职时间，可为空
        remark (str): 备注，可为空
        employee (EmployeeInDB): 关联的员工对象
        company (CompanyInDB): 关联的公司对象
        department (DepartmentInDB): 关联的部门对象
        position (PositionInDB): 关联的职位对象
    """

    __tablename__ = "employee_position"

    employee_id: Mapped[int] = MappedColumn(
        Integer, ForeignKey("employee.id"), nullable=False, comment="员工ID"
    )
    company_id: Mapped[int] = MappedColumn(
        Integer, ForeignKey("company.id"), nullable=False, comment="公司ID"
    )
    department_id: Mapped[int] = MappedColumn(
        Integer, ForeignKey("department.id"), nullable=False, comment="部门ID"
    )
    position_id: Mapped[int] = MappedColumn(
        Integer, ForeignKey("position.id"), nullable=False, comment="职位ID"
    )

    # 入职时间
    start_date: Mapped[Optional[date]] = MappedColumn(
        Date, nullable=True, comment="入职时间"
    )

    # 离职时间
    end_date: Mapped[Optional[date]] = MappedColumn(
        Date, nullable=True, comment="离职时间"
    )

    remark: Mapped[Optional[str]] = MappedColumn(
        String(255), nullable=True, comment="备注信息"
    )

    # 关联关系
    employee: Mapped["EmployeeInDB"] = db.relationship(
        "EmployeeInDB",
        back_populates="positions",
        overlaps="companies,members",  # 添加这个参数
    )  # type: ignore

    company: Mapped["CompanyInDB"] = db.relationship(
        "CompanyInDB",
        overlaps="companies,members",  # 添加这个参数
    )  # type: ignore

    department: Mapped["DepartmentInDB"] = db.relationship(
        "DepartmentInDB", back_populates="employee_positions"
    )  # type: ignore

    position: Mapped["PositionInDB"] = db.relationship(
        "PositionInDB", back_populates="employee_positions"
    )  # type: ignore

    def __init__(
        self,
        employee_id: int,
        company_id: int,
        department_id: int,
        position_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        remark: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__()
        self.employee_id = employee_id
        self.company_id = company_id
        self.department_id = department_id
        self.position_id = position_id
        self.start_date = start_date
        self.end_date = end_date
        self.remark = remark
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
