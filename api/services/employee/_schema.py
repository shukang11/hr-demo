from typing import Optional, Dict, Any, List
from datetime import date, datetime
from enum import Enum, IntEnum
from pydantic import BaseModel, Field, computed_field


class GenderIntEnum(IntEnum):
    """性别整数枚举（数据库存储用）"""
    UNKNOWN = 0  # 未知
    MALE = 1     # 男
    FEMALE = 2   # 女


class Gender(str, Enum):
    """性别字符串枚举（API接口用）"""
    MALE = "Male"     # 男
    FEMALE = "Female" # 女
    UNKNOWN = "Unknown" # 未知
    
    @classmethod
    def from_int(cls, value: int) -> "Gender":
        """从整数值转换为字符串枚举"""
        if value == 1:
            return cls.MALE
        elif value == 2:
            return cls.FEMALE
        else:
            return cls.UNKNOWN
    
    def to_int(self) -> int:
        """转换为整数值"""
        if self == self.MALE:
            return 1
        elif self == self.FEMALE:
            return 2
        else:
            return 0


class EmployeeBase(BaseModel):
    """员工基础模型，包含共同字段"""
    company_id: int = Field(..., description="公司ID")
    name: str = Field(..., max_length=255, description="员工姓名")
    email: Optional[str] = Field(None, max_length=255, description="电子邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    birthdate: Optional[date] = Field(None, description="出生日期")
    address: Optional[str] = Field(None, max_length=255, description="居住地址")
    gender: Gender = Field(default=Gender.UNKNOWN, description="性别")
    extra_value: Optional[Dict[str, Any]] = Field(None, description="附加JSON格式数据")
    extra_schema_id: Optional[int] = Field(None, description="关联的JSON Schema ID")


class EmployeeCreate(EmployeeBase):
    """创建员工的请求模型"""
    department_id: Optional[int] = Field(None, description="部门ID")
    position_id: Optional[int] = Field(None, description="职位ID")
    entry_date: Optional[date] = Field(None, description="入职日期")
    candidate_id: Optional[int] = Field(None, description="关联的候选人ID")


class EmployeeUpdate(BaseModel):
    """更新员工的请求模型，所有字段可选"""
    company_id: Optional[int] = Field(None, description="公司ID")
    name: Optional[str] = Field(None, max_length=255, description="员工姓名")
    email: Optional[str] = Field(None, max_length=255, description="电子邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    birthdate: Optional[date] = Field(None, description="出生日期")
    address: Optional[str] = Field(None, max_length=255, description="居住地址")
    gender: Optional[Gender] = Field(None, description="性别")
    department_id: Optional[int] = Field(None, description="部门ID")
    position_id: Optional[int] = Field(None, description="职位ID")
    extra_value: Optional[Dict[str, Any]] = Field(None, description="附加JSON格式数据")
    extra_schema_id: Optional[int] = Field(None, description="关联的JSON Schema ID")


class EmployeeSchema(EmployeeBase):
    """员工响应模型，用于API返回"""
    id: int = Field(..., description="员工ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    department_id: Optional[int] = Field(None, description="部门ID")
    position_id: Optional[int] = Field(None, description="职位ID")
    
    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        """重写model_validate方法，处理gender字段的转换"""
        if hasattr(obj, "gender") and isinstance(obj.gender, int):
            # 将整数性别转换为字符串枚举
            obj.gender = Gender.from_int(obj.gender)
        return super().model_validate(obj, *args, **kwargs)


class EmployeePositionBase(BaseModel):
    """员工职位基础模型，包含共同字段"""
    employee_id: int = Field(..., description="员工ID")
    company_id: int = Field(..., description="公司ID")
    department_id: int = Field(..., description="部门ID")
    position_id: int = Field(..., description="职位ID")
    remark: Optional[str] = Field(None, max_length=255, description="备注信息")


class EmployeePositionCreate(EmployeePositionBase):
    """创建员工职位的请求模型"""
    pass


class EmployeePositionSchema(EmployeePositionBase):
    """员工职位响应模型，用于API返回"""
    id: int = Field(..., description="关联ID")
    start_date: Optional[date] = Field(None, description="入职时间")

    class Config:
        from_attributes = True