from typing import TYPE_CHECKING, Optional
from extensions.ext_database import db
from .base import BaseModel
from sqlalchemy.orm import Mapped
if TYPE_CHECKING:
    from .schema import JsonSchemaInDB
    from .department import DepartmentInDB
    from .position import PositionInDB
    from .employee import EmployeeInDB


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

