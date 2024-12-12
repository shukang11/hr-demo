from typing import Optional, List, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from models.account import AccountInDB
from models.company import CompanyInDB
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
                owner_id=self.current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # 添加到数据库
            self.session.add(new_company)
            self.session.commit()
            self.session.refresh(new_company)
            
            return new_company, None
        except Exception as e:
            self.session.rollback()
            return None, f"创建公司失败: {str(e)}"
