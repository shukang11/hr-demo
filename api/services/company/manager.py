from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload, selectinload
from datetime import datetime

from libs.models import CompanyInDB, AccountInDB, AccountCompanyInDB
from libs.models.account_company import AccountCompanyRole

from ._schema import (
    CompanyCreate,
    CompanyUpdate,
    CompanySchema,
    CompanyDetailSchema,
    SubsidiaryInfo,
)
from services.permission import PermissionService


class CompanyService:
    session: Session
    # 表示的是当前登录的用户
    account: AccountInDB

    _permission: PermissionService

    def __init__(self, session: Session, account: AccountInDB) -> None:
        self.session = session
        self.account = account
        self._permission = PermissionService(session, account)

    def query_company_by(
        self, company_id: Optional[int] = None, name: Optional[str] = None
    ) -> Optional[CompanyInDB]:
        """根据ID查找公司

        Args:
            company_id: 公司ID
            name: 公司名称

        Returns:
            Optional[CompanyInDB]: 公司对象或None
        """

        if not self._permission.can_view_company(company_id):
            raise PermissionError("You do not have permission to view this company.")

        # 如果公司Id 和 name都没有传入，抛出异常
        if not company_id and not name:
            raise PermissionError(
                "Either company_id or name must be provided to query a company."
            )

        stmt = select(CompanyInDB).options(joinedload(CompanyInDB.members))
        if company_id:
            stmt = stmt.where(CompanyInDB.id == company_id)
        if name:
            stmt = stmt.where(CompanyInDB.name == name)

        return self.session.execute(stmt).scalar_one_or_none()

    def is_company_owner(
        self, account_id: int, company_id: Optional[int] = None
    ) -> bool:
        """检查用户是否是公司的所有者

        Args:
            account_id: 用户ID
            company_id: 公司ID，如果为None则检查用户是否是任何公司的所有者

        Returns:
            bool: 是否是公司所有者
        """
        stmt = select(AccountCompanyInDB).where(
            AccountCompanyInDB.account_id == account_id,
            AccountCompanyInDB.role == AccountCompanyRole.OWNER,
        )
        if company_id:
            stmt = stmt.where(AccountCompanyInDB.company_id == company_id)

        result = self.session.execute(stmt).first()
        return result is not None

    def get_companies_paginated(
        self, page: int = 1, limit: int = 10
    ) -> Tuple[List[CompanySchema], int]:
        """获取分页的公司列表

        只返回当前用户有权限查看的公司

        Args:
            page: 页码，从1开始
            limit: 每页显示数量

        Returns:
            Tuple[List[CompanySchema], int]: 公司列表和总数
        """
        # 检查用户是否是任何公司的所有者
        is_owner = self.is_company_owner(self.account.id)

        # 如果是公司所有者，查询与用户关联的公司
        # 普通用户只能查看自己有关联的公司
        stmt = (
            select(CompanyInDB)
            .join(AccountCompanyInDB, CompanyInDB.id == AccountCompanyInDB.company_id)
            .where(AccountCompanyInDB.account_id == self.account.id)
        )
        count_stmt = (
            select(func.count())
            .select_from(CompanyInDB)
            .join(AccountCompanyInDB, CompanyInDB.id == AccountCompanyInDB.company_id)
            .where(AccountCompanyInDB.account_id == self.account.id)
        )

        # 计算总数
        total = self.session.execute(count_stmt).scalar() or 0

        # 分页查询
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        # 执行查询
        companies = self.session.execute(stmt).scalars().all()

        # 转换为API响应模型
        result = [CompanySchema.model_validate(c) for c in companies]

        return result, total

    def search_companies_by_name(
        self, name: str, page: int = 1, limit: int = 10
    ) -> Tuple[List[CompanySchema], int]:
        """按名称搜索公司，支持分页

        只返回当前用户有权限查看的公司

        Args:
            name: 公司名称（模糊匹配）
            page: 页码，从1开始
            limit: 每页显示数量

        Returns:
            Tuple[List[CompanySchema], int]: 匹配的公司列表和总数
        """
        # 构建模糊搜索条件
        search_pattern = f"%{name}%"

        # 普通用户只能查看自己有关联的公司
        stmt = (
            select(CompanyInDB)
            .join(AccountCompanyInDB, CompanyInDB.id == AccountCompanyInDB.company_id)
            .where(
                AccountCompanyInDB.account_id == self.account.id,
                CompanyInDB.name.like(search_pattern),
            )
        )
        count_stmt = (
            select(func.count())
            .select_from(CompanyInDB)
            .join(AccountCompanyInDB, CompanyInDB.id == AccountCompanyInDB.company_id)
            .where(
                AccountCompanyInDB.account_id == self.account.id,
                CompanyInDB.name.like(search_pattern),
            )
        )

        # 计算总数
        total = self.session.execute(count_stmt).scalar() or 0

        # 分页查询
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        # 执行查询
        companies = self.session.execute(stmt).scalars().all()

        # 转换为API响应模型
        result = [CompanySchema.model_validate(c) for c in companies]

        return result, total

    def insert_company(self, company_data: CompanyCreate) -> Optional[CompanySchema]:
        """创建新公司

        Args:
            company_data: 公司创建数据

        Returns:
            Optional[CompanySchema]: 公司对象或None
        """
        if not self._permission.can_create_company():
            raise PermissionError("You do not have permission to create a company.")
        # 检查是否有权限创建公司
        try:
            # 创建新公司记录
            new_company = CompanyInDB(
                name=company_data.name,
                extra_value=company_data.extra_value,
                extra_schema_id=company_data.extra_schema_id,
                description=company_data.description,
                created_at=datetime.now(datetime.timezone.utc),
                updated_at=datetime.now(datetime.timezone.utc),
            )
            self.session.add(new_company)
            self.session.flush()  # 获取ID

            # 为当前用户添加与新公司的关联，设置为公司拥有者
            company_relation = AccountCompanyInDB(
                account_id=self.account.id,
                company_id=new_company.id,
                role=AccountCompanyRole.OWNER,
            )
            self.session.add(company_relation)

            self.session.commit()
            return CompanySchema.model_validate(new_company)
        except Exception as _e:
            self.session.rollback()
            return None

    def update_company(
        self, company_id: int, company_data: CompanyUpdate
    ) -> Optional[CompanySchema]:
        """更新公司信息

        Args:
            company_id: 公司ID
            company_data: 更新数据

        Returns:
            Optional[CompanySchema]: 更新后的公司对象或None
        """

        if not self._permission.can_manage_company(company_id):
            raise PermissionError("You do not have permission to manage this company.")

        try:
            company = self.query_company_by(company_id=company_id)
            if not company:
                return None

            # 更新公司信息
            if company_data.name is not None:
                company.name = company_data.name
            if company_data.extra_value is not None:
                company.extra_value = company_data.extra_value
            if company_data.extra_schema_id is not None:
                company.extra_schema_id = company_data.extra_schema_id
            if company_data.description is not None:
                company.description = company_data.description

            company.updated_at = datetime.now(datetime.timezone.utc)

            self.session.commit()
            return CompanySchema.model_validate(company)
        except Exception as _e:
            self.session.rollback()
            return None

    def delete_company(self, company_id: int) -> bool:
        """删除公司

        Args:
            company_id: 公司ID

        Returns:
            bool: 删除成功与否
        """
        if not self._permission.can_manage_company(company_id):
            raise PermissionError("You do not have permission to manage this company.")

        try:
            company = self.query_company_by(company_id=company_id)
            if not company:
                return False

            self.session.delete(company)
            self.session.commit()
            return True
        except Exception as _e:
            self.session.rollback()
            return False

    def get_company_detail(self, company_id: int) -> Optional[CompanyDetailSchema]:
        """获取公司详情，包括父公司和子公司信息

        Args:
            company_id: 公司ID

        Returns:
            Optional[CompanyDetailSchema]: 详细的公司信息或None
        """
        if not self._permission.can_view_company(company_id):
            raise PermissionError("You do not have permission to view this company.")

        # 使用 joinedload 加载关联的父公司和子公司信息
        stmt = (
            select(CompanyInDB)
            .options(
                joinedload(CompanyInDB.parent), joinedload(CompanyInDB.subsidiaries)
            )
            .where(CompanyInDB.id == company_id)
        )

        company = self.session.execute(stmt).scalar_one_or_none()
        if not company:
            return None

        # 构建详细响应
        result = CompanyDetailSchema(
            id=company.id,
            name=company.name,
            description=company.description,
            parent_id=company.parent_id,
            extra_value=company.extra_value,
            extra_schema_id=company.extra_schema_id,
            created_at=company.created_at,
            updated_at=company.updated_at,
            subsidiaries=[
                SubsidiaryInfo(id=sub.id, name=sub.name) for sub in company.subsidiaries
            ],
        )

        # 如果有父公司，添加父公司信息
        if company.parent:
            result.parent_company = CompanySchema(
                id=company.parent.id,
                name=company.parent.name,
                description=company.parent.description,
                parent_id=company.parent.parent_id,
                extra_value=company.parent.extra_value,
                extra_schema_id=company.parent.extra_schema_id,
                created_at=company.parent.created_at,
                updated_at=company.parent.updated_at,
            )

        return result

    def get_subsidiaries(self, company_id: int) -> List[CompanySchema]:
        """获取公司的子公司列表

        Args:
            company_id: 公司ID

        Returns:
            List[CompanySchema]: 子公司列表
        """
        if not self._permission.can_view_company(company_id):
            raise PermissionError("You do not have permission to view this company.")

        # 检查公司是否存在
        company = self.query_company_by(company_id=company_id)
        if not company:
            return []

        # 查询所有子公司
        stmt = select(CompanyInDB).where(CompanyInDB.parent_id == company_id)
        subsidiaries = self.session.execute(stmt).scalars().all()

        # 转换为API响应模型
        result = [CompanySchema.model_validate(c) for c in subsidiaries]

        return result

    def add_subsidiary(
        self, parent_id: int, company_data: CompanyCreate
    ) -> Optional[CompanySchema]:
        """添加子公司

        Args:
            parent_id: 父公司ID
            company_data: 子公司数据

        Returns:
            Optional[CompanySchema]: 新创建的子公司信息或None
        """
        if not self._permission.can_manage_company(parent_id):
            raise PermissionError("You do not have permission to manage this company.")

        # 检查父公司是否存在
        parent_company = self.query_company_by(company_id=parent_id)
        if not parent_company:
            return None

        try:
            # 创建子公司
            new_company = CompanyInDB(
                name=company_data.name,
                description=company_data.description,
                parent_id=parent_id,  # 设置父公司ID
                extra_value=company_data.extra_value,
                extra_schema_id=company_data.extra_schema_id,
                created_at=datetime.now(datetime.timezone.utc),
                updated_at=datetime.now(datetime.timezone.utc),
            )
            self.session.add(new_company)

            # 创建用户与子公司的关系
            relation = AccountCompanyInDB(
                account_id=self.account.id,
                company_id=new_company.id,
                role=AccountCompanyRole.OWNER,
            )
            self.session.add(relation)

            self.session.commit()
            return CompanySchema.model_validate(new_company)
        except Exception as e:
            self.session.rollback()
            raise e

    def get_company_detail(self, company_id: int) -> Optional[CompanyDetailSchema]:
        """获取公司详情，包括父公司和子公司信息

        Args:
            company_id: 公司ID

        Returns:
            Optional[CompanyDetailSchema]: 包含子公司信息的公司详情
        """
        if not self._permission.can_view_company(company_id):
            raise PermissionError("You do not have permission to view this company.")

        try:
            # 查询公司信息，并加载父公司和子公司
            stmt = (
                select(CompanyInDB)
                .options(
                    joinedload(CompanyInDB.parent),  # 加载父公司
                    selectinload(CompanyInDB.subsidiaries),  # 加载子公司
                )
                .where(CompanyInDB.id == company_id)
            )

            company = self.session.execute(stmt).scalar_one_or_none()
            if not company:
                return None

            # 转换为详细Schema
            result = CompanyDetailSchema.model_validate(company)

            # 如果有父公司，添加父公司信息
            if company.parent:
                result.parent_company = CompanySchema.model_validate(company.parent)

            # 添加子公司信息
            result.subsidiaries = [
                SubsidiaryInfo(id=sub.id, name=sub.name) for sub in company.subsidiaries
            ]

            return result
        except Exception as e:
            print(f"获取公司详情失败: {e}")
            return None

    def get_subsidiaries(self, company_id: int) -> List[CompanySchema]:
        """获取指定公司的子公司列表

        Args:
            company_id: 父公司ID

        Returns:
            List[CompanySchema]: 子公司列表
        """
        if not self._permission.can_view_company(company_id):
            raise PermissionError("You do not have permission to view this company.")

        try:
            # 查询子公司
            stmt = select(CompanyInDB).where(CompanyInDB.parent_id == company_id)

            subsidiaries = self.session.execute(stmt).scalars().all()
            return [CompanySchema.model_validate(sub) for sub in subsidiaries]
        except Exception as e:
            print(f"获取子公司列表失败: {e}")
            return []

    def add_subsidiary(
        self, parent_id: int, company_data: CompanyCreate
    ) -> Optional[CompanySchema]:
        """添加子公司

        Args:
            parent_id: 父公司ID
            company_data: 子公司数据

        Returns:
            Optional[CompanySchema]: 创建的子公司信息
        """
        if not self._permission.can_manage_company(parent_id):
            raise PermissionError("You do not have permission to manage this company.")

        # 检查父公司是否存在
        parent_company = self.query_company_by(company_id=parent_id)
        if not parent_company:
            return None

        try:
            # 创建子公司
            subsidiary = CompanyInDB(
                name=company_data.name,
                description=company_data.description,
                extra_value=company_data.extra_value,
                extra_schema_id=company_data.extra_schema_id,
                parent_id=parent_id,  # 设置父公司ID
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            self.session.add(subsidiary)
            self.session.flush()  # 获取自增ID

            # 创建当前用户与子公司的关系
            relation = AccountCompanyInDB(
                account_id=self.account.id,
                company_id=subsidiary.id,
                role=AccountCompanyRole.OWNER,  # 设置为所有者角色
            )
            self.session.add(relation)

            self.session.commit()
            return CompanySchema.model_validate(subsidiary)
        except Exception as e:
            self.session.rollback()
            print(f"创建子公司失败: {e}")
            return None
