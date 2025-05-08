import logging  # 导入 logging
from sqlalchemy.orm import Session

# 导入所需模型
from libs.models import AccountInDB, AccountCompanyInDB, AccountCompanyRole
from sqlalchemy import select, exists  # 导入 select 和 exists

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
        # 检查用户是否是该公司的所有者或管理员
        stmt = select(
            exists().where(
                AccountCompanyInDB.account_id == self.account.id,
                AccountCompanyInDB.company_id == company_id,
                AccountCompanyInDB.role.in_(
                    [AccountCompanyRole.OWNER, AccountCompanyRole.ADMIN]
                ),
            )
        )
        has_permission = self.session.execute(stmt).scalar()

        if has_permission:
            log.debug(
                f"User '{self.account.username}' has specific role (owner/admin) for company {company_id}."
            )
            return True

        log.warning(
            f"User '{self.account.username}' lacks permission to manage company {company_id}."
        )
        return False

    def can_view_company(self, company_id: int) -> bool:
        """
        检查当前用户是否有权查看指定的公司。
        公司所有者、公司管理员以及公司普通成员都可以查看公司。

        Args:
            company_id (int): 目标公司的 ID。

        Returns:
            bool: 如果用户有权限则返回 True，否则返回 False。
        """
        # 检查用户是否与该公司有关联（任何角色）
        stmt = select(
            exists().where(
                AccountCompanyInDB.account_id == self.account.id,
                AccountCompanyInDB.company_id == company_id,
            )
        )
        is_associated = self.session.execute(stmt).scalar()

        if is_associated:
            log.debug(
                f"User '{self.account.username}' is associated with company {company_id} and can view it."
            )
            return True

        log.info(
            f"User '{self.account.username}' lacks permission to view company {company_id}."
        )
        return False

    def can_create_company(self) -> bool:
        """
        检查当前用户是否有权创建新的公司。
        所有激活状态的用户都可以创建公司。

        Returns:
            bool: 如果用户有权限则返回 True，否则返回 False。
        """
        # 检查用户是否处于激活状态
        if self.account.is_active:
            log.debug(f"User '{self.account.username}' can create a company.")
            return True

        log.warning(
            f"User '{self.account.username}' is inactive and cannot create a company."
        )
        return False

    def is_super_admin(self, company_id: int = None) -> bool:
        """
        检查用户是否为超级管理员。
        在此实现中，我们使用can_manage_company方法作为判断依据。

        Args:
            company_id (int, optional): 公司ID，如果提供将检查用户是否为该公司的管理员。
                                       如果不提供，则默认根据用户的公司关联判断。

        Returns:
            bool: 如果用户是超级管理员则返回True，否则返回False。
        """
        if company_id is None:
            # 如果未提供company_id，记录警告并默认返回False
            log.warning(
                f"is_super_admin called without company_id by user '{self.account.username}'"
            )
            return False

        # 使用can_manage_company方法判断用户是否有管理该公司的权限
        return self.can_manage_company(company_id)
