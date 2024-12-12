from typing import TYPE_CHECKING, Optional
from extensions.ext_database import db
from .base import BaseModel
from sqlalchemy.orm import Mapped
if TYPE_CHECKING:
    from .company import CompanyInDB
    from .employee import EmployeeInDB
    from .department import DepartmentInDB
    from .employee import EmployeePositionInDB

class PositionInDB(BaseModel):
    """Position information database model
    Stores position information and its relationship with company

    Attributes:
        name (str): Position name, required
        company_id (int): Company ID, required
        remark (str): Remarks
        company (CompanyInDB): Associated company object
        employee_positions (list): List of employee-position associations for this position
    """
    __tablename__ = 'position'

    name: Mapped[str] = db.Column(db.String(64), nullable=False)
    company_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    remark: Mapped[Optional[str]] = db.Column(db.String(255))

    # Relationships
    company: Mapped['CompanyInDB'] = db.relationship('CompanyInDB', back_populates='positions')
    employee_positions: Mapped[list['EmployeePositionInDB']] = db.relationship('EmployeePositionInDB', back_populates='position')


class EmployeePositionInDB(BaseModel):
    """Employee-Position association database model
    Stores many-to-many relationships between employees and positions with additional information

    Attributes:
        employee_id (int): Employee ID, required
        company_id (int): Company ID, required
        department_id (int): Department ID, required
        position_id (int): Position ID, required
        remark (str): Remarks
        employee (EmployeeInDB): Associated employee object
        company (CompanyInDB): Associated company object
        department (DepartmentInDB): Associated department object
        position (PositionInDB): Associated position object
    """
    __tablename__ = 'employee_position'

    employee_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    company_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    department_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    position_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    remark: Mapped[Optional[str]] = db.Column(db.String(255))

    # Relationships
    employee: Mapped['EmployeeInDB'] = db.relationship('EmployeeInDB', back_populates='positions')
    company: Mapped['CompanyInDB'] = db.relationship('CompanyInDB')
    department: Mapped['DepartmentInDB'] = db.relationship('DepartmentInDB', back_populates='employee_positions')
    position: Mapped['PositionInDB'] = db.relationship('PositionInDB', back_populates='employee_positions') 