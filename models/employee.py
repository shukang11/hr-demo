from typing import TYPE_CHECKING, Optional
from datetime import date
from sqlalchemy.orm import Mapped
from extensions.ext_database import db
from .base import BaseModel
from .schema import JsonSchemaInDB

if TYPE_CHECKING:
    from .department import DepartmentInDB
    from .position import EmployeePositionInDB

class EmployeeInDB(BaseModel):
    """Employee information database model
    Stores detailed employee information and their relationships with company, department, and position

    Attributes:
        name (str): Employee name, required
        email (str): Email address
        phone (str): Contact phone number
        birthdate (date): Date of birth
        address (str): Residential address
        hire_date (date): Employment date
        termination_date (date): Termination date
        gender (str): Gender, must be 'Male', 'Female' or 'Unknown'
        extra_value (JSON): Additional JSON format data
        extra_schema_id (int): Associated JSON Schema ID
        extra_schema (JsonSchemaInDB): Associated JSON Schema object
        positions (list): List of positions held by the employee
        led_departments (list): List of departments led by the employee
    """
    __tablename__ = 'employee'

    name: Mapped[str] = db.Column(db.String(255), nullable=False)
    email: Mapped[Optional[str]] = db.Column(db.String(255))
    phone: Mapped[Optional[str]] = db.Column(db.String(20))
    birthdate: Mapped[Optional[date]] = db.Column(db.Date)
    address: Mapped[Optional[str]] = db.Column(db.String(255))
    hire_date: Mapped[Optional[date]] = db.Column(db.Date)
    termination_date: Mapped[Optional[date]] = db.Column(db.Date)
    gender: Mapped[str] = db.Column(db.String, nullable=False)
    extra_value: Mapped[Optional[dict]] = db.Column(db.JSON)
    extra_schema_id: Mapped[Optional[int]] = db.Column(db.Integer, db.ForeignKey('json_schemas.id'))

    # Relationships
    extra_schema: Mapped['JsonSchemaInDB'] = db.relationship('JsonSchemaInDB', foreign_keys=[extra_schema_id])
    positions: Mapped[list['EmployeePositionInDB']] = db.relationship('EmployeePositionInDB', back_populates='employee')
    led_departments: Mapped[list['DepartmentInDB']] = db.relationship('DepartmentInDB', back_populates='leader')