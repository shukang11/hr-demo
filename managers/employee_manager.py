from typing import Optional, List
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from models.account import AccountInDB
from models.employee import EmployeeInDB
from models.position import PositionInDB
from models.department import DepartmentInDB


class EmployeeService:
    def __init__(self, current_user: AccountInDB, session: Session):
        self.current_user = current_user
        self.session = session

    def create_employee(
        self,
        account_id: int,
        position_id: int,
        department_id: int,
        hire_date: date,
        employee_number: str,
        status: str = "active",
        job_type: Optional[str] = None,
        salary: Optional[float] = None
    ) -> EmployeeInDB:
        """创建新雇员
        
        Args:
            account_id: 关联的账户ID
            position_id: 职位ID
            department_id: 部门ID
            hire_date: 入职日期
            employee_number: 员工编号
            status: 雇员状态
            job_type: 工作类型
            salary: 薪资
            
        Returns:
            EmployeeInDB: 新创建的雇员对象
        """
        employee = EmployeeInDB(
            account_id=account_id,
            position_id=position_id,
            department_id=department_id,
            hire_date=hire_date,
            employee_number=employee_number,
            status=status,
            job_type=job_type,
            salary=salary
        )
        self.session.add(employee)
        try:
            self.session.commit()
            self.session.refresh(employee)
            return employee
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Employee creation failed - possible duplicate employee number or invalid references")

    def get_employee(self, employee_id: int) -> Optional[EmployeeInDB]:
        """获取雇员详情
        
        Args:
            employee_id: 雇员ID
            
        Returns:
            Optional[EmployeeInDB]: 雇员对象或None
        """
        stmt = (
            select(EmployeeInDB)
            .options(
                joinedload(EmployeeInDB.account),
                joinedload(EmployeeInDB.position),
                joinedload(EmployeeInDB.department)
            )
            .where(EmployeeInDB.id == employee_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_employees(
        self,
        department_id: Optional[int] = None,
        position_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[EmployeeInDB]:
        """列出雇员
        
        Args:
            department_id: 部门ID过滤
            position_id: 职位ID过滤
            status: 状态过滤
            
        Returns:
            List[EmployeeInDB]: 雇员列表
        """
        stmt = select(EmployeeInDB)
        
        if department_id is not None:
            stmt = stmt.where(EmployeeInDB.department_id == department_id)
        if position_id is not None:
            stmt = stmt.where(EmployeeInDB.position_id == position_id)
        if status is not None:
            stmt = stmt.where(EmployeeInDB.status == status)
            
        stmt = stmt.order_by(EmployeeInDB.id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def update_employee(
        self,
        employee_id: int,
        position_id: Optional[int] = None,
        department_id: Optional[int] = None,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
        salary: Optional[float] = None
    ) -> Optional[EmployeeInDB]:
        """更新雇员信息
        
        Args:
            employee_id: 雇员ID
            position_id: 新职位ID
            department_id: 新部门ID
            status: 新状态
            job_type: 新工作类型
            salary: 新薪资
            
        Returns:
            Optional[EmployeeInDB]: 更新后的雇员对象或None
        """
        employee = self.get_employee(employee_id)
        if not employee:
            return None

        if position_id is not None:
            employee.position_id = position_id
        if department_id is not None:
            employee.department_id = department_id
        if status is not None:
            employee.status = status
        if job_type is not None:
            employee.job_type = job_type
        if salary is not None:
            employee.salary = salary

        try:
            self.session.commit()
            self.session.refresh(employee)
            return employee
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Employee update failed - invalid position or department")

    def terminate_employee(
        self,
        employee_id: int,
        termination_date: date,
        termination_reason: str
    ) -> Optional[EmployeeInDB]:
        """终止雇员
        
        Args:
            employee_id: 雇员ID
            termination_date: 离职日期
            termination_reason: 离职原因
            
        Returns:
            Optional[EmployeeInDB]: 更新后的雇员对象或None
        """
        employee = self.get_employee(employee_id)
        if not employee:
            return None

        employee.status = "terminated"
        employee.termination_date = termination_date
        employee.termination_reason = termination_reason

        try:
            self.session.commit()
            self.session.refresh(employee)
            return employee
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Employee termination failed") 