from typing import TYPE_CHECKING, Optional
from extensions.ext_database import db
from .base import BaseModel
from sqlalchemy.orm import Mapped
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Text

if TYPE_CHECKING:
    from .json_schema import JsonSchemaInDB
    from .department import DepartmentInDB
    from .employee_position import PositionInDB
    from .employee import EmployeeInDB


class CompanyInDB(BaseModel):
    """公司信息数据库模型
    存储公司基本信息及其与其他实体的关系

    属性:
        name (str): 公司名称，必填
        extra_value (JSON): 附加JSON格式数据
        extra_schema_id (int): 关联的JSON Schema ID
        extra_schema (JsonSchemaInDB): 关联的JSON Schema对象
        departments (list): 公司部门列表
        positions (list): 公司职位列表
        schemas (list): 公司拥有的JSON Schema列表
        description (str): 公司描述
    """

    __tablename__ = "company"  # 表名

    name: Mapped[str] = Column(
        String(255),
        nullable=False,  # 不允许为空，公司必须有名称
        comment="公司名称",
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
    description: Mapped[Optional[str]] = Column(
        Text,
        nullable=True,
        comment="公司描述",
    )

    # 关系定义
    extra_schema: Mapped["JsonSchemaInDB"] = db.relationship(
        "JsonSchemaInDB",
        foreign_keys=[extra_schema_id],  # 指定外键
    )
    departments: Mapped[list["DepartmentInDB"]] = db.relationship(
        "DepartmentInDB",
        back_populates="company",  # 与DepartmentInDB中的company属性相对应
    )
    positions: Mapped[list["PositionInDB"]] = db.relationship(
        "PositionInDB",
        back_populates="company",  # 与PositionInDB中的company属性相对应
    )

    members: Mapped[list["EmployeeInDB"]] = db.relationship(
        "EmployeeInDB",
        secondary="employee_position",  # 关联表
        back_populates="companies",  # 与EmployeeInDB中的companies属性相对应
    )
