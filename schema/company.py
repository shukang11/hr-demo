from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CompanyBase(BaseModel):
    """公司基础信息模型
    
    包含公司的基本属性，用作其他公司相关模型的基类
    """
    name: str = Field(..., description="公司名称")
    description: Optional[str] = Field(None, description="公司描述")

class CompanyCreate(CompanyBase):
    """公司创建模型
    
    用于创建新公司时的请求数据验证
    """
    pass

class CompanyUpdate(CompanyBase):
    """公司更新模型
    
    用于更新公司信息时的请求数据验证，所有字段都是可选的
    """
    name: Optional[str] = Field(None, description="公司名称")

class CompanyInResponse(CompanyBase):
    """公司响应模型
    
    用于序列化返回给客户端的公司信息
    """
    id: int = Field(..., description="公司唯一标识符")
    name: str = Field(..., description="公司名称")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attribute = True
