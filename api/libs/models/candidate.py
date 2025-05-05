from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, JSON
from sqlalchemy.orm import Mapped
from extensions.ext_database import db
from .base import BaseModel
import enum

if TYPE_CHECKING:
    from .json_schema import JsonSchemaInDB
    from .company import CompanyInDB
    from .position import PositionInDB
    from .department import DepartmentInDB
    from .employee import EmployeeInDB


# 候选人状态枚举
class CandidateStatus(str, enum.Enum):
    PENDING = "Pending"  # 待处理
    SCHEDULED = "Scheduled"  # 已安排面试
    INTERVIEWED = "Interviewed"  # 已面试
    ACCEPTED = "Accepted"  # 已通过
    REJECTED = "Rejected"  # 已拒绝
    WITHDRAWN = "Withdrawn"  # 已撤回


class CandidateInDB(BaseModel):
    """候选人信息数据库模型
    存储招聘候选人信息及其与公司、部门、职位的关系

    属性:
        company_id (int): 公司ID，必填
        name (str): 候选人姓名，必填
        phone (str): 联系电话，可选
        email (str): 电子邮箱，可选
        position_id (int): 应聘职位ID，必填
        department_id (int): 目标部门ID，必填
        interview_date (datetime): 面试日期，必填
        status (CandidateStatus): 候选人状态，默认为待处理
        interviewer_id (int): 面试官ID，可选
        evaluation (str): 面试评价，可选
        remark (str): 备注信息，可选
        extra_value (JSON): 附加JSON格式数据，可选
        extra_schema_id (int): 关联的JSON Schema ID，可选

        company (CompanyInDB): 关联的公司对象
        position (PositionInDB): 关联的职位对象
        department (DepartmentInDB): 关联的部门对象
        interviewer (EmployeeInDB): 关联的面试官对象
        extra_schema (JsonSchemaInDB): 关联的JSON Schema对象
    """

    __tablename__ = "candidate"  # 表名

    company_id: Mapped[int] = Column(
        Integer, ForeignKey("company.id"), nullable=False, comment="公司ID"
    )
    name: Mapped[str] = Column(String(64), nullable=False, comment="候选人姓名")
    phone: Mapped[Optional[str]] = Column(String(20), nullable=True, comment="联系电话")
    email: Mapped[Optional[str]] = Column(
        String(255), nullable=True, comment="电子邮箱"
    )
    position_id: Mapped[int] = Column(
        Integer, ForeignKey("position.id"), nullable=False, comment="应聘职位ID"
    )
    department_id: Mapped[int] = Column(
        Integer, ForeignKey("department.id"), nullable=False, comment="目标部门ID"
    )
    interview_date: Mapped[datetime] = Column(
        DateTime, nullable=False, comment="面试日期"
    )
    status: Mapped[CandidateStatus] = Column(
        Enum(CandidateStatus),
        nullable=False,
        default=CandidateStatus.PENDING,
        comment="候选人状态",
    )
    interviewer_id: Mapped[Optional[int]] = Column(
        Integer, ForeignKey("employee.id"), nullable=True, comment="面试官ID"
    )
    evaluation: Mapped[Optional[str]] = Column(Text, nullable=True, comment="面试评价")
    remark: Mapped[Optional[str]] = Column(
        String(255), nullable=True, comment="备注信息"
    )
    extra_value: Mapped[Optional[dict]] = Column(
        JSON, nullable=True, comment="附加JSON格式数据"
    )
    extra_schema_id: Mapped[Optional[int]] = Column(
        Integer,
        ForeignKey("json_schemas.id"),
        nullable=True,
        comment="关联的JSON Schema ID",
    )

    # 关系定义
    company: Mapped["CompanyInDB"] = db.relationship(
        "CompanyInDB", foreign_keys=[company_id]
    )
    position: Mapped["PositionInDB"] = db.relationship(
        "PositionInDB", foreign_keys=[position_id]
    )
    department: Mapped["DepartmentInDB"] = db.relationship(
        "DepartmentInDB", foreign_keys=[department_id]
    )
    interviewer: Mapped[Optional["EmployeeInDB"]] = db.relationship(
        "EmployeeInDB", foreign_keys=[interviewer_id]
    )
    extra_schema: Mapped[Optional["JsonSchemaInDB"]] = db.relationship(
        "JsonSchemaInDB", foreign_keys=[extra_schema_id]
    )
