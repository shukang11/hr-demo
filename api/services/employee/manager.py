from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime

# 导入数据库模型
from libs.models import EmployeeInDB, AccountInDB, EmployeePositionInDB
from services.permission import PermissionService, PermissionError

# 导入员工相关的 Pydantic 模型
from ._schema import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeSchema,
    EmployeePositionCreate,
    EmployeePositionSchema,
    Gender,
)


# 定义员工服务类
class EmployeeService:
    session: Session  # 数据库会话对象
    account: AccountInDB  # 当前登录的用户对象
    _permission: PermissionService  # 权限服务对象

    def __init__(self, session: Session, account: AccountInDB):
        self.session = session
        self.account = account
        self._permission = PermissionService(session, account)

    def create_employee(
        self,
        employee_data: EmployeeCreate,
    ) -> Optional[EmployeeSchema]:
        """创建新员工

        Args:
            employee_data: 包含员工信息的 Pydantic 模型

        Returns:
            成功创建则返回员工信息模型，失败则返回 None

        Raises:
            PermissionError: 如果用户没有在指定公司创建员工的权限
        """
        # 检查权限
        if not self._permission.can_manage_company(employee_data.company_id):
            raise PermissionError("您没有在该公司创建员工的权限")

        # 将字符串枚举性别转换为整数
        gender_int = employee_data.gender.to_int() if employee_data.gender else 0

        # 创建 EmployeeInDB 数据库模型实例
        employee = EmployeeInDB(
            company_id=employee_data.company_id,
            name=employee_data.name,
            email=employee_data.email,
            phone=employee_data.phone,
            birthdate=employee_data.birthdate,
            address=employee_data.address,
            gender=gender_int,  # 使用整数值
            extra_value=employee_data.extra_value,
            extra_schema_id=employee_data.extra_schema_id,
        )

        # 添加到会话
        self.session.add(employee)

        try:
            # 提交事务，保存到数据库
            self.session.commit()
            # 刷新对象，获取生成的ID等
            self.session.refresh(employee)

            # 如果提供了部门和职位信息，创建员工职位关联
            if employee_data.department_id and employee_data.position_id:
                position = EmployeePositionInDB(
                    employee_id=employee.id,
                    company_id=employee_data.company_id,
                    department_id=employee_data.department_id,
                    position_id=employee_data.position_id,
                    start_date=employee_data.entry_date or datetime.now().date(),
                )
                self.session.add(position)
                self.session.commit()

            # 将数据库模型转换为API响应模型
            return EmployeeSchema.model_validate(employee)
        except IntegrityError:
            # 处理数据库完整性错误
            self.session.rollback()
            return None

    def update_employee(
        self,
        employee_id: int,
        employee_data: EmployeeUpdate,
    ) -> Optional[EmployeeSchema]:
        """更新员工信息

        Args:
            employee_id: 员工ID
            employee_data: 包含要更新的字段的Pydantic模型

        Returns:
            成功更新则返回更新后的员工信息模型，失败或未找到则返回None

        Raises:
            PermissionError: 当用户没有权限更新指定员工时
        """
        # 获取员工信息
        employee = self.query_employee_by_id(employee_id)
        if not employee:
            return None

        # 检查权限
        if not self._permission.can_manage_company(employee.company_id):
            raise PermissionError("您没有更新该员工的权限")

        # 将Pydantic模型转换为字典，排除未设置的字段
        update_data = employee_data.model_dump(exclude_unset=True)

        # 更新每个字段
        for key, value in update_data.items():
            # 排除department_id和position_id，这两个字段需要通过职位关联管理
            if key == "gender" and value is not None:
                # 将字符串枚举性别转换为整数
                setattr(employee, key, value.to_int())
            elif key not in ["department_id", "position_id"]:
                setattr(employee, key, value)

        try:
            # 提交事务，保存更改
            self.session.commit()
            # 刷新对象，获取最新状态
            self.session.refresh(employee)

            # 如果提供了部门和职位信息，更新或创建员工职位关联
            if employee_data.department_id is not None and employee_data.position_id is not None:
                # 获取当前职位关联
                current_position = self.get_employee_current_position(employee_id)
                
                if current_position:
                    # 如果部门或职位发生变化，创建新的职位关联
                    if (current_position.department_id != employee_data.department_id or
                        current_position.position_id != employee_data.position_id):
                        position = EmployeePositionInDB(
                            employee_id=employee.id,
                            company_id=employee.company_id,
                            department_id=employee_data.department_id,
                            position_id=employee_data.position_id,
                            start_date=datetime.now().date(),
                        )
                        self.session.add(position)
                        self.session.commit()
                else:
                    # 如果没有当前职位关联，创建新的
                    position = EmployeePositionInDB(
                        employee_id=employee.id,
                        company_id=employee.company_id,
                        department_id=employee_data.department_id,
                        position_id=employee_data.position_id,
                        start_date=datetime.now().date(),
                    )
                    self.session.add(position)
                    self.session.commit()

            # 转换为API响应模型
            return EmployeeSchema.model_validate(employee)
        except IntegrityError:
            # 处理数据库完整性错误
            self.session.rollback()
            return None

    def query_employee_by_id(
        self,
        employee_id: int
    ) -> Optional[EmployeeInDB]:
        """根据ID查询员工信息

        Args:
            employee_id: 员工ID

        Returns:
            找到则返回员工数据库模型对象，否则返回None

        Raises:
            PermissionError: 当用户没有权限查看指定员工时
        """
        # 构建查询语句
        stmt = (
            select(EmployeeInDB)
            .options(
                joinedload(EmployeeInDB.positions),
                joinedload(EmployeeInDB.extra_schema)
            )
            .where(EmployeeInDB.id == employee_id)
        )

        # 执行查询
        employee = self.session.execute(stmt).scalar_one_or_none()

        # 检查权限
        if employee and not self._permission.can_view_company(employee.company_id):
            raise PermissionError("您没有查看该员工的权限")

        return employee

    def get_employee_list(
        self,
        company_id: int,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[EmployeeSchema], int]:
        """获取指定公司的员工列表，支持分页

        Args:
            company_id: 公司ID
            page: 页码，从1开始
            limit: 每页显示数量

        Returns:
            包含员工列表和总数的元组

        Raises:
            PermissionError: 当用户没有权限查看指定公司的员工时
        """
        # 检查权限
        if not self._permission.can_view_company(company_id):
            raise PermissionError("您没有查看该公司员工的权限")

        # 构建基础查询
        stmt = (
            select(EmployeeInDB)
            .where(EmployeeInDB.company_id == company_id)
        )

        # 计数查询
        count_stmt = (
            select(func.count())
            .select_from(EmployeeInDB)
            .where(EmployeeInDB.company_id == company_id)
        )

        # 获取总数
        total = self.session.execute(count_stmt).scalar() or 0

        # 添加分页
        stmt = (
            stmt
            .order_by(EmployeeInDB.id)
            .offset((page - 1) * limit)
            .limit(limit)
        )

        # 执行查询
        employees = self.session.execute(stmt).scalars().all()

        # 转换为API响应模型列表
        result = [EmployeeSchema.model_validate(e) for e in employees]

        return result, total

    def get_employees_by_department(
        self,
        department_id: int,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[EmployeeSchema], int]:
        """获取指定部门的员工列表，支持分页

        Args:
            department_id: 部门ID
            page: 页码，从1开始
            limit: 每页显示数量

        Returns:
            包含员工列表和总数的元组

        Raises:
            PermissionError: 当用户没有权限查看指定部门的员工时
        """
        # 使用部门ID查询员工
        stmt = (
            select(EmployeeInDB)
            .join(EmployeePositionInDB, EmployeeInDB.id == EmployeePositionInDB.employee_id)
            .where(EmployeePositionInDB.department_id == department_id)
            .group_by(EmployeeInDB.id)  # 对员工ID分组，避免重复
        )

        # 获取第一个员工来检查权限
        check_stmt = (
            select(EmployeePositionInDB.company_id)
            .where(EmployeePositionInDB.department_id == department_id)
            .limit(1)
        )
        company_id_result = self.session.execute(check_stmt).first()
        
        if company_id_result:
            company_id = company_id_result[0]
            # 检查权限
            if not self._permission.can_view_company(company_id):
                raise PermissionError("您没有查看该部门员工的权限")
        else:
            # 如果部门不存在或没有员工，返回空列表
            return [], 0

        # 计数查询
        count_stmt = (
            select(func.count(func.distinct(EmployeeInDB.id)))
            .select_from(EmployeeInDB)
            .join(EmployeePositionInDB, EmployeeInDB.id == EmployeePositionInDB.employee_id)
            .where(EmployeePositionInDB.department_id == department_id)
        )

        # 获取总数
        total = self.session.execute(count_stmt).scalar() or 0

        # 添加分页
        stmt = (
            stmt
            .order_by(EmployeeInDB.id)
            .offset((page - 1) * limit)
            .limit(limit)
        )

        # 执行查询
        employees = self.session.execute(stmt).scalars().all()

        # 转换为API响应模型列表
        result = [EmployeeSchema.model_validate(e) for e in employees]

        return result, total

    def search_employees(
        self,
        company_id: int,
        name: str,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[EmployeeSchema], int]:
        """搜索员工

        Args:
            company_id: 公司ID
            name: 搜索关键词
            page: 页码，从1开始
            limit: 每页显示数量

        Returns:
            包含员工列表和总数的元组

        Raises:
            PermissionError: 当用户没有权限查看指定公司的员工时
        """
        # 检查权限
        if not self._permission.can_view_company(company_id):
            raise PermissionError("您没有查看该公司员工的权限")

        # 构建模糊搜索条件
        search_pattern = f"%{name}%"
        stmt = (
            select(EmployeeInDB)
            .where(
                EmployeeInDB.company_id == company_id,
                EmployeeInDB.name.like(search_pattern)
            )
        )

        # 计数查询
        count_stmt = (
            select(func.count())
            .select_from(EmployeeInDB)
            .where(
                EmployeeInDB.company_id == company_id,
                EmployeeInDB.name.like(search_pattern)
            )
        )

        # 获取总数
        total = self.session.execute(count_stmt).scalar() or 0

        # 添加分页
        stmt = (
            stmt
            .order_by(EmployeeInDB.id)
            .offset((page - 1) * limit)
            .limit(limit)
        )

        # 执行查询
        employees = self.session.execute(stmt).scalars().all()

        # 转换为API响应模型列表
        result = [EmployeeSchema.model_validate(e) for e in employees]

        return result, total

    def delete_employee(
        self,
        employee_id: int
    ) -> bool:
        """删除员工

        Args:
            employee_id: 员工ID

        Returns:
            删除成功返回True，失败或未找到返回False

        Raises:
            PermissionError: 当用户没有权限删除指定员工时
        """
        # 获取员工信息
        employee = self.query_employee_by_id(employee_id)
        if not employee:
            return False

        # 检查权限
        if not self._permission.can_manage_company(employee.company_id):
            raise PermissionError("您没有删除该员工的权限")

        try:
            # 删除相关职位关联
            position_stmt = (
                select(EmployeePositionInDB)
                .where(EmployeePositionInDB.employee_id == employee_id)
            )
            positions = self.session.execute(position_stmt).scalars().all()
            for position in positions:
                self.session.delete(position)

            # 删除员工
            self.session.delete(employee)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    # 员工职位关联相关方法

    def add_employee_position(
        self,
        position_data: EmployeePositionCreate
    ) -> Optional[EmployeePositionSchema]:
        """为员工添加职位

        Args:
            position_data: 职位关联数据

        Returns:
            成功则返回职位关联信息，失败则返回None

        Raises:
            PermissionError: 当用户没有权限管理指定员工的职位时
        """
        # 检查权限
        if not self._permission.can_manage_company(position_data.company_id):
            raise PermissionError("您没有管理该公司员工职位的权限")

        # 验证员工是否属于该公司
        emp_stmt = (
            select(EmployeeInDB)
            .where(
                EmployeeInDB.id == position_data.employee_id,
                EmployeeInDB.company_id == position_data.company_id
            )
        )
        employee = self.session.execute(emp_stmt).scalar_one_or_none()
        if not employee:
            raise PermissionError("员工不存在或不属于该公司")

        # 创建职位关联
        position = EmployeePositionInDB(
            employee_id=position_data.employee_id,
            company_id=position_data.company_id,
            department_id=position_data.department_id,
            position_id=position_data.position_id,
            remark=position_data.remark,
            start_date=datetime.now().date(),
        )

        self.session.add(position)
        try:
            self.session.commit()
            self.session.refresh(position)
            return EmployeePositionSchema.model_validate(position)
        except IntegrityError:
            self.session.rollback()
            return None

    def remove_employee_position(
        self,
        position_id: int
    ) -> bool:
        """移除员工职位关联

        Args:
            position_id: 职位关联ID

        Returns:
            成功返回True，失败或未找到返回False

        Raises:
            PermissionError: 当用户没有权限管理指定员工的职位时
        """
        # 查询职位关联
        stmt = (
            select(EmployeePositionInDB)
            .where(EmployeePositionInDB.id == position_id)
        )
        position = self.session.execute(stmt).scalar_one_or_none()

        if not position:
            return False

        # 检查权限
        if not self._permission.can_manage_company(position.company_id):
            raise PermissionError("您没有管理该公司员工职位的权限")

        try:
            self.session.delete(position)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def get_employee_positions(
        self,
        employee_id: int
    ) -> List[EmployeePositionSchema]:
        """获取员工的职位列表

        Args:
            employee_id: 员工ID

        Returns:
            职位关联列表

        Raises:
            PermissionError: 当用户没有权限查看指定员工的职位时
        """
        # 查询员工所属公司
        emp_stmt = select(EmployeeInDB.company_id).where(EmployeeInDB.id == employee_id)
        company_id_result = self.session.execute(emp_stmt).first()

        if not company_id_result:
            # 员工不存在
            return []

        company_id = company_id_result[0]

        # 检查权限
        if not self._permission.can_view_company(company_id):
            raise PermissionError("您没有查看该员工职位的权限")

        # 查询职位关联
        stmt = (
            select(EmployeePositionInDB)
            .where(EmployeePositionInDB.employee_id == employee_id)
            .order_by(EmployeePositionInDB.start_date.desc())
        )
        positions = self.session.execute(stmt).scalars().all()

        # 转换为API响应模型列表
        return [EmployeePositionSchema.model_validate(p) for p in positions]

    def get_employee_current_position(
        self,
        employee_id: int
    ) -> Optional[EmployeePositionInDB]:
        """获取员工当前职位

        Args:
            employee_id: 员工ID

        Returns:
            当前职位关联，如果没有则返回None

        Raises:
            PermissionError: 当用户没有权限查看指定员工的职位时
        """
        # 查询员工所属公司
        emp_stmt = select(EmployeeInDB.company_id).where(EmployeeInDB.id == employee_id)
        company_id_result = self.session.execute(emp_stmt).first()

        if not company_id_result:
            # 员工不存在
            return None

        company_id = company_id_result[0]

        # 检查权限
        if not self._permission.can_view_company(company_id):
            raise PermissionError("您没有查看该员工职位的权限")

        # 查询最新的职位关联（按入职时间倒序）
        stmt = (
            select(EmployeePositionInDB)
            .where(EmployeePositionInDB.employee_id == employee_id)
            .order_by(EmployeePositionInDB.start_date.desc())
            .limit(1)
        )
        position = self.session.execute(stmt).scalar_one_or_none()

        return position

    def get_employee_position_history(
        self,
        employee_id: int
    ) -> List[EmployeePositionSchema]:
        """获取员工职位历史

        Args:
            employee_id: 员工ID

        Returns:
            职位关联历史列表

        Raises:
            PermissionError: 当用户没有权限查看指定员工的职位时
        """
        # 与get_employee_positions相同，但为了API一致性保留此方法
        return self.get_employee_positions(employee_id)