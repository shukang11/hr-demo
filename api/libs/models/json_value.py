from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy import Column, String, JSON
from .base import BaseModel


class JsonValueInDB(BaseModel):
    __tablename__ = "json_values"

    value: Mapped[dict] = Column(
        JSON,
        nullable=False,  # 不允许为空，值是必填的
        comment="JSON值",
    )

    remark: Mapped[Optional[str]] = Column(
        String(255),
        nullable=True,  # 允许为空，备注是可选的
        comment="备注信息",
    )
