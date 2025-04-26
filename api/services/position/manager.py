from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from api.libs.models import PositionInDB, DepartmentInDB  # Adjusted import path
from ._schema import (
    PositionCreate,
    PositionUpdate,
    PositionSchema,
)  # Import new schemas


class PositionService:
    session: Session

    def __init__(self, session: Session):  # Removed current_user
        self.session = session

    def create_position(
        self,
        position_data: PositionCreate,  # Use PositionCreate schema
    ) -> Optional[PositionSchema]:  # Return PositionSchema
        """创建新职位

        Args:
            position_data: 职位创建数据

        Returns:
            Optional[PositionSchema]: 新创建的职位对象或None
        """
        # Validate department exists (optional, depending on requirements)
        # stmt_dep = select(DepartmentInDB).where(DepartmentInDB.id == position_data.department_id)
        # department = self.session.execute(stmt_dep).scalar_one_or_none()
        # if not department:
        #     # Or raise a specific exception
        #     return None

        position = PositionInDB(
            name=position_data.name,  # Use name instead of title
            company_id=position_data.company_id,  # Add company_id
            remark=position_data.remark,  # Use remark
            # Assuming created_at/updated_at are handled by BaseModel or DB defaults
        )
        self.session.add(position)
        try:
            self.session.commit()
            self.session.refresh(position)
            return PositionSchema.model_validate(position)
        except IntegrityError:
            self.session.rollback()
            # Consider logging the error
            # raise ValueError("Position creation failed - possible duplicate name or invalid company")
            return None  # Or raise specific exception

    def query_position_by_id(
        self, position_id: int
    ) -> Optional[PositionInDB]:  # Renamed for consistency
        """获取职位详情

        Args:
            position_id: 职位ID

        Returns:
            Optional[PositionInDB]: 职位对象或None
        """
        stmt = (
            select(PositionInDB)
            # .options(joinedload(PositionInDB.department)) # Adjust join if needed based on new model
            .options(joinedload(PositionInDB.company))  # Join with company
            .where(PositionInDB.id == position_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_positions(
        self, company_id: Optional[int] = None
    ) -> List[PositionSchema]:  # Filter by company_id, return list of schemas
        """列出公司的所有职位

        Args:
            company_id: 公司ID，如果为None则列出所有职位

        Returns:
            List[PositionSchema]: 职位列表
        """
        stmt = select(PositionInDB)
        if company_id is not None:
            stmt = stmt.where(PositionInDB.company_id == company_id)
        stmt = stmt.order_by(PositionInDB.id)
        result = self.session.execute(stmt)
        positions = result.scalars().all()
        return [PositionSchema.model_validate(p) for p in positions]

    def update_position(
        self,
        position_id: int,
        position_data: PositionUpdate,  # Use PositionUpdate schema
    ) -> Optional[PositionSchema]:  # Return PositionSchema
        """更新职位信息

        Args:
            position_id: 职位ID
            position_data: 更新数据

        Returns:
            Optional[PositionSchema]: 更新后的职位对象或None
        """
        position = self.query_position_by_id(position_id)
        if not position:
            return None

        update_data = position_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(position, key, value)

        # Add updated_at logic if needed
        # position.updated_at = datetime.now(datetime.timezone.utc)

        try:
            self.session.commit()
            self.session.refresh(position)
            return PositionSchema.model_validate(position)
        except IntegrityError:
            self.session.rollback()
            # Consider logging the error
            # raise ValueError("Position update failed - possible duplicate name or invalid company")
            return None  # Or raise specific exception

    def delete_position(self, position_id: int) -> bool:
        """删除职位

        Args:
            position_id: 职位ID

        Returns:
            bool: 是否删除成功
        """
        position = self.query_position_by_id(position_id)
        if not position:
            return False

        try:
            # Check for dependencies (e.g., employees in this position) before deleting
            # if position.employee_positions: # Assuming relation exists
            #    raise ValueError("Cannot delete position with existing employees")

            self.session.delete(position)
            self.session.commit()
            return True
        except IntegrityError as e:  # Catch specific errors if needed
            self.session.rollback()
            # Consider logging the error
            # raise ValueError(f"Cannot delete position: {e}")
            return False
        except (
            Exception
        ) as e:  # Catch potential custom exceptions like ValueError above
            self.session.rollback()
            # Consider logging the error
            # print(f"Error deleting position: {e}") # Or log properly
            return False
