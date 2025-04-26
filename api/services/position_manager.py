from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from models.account import AccountInDB
from models.position import PositionInDB
from models.department import DepartmentInDB


class PositionService:
    def __init__(self, current_user: AccountInDB, session: Session):
        self.current_user = current_user
        self.session = session

    def create_position(
        self,
        title: str,
        department_id: int,
        description: Optional[str] = None,
        requirements: Optional[str] = None,
        salary_range: Optional[str] = None,
    ) -> PositionInDB:
        """创建新职位

        Args:
            title: 职位名称
            department_id: 所属部门ID
            description: 职位描述
            requirements: 职位要求
            salary_range: 薪资范围

        Returns:
            PositionInDB: 新创建的职位对象
        """
        position = PositionInDB(
            title=title,
            department_id=department_id,
            description=description,
            requirements=requirements,
            salary_range=salary_range,
        )
        self.session.add(position)
        try:
            self.session.commit()
            self.session.refresh(position)
            return position
        except IntegrityError:
            self.session.rollback()
            raise ValueError(
                "Position creation failed - possible duplicate title or invalid department"
            )

    def get_position(self, position_id: int) -> Optional[PositionInDB]:
        """获取职位详情

        Args:
            position_id: 职位ID

        Returns:
            Optional[PositionInDB]: 职位对象或None
        """
        stmt = (
            select(PositionInDB)
            .options(joinedload(PositionInDB.department))
            .where(PositionInDB.id == position_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_positions(self, department_id: Optional[int] = None) -> List[PositionInDB]:
        """列出部门的所有职位

        Args:
            department_id: 部门ID，如果为None则列出所有职位

        Returns:
            List[PositionInDB]: 职位列表
        """
        stmt = select(PositionInDB)
        if department_id is not None:
            stmt = stmt.where(PositionInDB.department_id == department_id)
        stmt = stmt.order_by(PositionInDB.id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def update_position(
        self,
        position_id: int,
        title: Optional[str] = None,
        department_id: Optional[int] = None,
        description: Optional[str] = None,
        requirements: Optional[str] = None,
        salary_range: Optional[str] = None,
    ) -> Optional[PositionInDB]:
        """更新职位信息

        Args:
            position_id: 职位ID
            title: 新职位名称
            department_id: 新部门ID
            description: 新职位描述
            requirements: 新职位要求
            salary_range: 新薪资范围

        Returns:
            Optional[PositionInDB]: 更新后的职位对象或None
        """
        position = self.get_position(position_id)
        if not position:
            return None

        if title is not None:
            position.title = title
        if department_id is not None:
            position.department_id = department_id
        if description is not None:
            position.description = description
        if requirements is not None:
            position.requirements = requirements
        if salary_range is not None:
            position.salary_range = salary_range

        try:
            self.session.commit()
            self.session.refresh(position)
            return position
        except IntegrityError:
            self.session.rollback()
            raise ValueError(
                "Position update failed - possible duplicate title or invalid department"
            )

    def delete_position(self, position_id: int) -> bool:
        """删除职位

        Args:
            position_id: 职位ID

        Returns:
            bool: 是否删除成功
        """
        position = self.get_position(position_id)
        if not position:
            return False

        try:
            self.session.delete(position)
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Cannot delete position with existing employees")
