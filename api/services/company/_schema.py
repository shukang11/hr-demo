from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """公司基础数据模型"""

    name: str = Field(..., description="公司名称")
    extra_value: Optional[Dict[str, Any]] = Field(None, description="附加JSON格式数据")
    extra_schema_id: Optional[int] = Field(None, description="关联的JSON Schema ID")
    description: Optional[str] = Field(None, description="公司描述")


class CompanyCreate(CompanyBase):
    """创建公司请求模型"""

    pass


class CompanyUpdate(BaseModel):
    """更新公司请求模型"""

    name: Optional[str] = Field(None, description="公司名称")
    extra_value: Optional[Dict[str, Any]] = Field(None, description="附加JSON格式数据")
    extra_schema_id: Optional[int] = Field(None, description="关联的JSON Schema ID")
    description: Optional[str] = Field(None, description="公司描述")


class CompanySchema(CompanyBase):
    """API响应的公司数据模型"""

    id: int = Field(..., description="公司ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        orm_mode = True
        from_attributes = True
