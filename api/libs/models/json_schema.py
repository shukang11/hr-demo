from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy import Column, String, JSON
from .base import BaseModel


class JsonSchemaInDB(BaseModel):
    """JSON Schema 数据库模型，用于存储和管理 JSON 数据结构模式

    属性:
        name (str): Schema 名称，必填
        schema (JSON): JSON Schema 定义，必填
        company_id (int): 所属公司 ID，可选
        remark (str): 备注信息，可选
        company (CompanyInDB): 关联的公司对象
    """

    __tablename__ = "json_schemas"

    name: Mapped[str] = Column(String(255), nullable=False, comment="Schema 名称")
    schema: Mapped[dict] = Column(JSON, nullable=False, comment="JSON Schema 定义")
    remark: Mapped[Optional[str]] = Column(
        String(255),
        nullable=True,  # 允许为空，备注是可选的
        comment="备注信息",
    )
