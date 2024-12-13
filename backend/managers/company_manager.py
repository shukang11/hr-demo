from typing import Optional, List, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from models.account import AccountInDB
from models.company import CompanyInDB, AccountCompanyInDB
from schema.company import CompanyCreate


class CompanyService:
    def __init__(self, current_user: AccountInDB, session: Session):
        self.current_user = current_user
        self.session = session

    def validate_member(self, member_id: int) -> Optional[AccountInDB]:
        """验证成员是否存在且合法
        
        Args:
            member_id: 成员ID
            
        Returns:
            Optional[AccountInDB]: 成员账户对象或None
        """
        stmt = select(AccountInDB).where(
            AccountInDB.id == member_id,
            AccountInDB.is_active.is_(True)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def find_company_by_id(self, company_id: int) -> Optional[CompanyInDB]:
        """根据ID查找公司
        
        Args:
            company_id: 公司ID
            
        Returns:
            Optional[CompanyInDB]: 公司对象或None
        """
        stmt = (
            select(CompanyInDB)
            .options(joinedload(CompanyInDB.members))
            .where(CompanyInDB.id == company_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def create_company(self, company_data: CompanyCreate) -> Tuple[Optional[CompanyInDB], Optional[str]]:
        """创建新公司
        
        Args:
            company_data: 公司创建数据
            
        Returns:
            Tuple[Optional[CompanyInDB], Optional[str]]: (公司对象, 错误信息)
        """
        try:
            # 创建新公司记录
            new_company = CompanyInDB(
                name=company_data.name,
                description=company_data.description,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.session.add(new_company)
            self.session.flush()
            
            # 创建账户-公司关系
            new_account_company = AccountCompanyInDB(
                account_id=self.current_user.id,
                company_id=new_company.id,
                role='owner'
            )
            
            # 添加到数据库
            self.session.add(new_account_company)
            self.session.flush()
            self.session.commit()
            return new_company, None
        except Exception as e:
            self.session.rollback()
            return None, f"创建公司失败: {str(e)}"
        
    def get_company_by_name(self, name: str) -> Optional[CompanyInDB]:
        """根据名称查找公司
        
        Args:
            name: 公司名称
            
        Returns:
            Optional[CompanyInDB]: 公司对象或None
        """
        # 查询公司及其关联的账户-公司关系
        stmt = (
            select(CompanyInDB, AccountCompanyInDB)
            .join(AccountCompanyInDB, CompanyInDB.id == AccountCompanyInDB.company_id)
            .where(CompanyInDB.name == name)
        )
        result = self.session.execute(stmt).first()
        
        if result:
            company: CompanyInDB
            account_company: AccountCompanyInDB
            company, account_company = result
            # 检查当前用户是否为公司创建者
            if account_company.account_id == self.current_user.id and account_company.role == 'owner':
                return company
        return None
