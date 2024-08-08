from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from core.controller._base import BaseController
from core.database import (
    AccountInterviewRecordInDB,
    CompanyMapAccountContractInDB,
    DepartmentMapAccountInDB,
    CompanyMapAccountInDB,
    AccountInDB,
)
from core.database.department import DepartmentInDB
from .schema import (
    InterviewEmployeePayload,
    QueryEmployeePayload,
    RecruitEmployeePayload,
)


# 以公司为主体或者操作对象为公司级别的控制器
class HumanResourceManager(BaseController):
    def __init__(self, session: Session) -> None:
        self.session = session

    # MARK: - 招聘员工
    # 面试招聘员工
    def insert_interview_employee_record(
        self, payload: InterviewEmployeePayload
    ) -> AccountInterviewRecordInDB:
        record: AccountInterviewRecordInDB
        if payload.id:
            # 更新
            stmt = select(AccountInterviewRecordInDB).where(
                AccountInterviewRecordInDB.id == payload.id
            )
            record = self.session.scalar(stmt)
            if not record:
                raise ValueError("面试记录不存在")
            if payload.interview_at:
                record.interview_at = payload.interview_at
            if payload.remark:
                record.remark = payload.remark
            if payload.is_pass is not None:
                record.is_pass = payload.is_pass

        else:
            # 创建
            record = AccountInterviewRecordInDB(
                account_id=payload.account_id,
                company_id=payload.company_id,
                job_id=payload.job_id,
                interview_at=payload.interview_at,
                is_pass=payload.is_pass,
                remark=payload.remark,
            )
        self.session.add(record)
        return record

    # 确定面试通过，签定合同
    def recruit_employee(
        self, payload: RecruitEmployeePayload
    ) -> CompanyMapAccountInDB:
        # 开启事务
        with self.session.begin():
            # 首先我们先签定合约
            contract = CompanyMapAccountContractInDB(
                contract_type=payload.contract_type,
                account_id=payload.account_id,
                company_id=payload.company_id,
                job_id=payload.job_id,
                contract_start_at=payload.contract_start_at,
                contract_end_at=payload.contract_end_at,
            )
            self.session.add(contract)
            # 然后绑定和公司的关系
            stmt = select(CompanyMapAccountInDB).where(
                CompanyMapAccountInDB.account_id == payload.account_id,
                CompanyMapAccountInDB.company_id == payload.company_id,
            )
            company_map_account = self.session.scalar(stmt)
            if not company_map_account:
                company_map_account = CompanyMapAccountInDB(
                    account_id=payload.account_id,
                    company_id=payload.company_id,
                )
                company_map_account.contracts = [contract]
            else:
                company_map_account.contracts.append(contract)
            self.session.add(company_map_account)
            return company_map_account

    # 分配员工到部门
    def assign_employee_to_department(
        self,
        account_id: int,
        company_id: int,
        department_id: Optional[int],
        job_id: int,
    ) -> CompanyMapAccountInDB:
        # 查询员工和公司的关系
        stmt = select(DepartmentMapAccountInDB).where(
            DepartmentMapAccountInDB.account_id == account_id,
            DepartmentMapAccountInDB.company_id == company_id,
        )
        department_map_account = self.session.scalar(stmt)
        if not department_map_account:
            department_map_account = DepartmentMapAccountInDB(
                account_id=account_id,
                company_id=company_id,
                department_id=department_id,
                job_id=job_id,
            )
        else:
            department_map_account.department_id = department_id
            department_map_account.job_id = job_id
        self.session.add(department_map_account)

        return department_map_account

    # MARK: - 查询
    def get_department(self, company_id: int) -> List[DepartmentInDB]:
        stmt = select(DepartmentInDB).where(DepartmentInDB.company_id == company_id)
        return self.session.execute(stmt).scalars().all()

    def get_employee(
        self, payload: QueryEmployeePayload
    ) -> List[CompanyMapAccountInDB]:
        assert self.operator_id, "operator_id is required"

        stmt = select(CompanyMapAccountInDB).options(
            joinedload(CompanyMapAccountInDB.contracts),
            joinedload(CompanyMapAccountInDB.account),
        )

        options = [AccountInDB.creator_id == self.operator_id]
        if payload.company_id:
            options.append(CompanyMapAccountInDB.company_id == payload.company_id)
        if payload.job_id:
            options.append(CompanyMapAccountInDB.job_id == payload.job_id)
        if payload.department_id:
            options.append(CompanyMapAccountInDB.department_id == payload.department_id)
        if len(payload.contract_type) > 0:
            options.append(
                CompanyMapAccountInDB.contract_type.in_(payload.contract_type)
            )

        stmt = select(CompanyMapAccountInDB).where(*options)
        return self.session.execute(stmt).scalars().all()
