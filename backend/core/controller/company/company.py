from sqlalchemy import select

from core.controller._base import BaseController
from core.database import CompanyInDB, DepartmentInDB, CompanyJobInDB

from .schema import (
    InsertCompanyJobPayload,
    InsertCompanyPayload,
    InsertDepartmentPayload,
)


# 以公司为主体或者操作对象为公司级别的控制器
class CompanyManager(BaseController):
    def insert_company(self, paylod: InsertCompanyPayload) -> CompanyInDB:
        # 首先确定公司是否存在，如果存在就不创建
        stmt = select(CompanyInDB).where(
            CompanyInDB.name == paylod.name, CompanyInDB.admin_id == paylod.admin_id
        )
        is_exist = self.session.scalar(stmt)
        if is_exist:
            return is_exist

        # 创建公司
        company = CompanyInDB(
            name=paylod.name,
            description=paylod.description,
            admin_id=paylod.admin_id,
        )
        self.session.add(company)
        self.session.flush([company])
        return company

    def insert_department(self, payload: InsertDepartmentPayload) -> DepartmentInDB:
        insert_department: DepartmentInDB
        if payload.id:
            # 更新
            stmt = select(DepartmentInDB).where(DepartmentInDB.id == payload.id)
            insert_department = self.session.scalar(stmt)
            if not insert_department:
                raise ValueError("部门不存在")
            if payload.name:
                insert_department.name = payload.name
            if payload.parent_id:
                insert_department.parent_id = payload.parent_id
            if payload.leader_id:
                insert_department.leader_id = payload.leader_id

        elif payload.name:
            # 创建
            # 首先确定部门是否存在，如果存在就不创建
            stmt = select(DepartmentInDB).where(
                DepartmentInDB.name == payload.name,
                DepartmentInDB.company_id == payload.company_id,
            )
            is_exist = self.session.scalar(stmt)
            if not is_exist:
                insert_department = DepartmentInDB(
                    name=payload.name,
                    parent_id=payload.parent_id,
                    company_id=payload.company_id,
                    leader_id=payload.leader_id,
                )

        self.session.add(insert_department)
        self.session.flush([insert_department])
        # 创建部门
        return insert_department

    def insert_company_job(self, payload: InsertCompanyJobPayload) -> CompanyJobInDB:
        insert_job: CompanyJobInDB
        if payload.id:
            # 更新
            stmt = select(CompanyJobInDB).where(CompanyJobInDB.id == payload.id)
            insert_job = self.session.scalar(stmt)
            if not insert_job:
                raise ValueError("职位不存在")
            if payload.job_name:
                insert_job.job_name = payload.job_name
        elif payload.job_name:
            # 创建
            # 首先确定职位是否存在，如果存在就不创建
            stmt = select(CompanyJobInDB).where(
                CompanyJobInDB.job_name == payload.job_name,
                CompanyJobInDB.company_id == payload.company_id,
            )
            is_exist = self.session.scalar(stmt)
            if not is_exist:
                insert_job = CompanyJobInDB(
                    job_name=payload.job_name,
                    company_id=payload.company_id,
                )
        self.session.add(insert_job)
        return insert_job
