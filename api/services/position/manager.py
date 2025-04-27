from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

# 调整导入路径以匹配项目结构
from libs.models import PositionInDB, AccountInDB
from services.permission import PermissionService, PermissionError

# 导入职位相关的 Pydantic 模型（用于数据验证和序列化）
from ._schema import (
    PositionCreate,
    PositionUpdate,
    PositionSchema,
)  # Import new schemas


# 定义职位服务类，封装与职位相关的数据库操作
class PositionService:
    session: Session  # 数据库会话对象，用于执行数据库操作
    account: AccountInDB  # 当前登录的用户对象

    _permission: PermissionService  # 权限服务对象，用于权限验证

    # 初始化方法，接收数据库会话对象
    def __init__(self, session: Session, account: AccountInDB):  # Removed current_user
        self.session = session
        self.account = account
        self._permission = PermissionService(session, account)

    # 创建新职位的方法
    def create_position(
        self,
        position_data: PositionCreate,  # 使用 PositionCreate 模型验证输入数据
    ) -> Optional[PositionSchema]:  # 返回 PositionSchema 模型或 None
        """创建新职位

        Args:
            position_data (PositionCreate): 包含职位信息的 Pydantic 模型

        Returns:
            Optional[PositionSchema]: 成功创建则返回职位信息模型，失败则返回 None
        """

        if not self._permission.can_manage_company(position_data.company_id):
            raise PermissionError("您没有管理该公司的权限")

        # 可选：验证关联的部门是否存在
        # stmt_dep = select(DepartmentInDB).where(DepartmentInDB.id == position_data.department_id)
        # department = self.session.execute(stmt_dep).scalar_one_or_none()
        # if not department:
        #     # 或者抛出特定的异常
        #     return None

        # 创建 PositionInDB 数据库模型实例
        position = PositionInDB(
            name=position_data.name,  # 使用 Pydantic 模型中的 name 字段
            company_id=position_data.company_id,  # 添加 company_id 字段
            remark=position_data.remark,  # 使用 Pydantic 模型中的 remark 字段
            # 假设 created_at/updated_at 由 BaseModel 或数据库默认值处理
        )
        # 将新职位对象添加到数据库会话
        self.session.add(position)
        try:
            # 提交事务，将更改保存到数据库
            self.session.commit()
            # 刷新对象，以获取数据库生成的值（如 ID）
            self.session.refresh(position)
            # 将数据库模型转换为 Pydantic 模型并返回
            return PositionSchema.model_validate(position)
        except IntegrityError:  # 捕获数据库完整性错误（例如，唯一约束冲突）
            # 回滚事务，撤销更改
            self.session.rollback()
            # 考虑记录错误日志
            # 可以抛出更具体的异常，例如 ValueError("职位创建失败 - 可能存在重复名称或无效公司")
            return None  # 返回 None 表示创建失败

    # 根据 ID 查询职位详情的方法
    def query_position_by_id(
        self, position_id: int
    ) -> Optional[PositionInDB]:  # 返回数据库模型或 None
        """获取职位详情

        Args:
            position_id (int): 要查询的职位 ID

        Returns:
            Optional[PositionInDB]: 找到则返回职位数据库模型对象，否则返回 None
        """

        # 构建查询语句，选择 PositionInDB 表
        stmt = (
            select(PositionInDB)
            # 可选：根据需要调整预加载的关联关系
            # .options(joinedload(PositionInDB.department))
            # 预加载关联的公司信息，避免 N+1 查询问题
            .options(joinedload(PositionInDB.company))
            # 添加查询条件：ID 匹配
            .where(PositionInDB.id == position_id)
        )
        # 执行查询并返回单个结果，如果未找到则返回 None
        position = self.session.execute(stmt).scalar_one_or_none()

        # 添加权限检查
        if position and not self._permission.can_view_company(position.company_id):
            raise PermissionError("您没有查看该公司职位的权限")

        return position

    # 列出职位的方法，要求必须提供公司 ID
    def list_positions(
        self, company_id: int
    ) -> List[PositionSchema]:  # 返回 PositionSchema 模型列表
        """列出公司的所有职位

        Args:
            company_id (int): 公司 ID，必须提供

        Returns:
            List[PositionSchema]: 包含职位信息的 Pydantic 模型列表
        """
        # 添加权限检查
        if not self._permission.can_view_company(company_id):
            raise PermissionError("您没有查看该公司职位的权限")

        # 构建基础查询语句，选择 PositionInDB 表
        stmt = (
            select(PositionInDB)
            .where(PositionInDB.company_id == company_id)
            .order_by(PositionInDB.id)
        )

        # 执行查询
        result = self.session.execute(stmt)
        # 获取所有查询结果（数据库模型对象）
        positions = result.scalars().all()
        # 将数据库模型列表转换为 Pydantic 模型列表并返回
        return [PositionSchema.model_validate(p) for p in positions]

    # 更新职位信息的方法
    def update_position(
        self,
        position_id: int,
        position_data: PositionUpdate,  # 使用 PositionUpdate 模型验证输入数据
    ) -> Optional[PositionSchema]:  # 返回更新后的 PositionSchema 模型或 None
        """更新职位信息

        Args:
            position_id (int): 要更新的职位 ID
            position_data (PositionUpdate): 包含要更新的职位信息的 Pydantic 模型

        Returns:
            Optional[PositionSchema]: 成功更新则返回更新后的职位信息模型，失败或未找到则返回 None
        """
        # 先根据 ID 查询职位是否存在
        position = self.query_position_by_id(position_id)
        # 如果职位不存在，返回 None
        if not position:
            return None

        # 添加权限检查
        if not self._permission.can_manage_company(position.company_id):
            raise PermissionError("您没有管理该公司职位的权限")

        # 将 Pydantic 模型转换为字典，并排除未设置的字段（只更新传入的字段）
        update_data = position_data.model_dump(exclude_unset=True)

        # 遍历更新数据字典，更新职位对象的属性
        for key, value in update_data.items():
            setattr(position, key, value)

        # 如果需要手动更新 updated_at 字段，可以在这里添加逻辑
        # from datetime import datetime, timezone
        # position.updated_at = datetime.now(timezone.utc)

        try:
            # 提交事务，保存更改
            self.session.commit()
            # 刷新对象，获取更新后的状态
            self.session.refresh(position)
            # 将更新后的数据库模型转换为 Pydantic 模型并返回
            return PositionSchema.model_validate(position)
        except IntegrityError:  # 捕获可能的数据库完整性错误
            # 回滚事务
            self.session.rollback()
            # 考虑记录错误日志
            # 可以抛出更具体的异常，例如 ValueError("职位更新失败 - 可能存在重复名称或无效公司")
            return None  # 返回 None 表示更新失败

    # 删除职位的方法
    def delete_position(self, position_id: int) -> bool:
        """删除职位

        Args:
            position_id (int): 要删除的职位 ID

        Returns:
            bool: 删除成功返回 True，失败或未找到返回 False
        """
        # 先根据 ID 查询职位是否存在
        position = self.query_position_by_id(position_id)
        # 如果职位不存在，返回 False
        if not position:
            return False

        # 添加权限检查
        if not self._permission.can_manage_company(position.company_id):
            raise PermissionError("您没有管理该公司职位的权限")

        try:
            # 在删除前检查依赖关系（例如，是否有员工属于此职位）
            # if position.employee_positions: # 假设存在关联关系 employee_positions
            #    raise ValueError("无法删除存在员工的职位")

            # 从数据库会话中删除职位对象
            self.session.delete(position)
            # 提交事务，执行删除操作
            self.session.commit()
            # 返回 True 表示删除成功
            return True
        except IntegrityError as e:  # 捕获外键约束等完整性错误
            # 回滚事务
            self.session.rollback()
            # 考虑记录错误日志
            # 可以抛出更具体的异常，例如 ValueError(f"无法删除职位: {e}")
            return False
        except Exception as e:  # 捕获其他潜在异常（例如上面手动抛出的 ValueError）
            # 回滚事务
            self.session.rollback()
            # 考虑记录错误日志
            # print(f"删除职位时出错: {e}") # 或者使用更规范的日志记录
            return False
