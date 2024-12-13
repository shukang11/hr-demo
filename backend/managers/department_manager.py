from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from models.account import AccountInDB
from models.department import DepartmentInDB
from models.company import CompanyInDB


class DepartmentService:
    def __init__(self, current_user: AccountInDB, session: Session):
        self.current_user = current_user
        self.session = session

    def create_department(
        self, 
        name: str, 
        company_id: int, 
        parent_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> DepartmentInDB:
        """创建新部门
        
        Args:
            name: 部门名称
            company_id: 所属公司ID
            parent_id: 父部门ID
            description: 部门描述
            
        Returns:
            DepartmentInDB: 新创建的部门对象
        """
        department = DepartmentInDB(
            name=name,
            company_id=company_id,
            parent_id=parent_id,
            description=description
        )
        self.session.add(department)
        try:
            self.session.commit()
            self.session.refresh(department)
            return department
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Department creation failed - possible duplicate name or invalid parent/company")

    def get_department(self, department_id: int) -> Optional[DepartmentInDB]:
        """获取部门详情
        
        Args:
            department_id: 部门ID
            
        Returns:
            Optional[DepartmentInDB]: 部门对象或None
        """
        stmt = (
            select(DepartmentInDB)
            .options(joinedload(DepartmentInDB.company))
            .where(DepartmentInDB.id == department_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_departments(self, company_id: int) -> List[DepartmentInDB]:
        """列出公司的所有部门
        
        Args:
            company_id: 公司ID
            
        Returns:
            List[DepartmentInDB]: 部门列表
        """
        stmt = (
            select(DepartmentInDB)
            .where(DepartmentInDB.company_id == company_id)
            .order_by(DepartmentInDB.id)
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def update_department(
        self,
        department_id: int,
        name: Optional[str] = None,
        parent_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Optional[DepartmentInDB]:
        """更新部门信息
        
        Args:
            department_id: 部门ID
            name: 新部门名称
            parent_id: 新父部门ID
            description: 新部门描述
            
        Returns:
            Optional[DepartmentInDB]: 更新后的部门对象或None
        """
        department = self.get_department(department_id)
        if not department:
            return None

        if name is not None:
            department.name = name
        if parent_id is not None:
            department.parent_id = parent_id
        if description is not None:
            department.description = description

        try:
            self.session.commit()
            self.session.refresh(department)
            return department
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Department update failed - possible duplicate name or invalid parent")

    def delete_department(self, department_id: int) -> bool:
        """删除部门
        
        Args:
            department_id: 部门ID
            
        Returns:
            bool: 是否删除成功
        """
        department = self.get_department(department_id)
        if not department:
            return False

        try:
            self.session.delete(department)
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Cannot delete department with existing employees or sub-departments") 