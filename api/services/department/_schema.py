from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# 部门基础数据模型，包含公共字段
class DepartmentBase(BaseModel):
    """部门基础信息
    
    包含部门的基本字段，用于创建和更新操作的共享属性
    """
    name: str = Field(..., description="部门名称")
    company_id: int = Field(..., description="所属公司ID")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    leader_id: Optional[int] = Field(None, description="部门负责人ID")
    remark: Optional[str] = Field(None, description="部门描述")

# 创建部门请求模型
class DepartmentCreate(DepartmentBase):
    """创建部门请求模型
    
    用于验证创建部门时的请求数据
    """
    pass

# 更新部门请求模型，所有字段都是可选的
class DepartmentUpdate(BaseModel):
    """更新部门请求模型
    
    用于验证更新部门时的请求数据，所有字段均为可选
    """
    name: Optional[str] = Field(None, description="部门名称")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    leader_id: Optional[int] = Field(None, description="部门负责人ID")
    remark: Optional[str] = Field(None, description="部门描述")

# 部门响应模型
class DepartmentSchema(DepartmentBase):
    """部门响应模型
    
    用于序列化返回给客户端的部门数据
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True