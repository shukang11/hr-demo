import logging  # 导入 logging
from sqlalchemy.orm import Session

# 导入所需模型
from libs.models import AccountInDB, PositionInDB, EmployeeInDB  # 导入模型
from sqlalchemy import select  # 导入 select

log = logging.getLogger(__name__)


class PermissionService:
    """权限服务类

    封装了与权限相关的核心业务逻辑，如权限验证和信息查询。
    """

    session: Session
    account: AccountInDB  # 添加 account 属性类型提示

    def __init__(self, session: Session, account: AccountInDB) -> None:
        """初始化权限服务

        Args:
            session (Session): SQLAlchemy 数据库会话对象。
            account (AccountInDB): 账户信息对象。
        """
        if not account:
            # 权限服务必须基于一个有效的用户
            log.error("PermissionService initialized without a valid account.")
            raise ValueError("PermissionService requires a valid account.")
        self.session = session
        self.account = account

    def can_manage_company(self, company_id: int) -> bool:
        """
        检查当前用户是否有权管理指定的公司。

        Args:
            company_id (int): 目标公司的 ID。

        Returns:
            bool: 如果用户有权限则返回 True，否则返回 False。
        """
        # 1. 检查是否为全局管理员
        if self.account.is_admin:
            log.debug(
                f"User '{self.account.username}' (Admin) has permission for company {company_id}."
            )
            return True

        # 2. 检查用户是否是该公司的所有者或管理员
        from libs.models import AccountCompanyInDB, AccountCompanyRole

        stmt = select(AccountCompanyInDB).where(
            AccountCompanyInDB.account_id == self.account.id,
            AccountCompanyInDB.company_id == company_id,
            AccountCompanyInDB.role.in_(
                [AccountCompanyRole.OWNER, AccountCompanyRole.ADMIN]
            ),
        )
        has_permission = self.session.execute(stmt).scalar_one_or_none() is not None

        if has_permission:
            log.debug(
                f"User '{self.account.username}' has specific role (owner/admin) for company {company_id}."
            )
            return True

        log.warning(
            f"User '{self.account.username}' lacks permission to manage company {company_id}."
        )
        return False

    def can_manage_position(self, position_id: int) -> bool:
        """
        检查当前用户是否有权管理指定的职位。
        权限通常继承自对该职位所属公司的管理权限。

        Args:
            position_id (int): 目标职位的 ID。

        Returns:
            bool: 如果用户有权限则返回 True，否则返回 False。
        """
        # 先尝试通过 ID 获取职位对象
        position = self.session.get(PositionInDB, position_id)
        if not position:
            log.warning(
                f"Position {position_id} not found for permission check by user '{self.account.username}'."
            )
            return False  # 职位不存在，自然无权管理

        # 检查是否能管理该职位所属的公司
        # 注意：PositionInDB 需要有 company_id 属性
        if position.company_id:
            can_manage = self.can_manage_company(position.company_id)
            if can_manage:
                log.debug(
                    f"User '{self.account.username}' has permission for position {position_id} via company {position.company_id}."
                )
                return True
        else:
            # 如果职位没有关联公司，或者 company_id 为空，则根据业务逻辑判断
            # 可能是全局职位，只有管理员能管理
            if self.account.is_admin:
                log.debug(
                    f"User '{self.account.username}' (Admin) has permission for position {position_id} (no company link or global)."
                )
                return True
            log.warning(
                f"Position {position_id} has no company link, and user '{self.account.username}' is not admin."
            )

        # --- TODO: 未来扩展 ---
        # 可能有更细粒度的职位管理权限设置，例如基于部门权限

        log.warning(
            f"User '{self.account.username}' lacks permission to manage position {position_id}."
        )
        return False

    def can_manage_employee(self, employee_id: int) -> bool:
        """
        检查当前用户是否有权管理指定的员工。
        权限通常继承自对该员工所属公司/部门的管理权限。

        Args:
            employee_id (int): 目标员工的 ID。

        Returns:
            bool: 如果用户有权限则返回 True，否则返回 False。
        """
        # 先尝试通过 ID 获取员工对象
        employee = self.session.get(EmployeeInDB, employee_id)
        if not employee:
            log.warning(
                f"Employee {employee_id} not found for permission check by user '{self.account.username}'."
            )
            return False  # 员工不存在

        # --- 当前实现：仅全局管理员有权限 ---
        # 或者，更合理的做法是检查用户是否能管理该员工所属的公司
        # 需要确定员工如何关联到公司，这可能需要通过职位或部门
        # 假设员工通过 EmployeePositionInDB 关联到职位，再关联到公司
        # (需要 EmployeeInDB 有 positions 关系，且 EmployeePositionInDB 有 position 关系，PositionInDB 有 company_id)

        # 示例逻辑：通过员工的第一个职位找到公司ID
        company_id_to_check = None
        if hasattr(employee, "positions") and employee.positions:
            first_employee_position = employee.positions[0]
            if (
                hasattr(first_employee_position, "position")
                and first_employee_position.position
            ):
                position = first_employee_position.position
                if hasattr(position, "company_id") and position.company_id:
                    company_id_to_check = position.company_id

        if company_id_to_check:
            can_manage = self.can_manage_company(company_id_to_check)
            if can_manage:
                log.debug(
                    f"User '{self.account.username}' has permission for employee {employee_id} via company {company_id_to_check}."
                )
                return True
        else:
            # 如果无法通过职位关联到公司，检查是否是全局管理员
            if self.account.is_admin:
                log.debug(
                    f"User '{self.account.username}' (Admin) has permission for employee {employee_id} (no company link or global)."
                )
                return True
            log.warning(
                f"Could not determine company for employee {employee_id} to check permissions, and user '{self.account.username}' is not admin."
            )

        # --- TODO: 未来扩展 ---
        # 1. 可能需要更复杂的逻辑来确定员工所属的管理单元（公司/部门）。
        # 2. 检查用户是否有权管理该公司/部门。
        # 3. 考虑直线经理等特定角色权限。

        log.warning(
            f"User '{self.account.username}' lacks permission to manage employee {employee_id}."
        )
        return False

    # 可以根据需要添加更多权限检查方法，例如：
    # def can_view_company(self, company_id: int) -> bool: ...
    # def can_create_position_in_company(self, company_id: int) -> bool: ...
    # def can_assign_employee_to_position(self, employee_id: int, position_id: int) -> bool: ...
