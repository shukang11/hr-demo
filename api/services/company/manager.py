from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from libs.models import CompanyInDB, AccountInDB

from _schema import CompanyCreate, CompanyUpdate, CompanySchema


class CompanyService:
    session: Session
    # 表示的是当前登录的用户
    account: AccountInDB

    def __init__(self, session: Session, account: AccountInDB) -> None:
        self.session = session

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

        # 如果公司Id 和 name都没有传入，抛出异常
        if not company_id and not name:
            raise ValueError("Either company_id or name must be provided.")

        stmt = select(CompanyInDB).options(joinedload(CompanyInDB.members))
        if company_id:
            stmt = stmt.where(CompanyInDB.id == company_id)
        if name:
            stmt = stmt.where(CompanyInDB.name == name)

        return self.session.execute(stmt).scalar_one_or_none()

    def insert_company(self, company_data: CompanyCreate) -> Optional[CompanySchema]:
        """创建新公司

        Args:
            company_data: 公司创建数据

        Returns:
            Optional[CompanySchema]: 公司对象或None
        """
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
        try:
            company = self.query_company_by_id(company_id)
            if not company:
                return None

            # 更新公司信息
            company.name = company_data.name
            company.extra_value = company_data.extra_value
            company.extra_schema_id = company_data.extra_schema_id
            company.description = company_data.description

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
        try:
            company = self.query_company_by_id(company_id)
            if not company:
                return False

            self.session.delete(company)
            self.session.commit()
            return True
        except Exception as _e:
            self.session.rollback()
            return False
