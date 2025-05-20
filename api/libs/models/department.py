from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, MappedColumn, relationship
from extensions.ext_database import db
from .base import BaseModel

if TYPE_CHECKING:
    from .company import CompanyInDB
    from .employee import EmployeeInDB
    from .employee_position import EmployeePositionInDB


class DepartmentInDB(BaseModel):
    """部门信息数据库模型
    存储部门信息及其与公司和员工的关系，支持树形结构

    属性:
        parent_id (int): 父部门ID，用于树形结构
        company_id (int): 公司ID，必填
        name (str): 部门名称，必填
        leader_id (int): 部门负责人ID
        remark (str): 备注信息
        parent (DepartmentInDB): 父部门对象
        children (list): 子部门列表
        company (CompanyInDB): 关联的公司对象
        leader (EmployeeInDB): 部门负责人对象
        employee_positions (list): 部门内的员工-职位关联列表
    """

    __tablename__ = "department"  # 表名

    id: Mapped[int] = MappedColumn(
        Integer,
        primary_key=True,
        autoincrement=True,  # 自增主键
        comment="部门ID",
    )

    parent_id: Mapped[Optional[int]] = MappedColumn(
        Integer,
        ForeignKey("department.id"),
        nullable=True,  # 允许为空，因为顶级部门没有父部门
        comment="父部门ID",
    )
    company_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("company.id"),
        nullable=False,  # 不允许为空，每个部门必须属于一个公司
        comment="所属公司ID",
    )
    name: Mapped[str] = MappedColumn(
        String(64),
        nullable=False,  # 不允许为空，部门必须有名称
        comment="部门名称",
    )
    leader_id: Mapped[Optional[int]] = MappedColumn(
        Integer,
        ForeignKey("employee.id"),
        nullable=True,  # 允许为空，部门可以暂时没有负责人
        comment="部门负责人ID",
    )
    remark: Mapped[Optional[str]] = MappedColumn(
        String(255),
        nullable=True,  # 允许为空，备注是可选的
        comment="备注信息",
    )

    # 添加父部门和子部门的自引用关系
    # 使用lambda延迟计算，确保类完全定义后再引用其属性
    parent: Mapped[Optional["DepartmentInDB"]] = relationship(
        "DepartmentInDB",
        remote_side=lambda: [DepartmentInDB.id],
        back_populates="children",
        foreign_keys=[parent_id],
        uselist=False,  # 设置为False表示这是单一对象关系
    )
    children: Mapped[List["DepartmentInDB"]] = relationship(
        "DepartmentInDB",
        back_populates="parent",
        foreign_keys=[parent_id],
        cascade="all, delete-orphan",
    )

    company: Mapped["CompanyInDB"] = db.relationship(
        "CompanyInDB",
        back_populates="departments",  # 与CompanyInDB中的departments属性相对应
    )  # type: ignore
    leader: Mapped[Optional["EmployeeInDB"]] = db.relationship(
        "EmployeeInDB",
        back_populates="led_departments",  # 与EmployeeInDB中的led_departments属性相对应
    )  # type: ignore
    employee_positions: Mapped[list["EmployeePositionInDB"]] = db.relationship(
        "EmployeePositionInDB",
        back_populates="department",  # 与EmployeePositionInDB中的department属性相对应
    )  # type: ignore

    def __init__(
        self,
        name: str,
        company_id: int,
        parent_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.company_id = company_id
        self.parent_id = parent_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
