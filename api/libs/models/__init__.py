"""数据库模型模块
本模块包含所有与数据库相关的 SQLAlchemy 模型类

包含以下模型：
    - JsonSchemaInDB: JSON Schema 存储
    - CompanyInDB: 公司信息
    - EmployeeInDB: 员工信息
    - DepartmentInDB: 部门信息
    - PositionInDB: 职位信息
    - EmployeePositionInDB: 员工-职位关联
    - AccountInDB: 账户信息
    - AccountTokenInDB: 账户令牌
    - AccountCompanyInDB: 账户-公司关联
"""

from .base import BaseModel
from .json_schema import JsonSchemaInDB
from .company import CompanyInDB
from .employee import EmployeeInDB
from .department import DepartmentInDB
from .employee_position import EmployeePositionInDB
from .position import PositionInDB
from .json_value import JsonValueInDB
from .account import AccountInDB, AccountTokenInDB
from .account_company import AccountCompanyInDB, AccountCompanyRole
from .candidate import CandidateInDB, CandidateStatus
__all__ = [
    "BaseModel",
    "JsonSchemaInDB",
    "JsonValueInDB",
    # 公司相关模型
    "CompanyInDB",
    "EmployeeInDB",
    "DepartmentInDB",
    "PositionInDB",
    "EmployeePositionInDB",
    # 真实账户
    "AccountInDB",
    "AccountTokenInDB",
    # 公司与真实账户关联
    "AccountCompanyInDB",
    "AccountCompanyRole",
    # 候选人相关模型
    "CandidateInDB",
    "CandidateStatus",
]
