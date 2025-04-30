from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

# 调整导入路径以匹配项目结构
from libs.models import DepartmentInDB, AccountInDB
from services.permission import PermissionService, PermissionError

# 导入部门相关的 Pydantic 模型
from ._schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentSchema,
)


# 定义部门服务类，封装与部门相关的数据库操作
class DepartmentService:
    session: Session  # 数据库会话对象，用于执行数据库操作
    account: AccountInDB  # 当前登录的用户对象
    _permission: PermissionService  # 权限服务对象，用于权限验证

    # 初始化方法，接收数据库会话对象和账户对象
    def __init__(self, session: Session, account: AccountInDB):
        self.session = session
        self.account = account
        self._permission = PermissionService(session, account)

    # 创建新部门的方法
    def create_department(
        self,
        department_data: DepartmentCreate,
    ) -> Optional[DepartmentSchema]:
        """创建新部门

        Args:
            department_data (DepartmentCreate): 包含部门信息的 Pydantic 模型

        Returns:
            Optional[DepartmentSchema]: 成功创建则返回部门信息模型，失败则返回 None
            
        Raises:
            PermissionError: 如果用户没有在指定公司创建部门的权限
        """
        # 检查权限
        if not self._permission.can_manage_company(department_data.company_id):
            raise PermissionError("您没有管理该公司的权限")

        # 如果指定了父部门，验证父部门是否存在且属于同一公司
        if department_data.parent_id:
            parent_stmt = select(DepartmentInDB).where(
                DepartmentInDB.id == department_data.parent_id,
                DepartmentInDB.company_id == department_data.company_id
            )
            parent_dept = self.session.execute(parent_stmt).scalar_one_or_none()
            if not parent_dept:
                # 抛出权限错误，因为父部门不存在或不属于指定公司
                raise PermissionError("指定的父部门不存在或不属于该公司")

        # 创建 DepartmentInDB 数据库模型实例
        department = DepartmentInDB(
            name=department_data.name,
            company_id=department_data.company_id,
            parent_id=department_data.parent_id,
            leader_id=department_data.leader_id,
            remark=department_data.remark,
        )
        
        # 将新部门对象添加到数据库会话
        self.session.add(department)
        try:
            # 提交事务，将更改保存到数据库
            self.session.commit()
            # 刷新对象，以获取数据库生成的值（如 ID）
            self.session.refresh(department)
            # 将数据库模型转换为 Pydantic 模型并返回
            return DepartmentSchema.model_validate(department)
        except IntegrityError:  # 捕获数据库完整性错误（例如，唯一约束冲突）
            # 回滚事务，撤销更改
            self.session.rollback()
            return None

    # 根据 ID 查询部门详情的方法
    def query_department_by_id(
        self, department_id: int
    ) -> Optional[DepartmentInDB]:
        """获取部门详情

        Args:
            department_id (int): 要查询的部门 ID

        Returns:
            Optional[DepartmentInDB]: 找到则返回部门数据库模型对象，否则返回 None
            
        Raises:
            PermissionError: 如果用户没有查看该部门的权限
        """
        # 构建查询语句，选择 DepartmentInDB 表
        stmt = (
            select(DepartmentInDB)
            # 预加载关联的公司信息、父部门和负责人信息
            .options(
                joinedload(DepartmentInDB.company),
                joinedload(DepartmentInDB.parent),
                joinedload(DepartmentInDB.leader),
            )
            # 添加查询条件：ID 匹配
            .where(DepartmentInDB.id == department_id)
        )
        
        # 执行查询并返回单个结果，如果未找到则返回 None
        department = self.session.execute(stmt).scalar_one_or_none()

        # 添加权限检查
        if department and not self._permission.can_view_company(department.company_id):
            raise PermissionError("您没有查看该公司部门的权限")

        return department

    # 列出部门的方法，要求必须提供公司 ID
    def list_departments(
        self, company_id: int
    ) -> List[DepartmentSchema]:
        """列出公司的所有部门

        Args:
            company_id (int): 公司 ID，必须提供

        Returns:
            List[DepartmentSchema]: 包含部门信息的 Pydantic 模型列表
            
        Raises:
            PermissionError: 如果用户没有查看该公司部门的权限
        """
        # 添加权限检查
        if not self._permission.can_view_company(company_id):
            raise PermissionError("您没有查看该公司部门的权限")

        # 构建基础查询语句，选择 DepartmentInDB 表
        stmt = (
            select(DepartmentInDB)
            .where(DepartmentInDB.company_id == company_id)
            .order_by(DepartmentInDB.id)
        )

        # 执行查询
        result = self.session.execute(stmt)
        # 获取所有查询结果（数据库模型对象）
        departments = result.scalars().all()
        # 将数据库模型列表转换为 Pydantic 模型列表并返回
        return [DepartmentSchema.model_validate(d) for d in departments]

    # 搜索部门的方法
    def search_departments(
        self, company_id: int, name: str
    ) -> List[DepartmentSchema]:
        """根据名称搜索部门

        Args:
            company_id (int): 公司 ID
            name (str): 部门名称，用于模糊匹配

        Returns:
            List[DepartmentSchema]: 匹配的部门列表
            
        Raises:
            PermissionError: 如果用户没有查看该公司部门的权限
        """
        # 添加权限检查
        if not self._permission.can_view_company(company_id):
            raise PermissionError("您没有查看该公司部门的权限")

        # 构建模糊搜索查询
        search_pattern = f"%{name}%"
        stmt = (
            select(DepartmentInDB)
            .where(
                DepartmentInDB.company_id == company_id,
                DepartmentInDB.name.like(search_pattern)
            )
            .order_by(DepartmentInDB.id)
        )

        # 执行查询
        result = self.session.execute(stmt)
        departments = result.scalars().all()
        return [DepartmentSchema.model_validate(d) for d in departments]

    # 更新部门信息的方法
    def update_department(
        self,
        department_id: int,
        department_data: DepartmentUpdate,
    ) -> Optional[DepartmentSchema]:
        """更新部门信息

        Args:
            department_id (int): 要更新的部门 ID
            department_data (DepartmentUpdate): 包含要更新的部门信息的 Pydantic 模型

        Returns:
            Optional[DepartmentSchema]: 成功更新则返回更新后的部门信息模型，失败或未找到则返回 None
            
        Raises:
            PermissionError: 如果用户没有更新该部门的权限
        """
        # 先根据 ID 查询部门是否存在
        department = self.query_department_by_id(department_id)
        # 如果部门不存在，返回 None
        if not department:
            return None

        # 添加权限检查
        if not self._permission.can_manage_company(department.company_id):
            raise PermissionError("您没有管理该公司部门的权限")

        # 确保不会循环引用父部门
        if department_data.parent_id and department_data.parent_id == department_id:
            raise ValueError("部门不能将自己设为父部门")

        # 如果更新了父部门，验证父部门是否存在且属于同一公司
        if department_data.parent_id:
            parent_stmt = select(DepartmentInDB).where(
                DepartmentInDB.id == department_data.parent_id,
                DepartmentInDB.company_id == department.company_id
            )
            parent_dept = self.session.execute(parent_stmt).scalar_one_or_none()
            if not parent_dept:
                # 抛出权限错误，因为父部门不存在或不属于指定公司
                raise PermissionError("指定的父部门不存在或不属于该公司")

        # 将 Pydantic 模型转换为字典，并排除未设置的字段（只更新传入的字段）
        update_data = department_data.model_dump(exclude_unset=True)

        # 遍历更新数据字典，更新部门对象的属性
        for key, value in update_data.items():
            setattr(department, key, value)

        try:
            # 提交事务，保存更改
            self.session.commit()
            # 刷新对象，获取更新后的状态
            self.session.refresh(department)
            # 将更新后的数据库模型转换为 Pydantic 模型并返回
            return DepartmentSchema.model_validate(department)
        except IntegrityError:  # 捕获可能的数据库完整性错误
            # 回滚事务
            self.session.rollback()
            return None

    # 删除部门的方法
    def delete_department(self, department_id: int) -> bool:
        """删除部门

        Args:
            department_id (int): 要删除的部门 ID

        Returns:
            bool: 删除成功返回 True，失败或未找到返回 False
            
        Raises:
            PermissionError: 如果用户没有删除该部门的权限
        """
        # 先根据 ID 查询部门是否存在
        department = self.query_department_by_id(department_id)
        # 如果部门不存在，返回 False
        if not department:
            return False

        # 添加权限检查
        if not self._permission.can_manage_company(department.company_id):
            raise PermissionError("您没有管理该公司部门的权限")

        try:
            # 检查是否有子部门
            child_departments_stmt = select(DepartmentInDB.id).where(
                DepartmentInDB.parent_id == department_id
            )
            has_children = self.session.execute(child_departments_stmt).first() is not None
            
            if has_children:
                raise ValueError("无法删除存在子部门的部门")

            # 检查是否有员工与此部门关联
            # 这部分代码取决于您的数据模型，可能需要调整
            has_employees = False
            if hasattr(department, 'employee_positions') and department.employee_positions:
                has_employees = len(department.employee_positions) > 0
            
            if has_employees:
                raise ValueError("无法删除存在员工的部门")

            # 从数据库会话中删除部门对象
            self.session.delete(department)
            # 提交事务，执行删除操作
            self.session.commit()
            # 返回 True 表示删除成功
            return True
        except IntegrityError as e:  # 捕获外键约束等完整性错误
            # 回滚事务
            self.session.rollback()
            return False
        except ValueError as e:
            # 回滚事务
            self.session.rollback()
            # 重新抛出异常，让调用方处理
            raise e
        except Exception:  # 捕获其他潜在异常
            # 回滚事务
            self.session.rollback()
            return False