from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, MappedColumn, relationship
from sqlalchemy import Column, String, JSON, Integer, ForeignKey
from extensions.ext_database import db
from .base import BaseModel

if TYPE_CHECKING:
    from .json_schema import JsonSchemaInDB


class JsonValueInDB(BaseModel):
    """JSON值存储模型，用于存储自定义字段的值

    属性:
        schema_id (int): 关联的 JSON Schema ID
        entity_id (int): 关联的实体ID，如员工ID、候选人ID等
        entity_type (str): 关联的实体类型，如"employee"、"candidate"等
        value (dict): JSON格式的数据值
        remark (str): 备注信息
        schema (JsonSchemaInDB): 关联的JSON Schema对象
    """

    __tablename__ = "json_values"

    schema_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("json_schemas.id"),
        nullable=False,
        comment="关联的JSON Schema ID",
    )
    entity_id: Mapped[int] = MappedColumn(
        Integer, nullable=False, comment="关联的实体ID，如员工ID、候选人ID等"
    )
    entity_type: Mapped[str] = MappedColumn(
        String(50),
        nullable=False,
        comment="关联的实体类型，如'employee'、'candidate'等",
    )
    value: Mapped[dict] = MappedColumn(JSON, nullable=False, comment="JSON值")
    remark: Mapped[Optional[str]] = MappedColumn(
        String(255), nullable=True, comment="备注信息"
    )

    # 关系定义
    schema: Mapped["JsonSchemaInDB"] = relationship(
        "JsonSchemaInDB", foreign_keys=[schema_id]
    )

    # 索引以优化查询性能
    __table_args__ = (
        db.Index("ix_json_value_entity", "entity_type", "entity_id"),
        db.Index("ix_json_value_schema", "schema_id"),
    )

    def __init__(
        self,
        schema_id: int,
        entity_id: int,
        entity_type: str,
        value: dict,
        remark: Optional[str] = None,
    ):
        """初始化JSON值存储模型

        Args:
            schema_id (int): 关联的 JSON Schema ID
            entity_id (int): 关联的实体ID
            entity_type (str): 关联的实体类型
            value (dict): JSON格式的数据值
            remark (Optional[str]): 备注信息
        """
        super().__init__()
        self.schema_id = schema_id
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.value = value
        self.remark = remark
