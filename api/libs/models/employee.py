from typing import TYPE_CHECKING, Optional
from datetime import date
from sqlalchemy.orm import Mapped
from sqlalchemy import Column, Integer, SMALLINT, String, ForeignKey, Date, JSON
from extensions.ext_database import db
from .base import BaseModel
from .json_schema import JsonSchemaInDB

if TYPE_CHECKING:
    from .department import DepartmentInDB
    from .employee_position import EmployeePositionInDB
    from .company import CompanyInDB


class EmployeeInDB(BaseModel):
    """员工信息数据库模型
    存储员工详细信息及其与公司、部门和职位的关系

    属性:
        name (str): 员工姓名，必填
        company_id (int): 所属公司ID，必填
        email (str): 电子邮箱地址
        phone (str): 联系电话
        birthdate (date): 出生日期
        address (str): 居住地址
        gender (int): 性别，0-未知，1-男，2-女
        extra_value (JSON): 附加JSON格式数据
        extra_schema_id (int): 关联的JSON Schema ID
        extra_schema (JsonSchemaInDB): 关联的JSON Schema对象
        positions (list): 员工担任的职位列表
        led_departments (list): 员工作为负责人的部门列表
    """

    __tablename__ = "employee"  # 表名

    company_id: Mapped[int] = Column(
        Integer,
        ForeignKey("company.id"),
        nullable=False,  # 不允许为空，员工必须属于某个公司
        comment="所属公司ID",
    )
    name: Mapped[str] = Column(
        String(255),
        nullable=False,  # 不允许为空，员工必须有姓名
        comment="员工姓名",
    )
    email: Mapped[Optional[str]] = Column(
        String(255),
        nullable=True,  # 允许为空，邮箱是可选的
        comment="电子邮箱地址",
    )
    phone: Mapped[Optional[str]] = Column(
        String(20),
        nullable=True,  # 允许为空，电话是可选的
        comment="联系电话",
    )
    birthdate: Mapped[Optional[date]] = Column(
        Date,
        nullable=True,  # 允许为空，出生日期是可选的
        comment="出生日期",
    )
    address: Mapped[Optional[str]] = Column(
        String(255),
        nullable=True,  # 允许为空，地址是可选的
        comment="居住地址",
    )
    gender: Mapped[Optional[int]] = Column(
        SMALLINT,
        nullable=True,  # 允许为空，性别是可选的
        comment="性别，0-未知，1-男，2-女",
    )
    extra_value: Mapped[Optional[dict]] = Column(
        JSON,
        nullable=True,  # 允许为空，附加数据是可选的
        comment="附加JSON格式数据",
    )
    extra_schema_id: Mapped[Optional[int]] = Column(
        Integer,
        ForeignKey("json_schemas.id"),
        nullable=True,  # 允许为空，可以没有关联的JSON Schema
        comment="关联的JSON Schema ID",
    )

    # 关系定义
    extra_schema: Mapped["JsonSchemaInDB"] = db.relationship(
        "JsonSchemaInDB",
        foreign_keys=[extra_schema_id],  # 指定外键
    )
    positions: Mapped[list["EmployeePositionInDB"]] = db.relationship(
        "EmployeePositionInDB",
        back_populates="employee",  # 与EmployeePositionInDB中的employee属性相对应
        overlaps="members",  # 添加这个参数
    )
    led_departments: Mapped[list["DepartmentInDB"]] = db.relationship(
        "DepartmentInDB",
        back_populates="leader",  # 与DepartmentInDB中的leader属性相对应
    )

    # 添加缺失的多对多关系定义
    companies: Mapped[list["CompanyInDB"]] = db.relationship(
        "CompanyInDB",
        secondary="employee_position",  # 指定中间表
        back_populates="members",  # 与CompanyInDB.members对应
        overlaps="positions",  # 添加这个参数
    )
