from enum import StrEnum
from typing import TYPE_CHECKING, Optional
from extensions.ext_database import db
from .base import BaseModel
from sqlalchemy.orm import Mapped
if TYPE_CHECKING:
    from .schema import JsonSchemaInDB
    from .department import DepartmentInDB
    from .position import PositionInDB
    from .account import AccountInDB
    


class CompanyInDB(BaseModel):
    """Company information database model
    Stores basic company information and its relationships with other entities

    Attributes:
        name (str): Company name, required
        extra_value (JSON): Additional JSON format data
        extra_schema_id (int): Associated JSON Schema ID
        extra_schema (JsonSchemaInDB): Associated JSON Schema object
        departments (list): List of company departments
        positions (list): List of company positions
        description (str): Company description
    """
    __tablename__ = 'company'

    name: Mapped[str] = db.Column(db.String(255), nullable=False)
    description: Mapped[Optional[str]] = db.Column(db.String)
    extra_value: Mapped[Optional[dict]] = db.Column(db.JSON)
    extra_schema_id: Mapped[Optional[int]] = db.Column(db.Integer, db.ForeignKey('json_schemas.id'))

    # Relationships
    extra_schema: Mapped['JsonSchemaInDB'] = db.relationship('JsonSchemaInDB', foreign_keys=[extra_schema_id])
    departments: Mapped[list['DepartmentInDB']] = db.relationship('DepartmentInDB', back_populates='company')
    positions: Mapped[list['PositionInDB']] = db.relationship('PositionInDB', back_populates='company')

class AccountCompanyRole(StrEnum):
    """账户-公司关联角色"""
    OWNER = 'owner'
    ADMIN = 'admin'
    USER = 'user'

class AccountCompanyInDB(BaseModel):
    """账户-公司关联数据库模型
    存储账户与公司的多对多关系，定义账户在每个公司中的角色

    Attributes:
        account_id (int): 账户ID，不可为空
        company_id (int): 公司ID，不可为空
        role (str): 用户角色，必须为 'owner'、'admin' 或 'user'
        account (AccountInDB): 关联的账户对象
        company (CompanyInDB): 关联的公司对象
    """
    __tablename__ = 'account_company'

    account_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    company_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    role: Mapped[AccountCompanyRole] = db.Column(db.String(32), nullable=False)

    # Relationships
    account: Mapped['AccountInDB'] = db.relationship('AccountInDB', back_populates='companies')
    company: Mapped['CompanyInDB'] = db.relationship('CompanyInDB')

    __table_args__ = (
        db.UniqueConstraint('account_id', 'company_id', name='uix_account_company'),
    ) 