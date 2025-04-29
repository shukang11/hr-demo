from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from libs.models import CandidateInDB, AccountInDB, CandidateStatus
from services.permission import PermissionService, PermissionError

from ._schema import (
    CandidateCreate,
    CandidateUpdate,
    CandidateStatusUpdate,
    CandidateSchema,
)


class CandidateService:
    """候选人服务类，封装与候选人相关的数据库操作"""
    session: Session  # 数据库会话对象
    account: AccountInDB  # 当前登录的用户对象
    _permission: PermissionService  # 权限服务对象

    def __init__(self, session: Session, account: AccountInDB):
        """初始化候选人服务
        
        Args:
            session: SQLAlchemy数据库会话
            account: 当前登录用户
        """
        self.session = session
        self.account = account
        self._permission = PermissionService(session, account)

    def create_candidate(
        self,
        candidate_data: CandidateCreate
    ) -> Optional[CandidateSchema]:
        """创建新的候选人记录
        
        Args:
            candidate_data: 包含候选人信息的Pydantic模型
            
        Returns:
            成功创建则返回候选人信息模型，失败则返回None
            
        Raises:
            PermissionError: 当用户没有权限在指定公司下创建候选人时
        """
        # 检查权限
        if not self._permission.can_manage_company(candidate_data.company_id):
            raise PermissionError("您没有在该公司创建候选人的权限")
        
        # 创建候选人数据库模型实例
        candidate = CandidateInDB(
            company_id=candidate_data.company_id,
            name=candidate_data.name,
            phone=candidate_data.phone,
            email=candidate_data.email,
            position_id=candidate_data.position_id,
            department_id=candidate_data.department_id,
            interview_date=candidate_data.interview_date,
            status=candidate_data.status,
            interviewer_id=candidate_data.interviewer_id,
            remark=candidate_data.remark,
            extra_value=candidate_data.extra_value,
            extra_schema_id=candidate_data.extra_schema_id,
        )
        
        # 添加到数据库会话
        self.session.add(candidate)
        try:
            # 提交事务，保存到数据库
            self.session.commit()
            # 刷新对象，获取生成的ID等
            self.session.refresh(candidate)
            # 将数据库模型转换为API响应模型
            return CandidateSchema.model_validate(candidate)
        except IntegrityError:
            # 处理数据库完整性错误
            self.session.rollback()
            return None
    
    def update_candidate(
        self,
        candidate_id: int,
        candidate_data: CandidateUpdate
    ) -> Optional[CandidateSchema]:
        """更新候选人信息
        
        Args:
            candidate_id: 候选人ID
            candidate_data: 包含要更新的字段的Pydantic模型
            
        Returns:
            成功更新则返回更新后的候选人信息模型，失败或未找到则返回None
            
        Raises:
            PermissionError: 当用户没有权限更新指定候选人时
        """
        # 先获取候选人信息
        candidate = self.query_candidate_by_id(candidate_id)
        if not candidate:
            return None
        
        # 检查权限
        if not self._permission.can_manage_company(candidate.company_id):
            raise PermissionError("您没有更新该候选人的权限")
        
        # 将Pydantic模型转换为字典，排除未设置的字段
        update_data = candidate_data.model_dump(exclude_unset=True)
        
        # 更新每个字段
        for key, value in update_data.items():
            setattr(candidate, key, value)
        
        try:
            # 提交事务，保存更改
            self.session.commit()
            # 刷新对象，获取最新状态
            self.session.refresh(candidate)
            # 转换为API响应模型
            return CandidateSchema.model_validate(candidate)
        except IntegrityError:
            # 处理数据库完整性错误
            self.session.rollback()
            return None
    
    def update_candidate_status(
        self,
        candidate_id: int,
        status_data: CandidateStatusUpdate
    ) -> Optional[CandidateSchema]:
        """更新候选人状态
        
        Args:
            candidate_id: 候选人ID
            status_data: 包含状态信息的Pydantic模型
            
        Returns:
            成功更新则返回更新后的候选人信息模型，失败或未找到则返回None
            
        Raises:
            PermissionError: 当用户没有权限更新指定候选人状态时
        """
        # 先获取候选人信息
        candidate = self.query_candidate_by_id(candidate_id)
        if not candidate:
            return None
        
        # 检查权限
        if not self._permission.can_manage_company(candidate.company_id):
            raise PermissionError("您没有更新该候选人状态的权限")
        
        # 更新状态相关字段
        candidate.status = status_data.status
        if status_data.evaluation is not None:
            candidate.evaluation = status_data.evaluation
        if status_data.remark is not None:
            candidate.remark = status_data.remark
        
        # 更新时间
        candidate.updated_at = datetime.now()
        
        try:
            # 提交事务，保存更改
            self.session.commit()
            # 刷新对象，获取最新状态
            self.session.refresh(candidate)
            # 转换为API响应模型
            return CandidateSchema.model_validate(candidate)
        except IntegrityError:
            # 处理数据库完整性错误
            self.session.rollback()
            return None
    
    def query_candidate_by_id(
        self,
        candidate_id: int
    ) -> Optional[CandidateInDB]:
        """根据ID查询候选人信息
        
        Args:
            candidate_id: 候选人ID
            
        Returns:
            找到则返回候选人数据库模型对象，否则返回None
            
        Raises:
            PermissionError: 当用户没有权限查看指定候选人时
        """
        # 构建查询语句
        stmt = (
            select(CandidateInDB)
            # 加载关联关系
            .options(
                joinedload(CandidateInDB.company),
                joinedload(CandidateInDB.extra_schema)
            )
            .where(CandidateInDB.id == candidate_id)
        )
        
        # 执行查询
        candidate = self.session.execute(stmt).scalar_one_or_none()
        
        # 检查权限
        if candidate and not self._permission.can_view_company(candidate.company_id):
            raise PermissionError("您没有查看该候选人的权限")
        
        return candidate
    
    def get_candidates_by_company(
        self,
        company_id: int,
        page: int = 1,
        limit: int = 10,
        status: Optional[CandidateStatus] = None,
        search: Optional[str] = None
    ) -> Tuple[List[CandidateSchema], int]:
        """获取指定公司的候选人列表，支持分页、状态筛选和搜索
        
        Args:
            company_id: 公司ID
            page: 页码，从1开始
            limit: 每页显示数量
            status: 可选的状态筛选条件
            search: 可选的搜索关键词（按姓名搜索）
            
        Returns:
            包含候选人列表和总数的元组
            
        Raises:
            PermissionError: 当用户没有权限查看指定公司的候选人时
        """
        # 检查权限
        if not self._permission.can_view_company(company_id):
            raise PermissionError("您没有查看该公司候选人的权限")
        
        # 构建基础查询
        stmt = (
            select(CandidateInDB)
            .where(CandidateInDB.company_id == company_id)
        )
        
        # 添加状态筛选条件
        if status:
            stmt = stmt.where(CandidateInDB.status == status)
        
        # 添加搜索条件
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(CandidateInDB.name.like(search_pattern))
        
        # 构建计数查询
        count_stmt = (
            select(func.count())
            .select_from(CandidateInDB)
            .where(CandidateInDB.company_id == company_id)
        )
        
        # 添加相同的筛选条件
        if status:
            count_stmt = count_stmt.where(CandidateInDB.status == status)
        if search:
            count_stmt = count_stmt.where(CandidateInDB.name.like(search_pattern))
        
        # 获取总数
        total = self.session.execute(count_stmt).scalar() or 0
        
        # 添加分页和排序
        stmt = (
            stmt
            .order_by(CandidateInDB.updated_at.desc(), CandidateInDB.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        
        # 执行查询
        candidates = self.session.execute(stmt).scalars().all()
        
        # 转换为API响应模型列表
        result = [CandidateSchema.model_validate(c) for c in candidates]
        
        return result, total
    
    def delete_candidate(self, candidate_id: int) -> bool:
        """删除候选人
        
        Args:
            candidate_id: 候选人ID
            
        Returns:
            删除成功返回True，失败或未找到返回False
            
        Raises:
            PermissionError: 当用户没有权限删除指定候选人时
        """
        # 先获取候选人信息
        candidate = self.query_candidate_by_id(candidate_id)
        if not candidate:
            return False
        
        # 检查权限
        if not self._permission.can_manage_company(candidate.company_id):
            raise PermissionError("您没有删除该候选人的权限")
        
        try:
            # 从数据库中删除
            self.session.delete(candidate)
            # 提交事务
            self.session.commit()
            return True
        except Exception:
            # 处理可能的错误
            self.session.rollback()
            return False