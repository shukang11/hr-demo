from typing import List, Optional
from datetime import datetime
from pydantic import Field, field_validator
from core.database import CompanyStatus, ContractType
from core.utils.schema_extention import PagePayload, SchemaBaseModel


# MARK: - Schema
class CompanySchema(SchemaBaseModel):
    """
    公司的模型。

    属性:
    - id (int): 公司的ID。
    - name (str): 公司名称。
    - description (str): 公司描述。
    - admin_id (int): 最高管理员的ID。
    - status (CompanyStatus): 公司的状态。
    """

    id: int
    name: str
    description: str
    admin_id: int
    status: CompanyStatus


class CompanyEmployeeSchema(SchemaBaseModel):
    account_id: int
    company_id: int


# MARK: - 操作模型
class InsertCompanyPayload(SchemaBaseModel):
    """
    创建公司的模型。

    属性:
    - name (str): 公司名称，长度在2到64之间。
    - description (Optional[str]): 公司描述，可选，长度在2到255之间。
    - admin_id (int): 最高管理员的ID。
    """

    id: Optional[int] = Field(None, description="公司的ID")
    name: Optional[str] = Field(None, min_length=2, max_length=64)
    description: Optional[str] = Field(None, min_length=2, max_length=255)
    status: Optional[CompanyStatus] = Field(None, description="公司的状态")
    admin_id: int = Field(..., description="最高管理员的ID")


class InsertDepartmentPayload(SchemaBaseModel):
    id: Optional[int] = Field(None, description="部门的ID")
    name: str = Field(..., min_length=2, max_length=64)
    parent_id: Optional[int] = Field(None, description="父部门的ID")
    company_id: int = Field(..., description="公司的ID")
    leader_id: Optional[int] = Field(None, description="部门领导的ID")


class InsertCompanyJobPayload(SchemaBaseModel):
    id: Optional[int] = Field(None, description="职位的ID")
    company_id: int = Field(..., description="公司的ID")
    job_name: str = Field(..., min_length=2, max_length=64)
    description: Optional[str] = Field(None, min_length=2, max_length=255)


# 面试员工，添加面试记录
class InterviewEmployeePayload(SchemaBaseModel):
    id: Optional[int] = Field(None, description="面试记录的ID")
    account_id: int = Field(..., description="员工的ID")
    company_id: int = Field(..., description="公司的ID")
    job_id: int = Field(..., description="职位的ID")
    interview_at: datetime = Field(..., description="面试时间")
    is_pass: Optional[bool] = Field(None, description="是否通过面试")
    remark: Optional[str] = Field(None, description="备注")

    @field_validator("interview_at")
    def parse_timestamp(cls, value) -> datetime:
        # 将 13 位数字转换为 datetime 对象
        return cls.convert_int_2_datetime(value)


# 招聘员工
class RecruitEmployeePayload(SchemaBaseModel):
    account_id: int = Field(..., description="员工的ID")
    company_id: int = Field(..., description="公司的ID")
    job_id: int = Field(..., description="职位的ID")
    deparentment_id: Optional[int] = Field(None, description="部门的ID")
    contract_type: ContractType = Field(..., description="合约类型")

    has_real_contract: Optional[bool] = Field(None, description="是否有真实合同")
    contract_start_at: Optional[datetime] = Field(None, description="合约开始时间")
    contract_end_at: Optional[datetime] = Field(None, description="合约结束时间")
    remark: Optional[str] = Field(None, description="备注")

    @field_validator("contract_end_at", "contract_start_at")
    def parse_timestamp(cls, value) -> datetime:
        # 将 13 位数字转换为 datetime 对象
        return cls.convert_int_2_datetime(value)


# MARK: - 查询模型


class QueryEmployeePayload(SchemaBaseModel):
    company_id: Optional[int] = Field(None, description="公司的ID")
    job_id: Optional[int] = Field(None, description="职位的ID")
    department_id: Optional[int] = Field(None, description="部门的ID")

    contract_type: Optional[List[ContractType]] = Field(None, description="合约类型")

    contract_start_at: Optional[datetime] = Field(None, description="合约开始时间")
    contract_end_at: Optional[datetime] = Field(None, description="合约结束时间")
    page: PagePayload = Field(PagePayload(), description="分页参数")

    @field_validator("contract_end_at", "contract_start_at")
    def parse_timestamp(cls, value) -> datetime:
        # 将 13 位数字转换为 datetime 对象
        return cls.convert_int_2_datetime(value)
