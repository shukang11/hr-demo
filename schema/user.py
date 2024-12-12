from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """用户基础信息模型
    
    包含用户的基本属性，用作其他用户相关模型的基类
    """
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="电子邮箱")
    full_name: str = Field(..., description="用户全名")
    is_admin: bool = Field(default=False, description="是否是管理员")

class UserCreate(UserBase):
    """用户创建模型
    
    用于创建新用户时的请求数据验证
    """
    password: str = Field(..., min_length=6, description="用户密码，至少6个字符")

class UserUpdate(BaseModel):
    """用户更新模型
    
    用于更新用户信息时的请求数据验证，所有字段都是可选的
    """
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    full_name: Optional[str] = Field(None, description="用户全名")
    password: Optional[str] = Field(None, min_length=6, description="用户密码，至少6个字符")

class UserInResponse(UserBase):
    """用户响应模型
    
    用于序列化返回给客户端的用户信息
    """
    id: str = Field(..., description="用户唯一标识符")

class LoginRequest(BaseModel):
    """登录请求模型
    
    用于验证用户登录请求的数据
    """
    username: str = Field(..., description="用户名")
    password: str = Field(..., min_length=6, description="密码")

class LoginResponse(BaseModel):
    """登录响应模型
    
    包含登录成功后返回的完整信息
    """
    token: str = Field(..., description="用户认证令牌")
    user: UserInResponse = Field(..., description="用户信息")
