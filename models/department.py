from typing import TYPE_CHECKING, Optional
from extensions.ext_database import db
from .base import BaseModel
from sqlalchemy.orm import Mapped
if TYPE_CHECKING:
    from .company import CompanyInDB
    from .employee import EmployeeInDB
    from .position import EmployeePositionInDB

class DepartmentInDB(BaseModel):
    """Department information database model
    Stores department information and its relationships with company and employees, supports tree structure

    Attributes:
        parent_id (int): Parent department ID for tree structure
        company_id (int): Company ID, required
        name (str): Department name, required
        leader_id (int): Department leader ID
        remark (str): Remarks
        parent (DepartmentInDB): Parent department object
        children (list): List of child departments
        company (CompanyInDB): Associated company object
        leader (EmployeeInDB): Department leader object
        employee_positions (list): List of employee-position associations in the department
    """
    __tablename__ = 'department'
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = db.Column(db.Integer, db.ForeignKey('department.id'))
    company_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name: Mapped[str] = db.Column(db.String(64), nullable=False)
    leader_id: Mapped[Optional[int]] = db.Column(db.Integer, db.ForeignKey('employee.id'))
    remark: Mapped[Optional[str]] = db.Column(db.String(255))

    # Relationships
    parent: Mapped[Optional['DepartmentInDB']] = db.relationship('DepartmentInDB', remote_side=[id], backref='children')
    company: Mapped['CompanyInDB'] = db.relationship('CompanyInDB', back_populates='departments')
    leader: Mapped[Optional['EmployeeInDB']] = db.relationship('EmployeeInDB', back_populates='led_departments')
    employee_positions: Mapped[list['EmployeePositionInDB']] = db.relationship('EmployeePositionInDB', back_populates='department') 