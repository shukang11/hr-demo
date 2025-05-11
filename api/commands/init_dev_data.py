from typing import TYPE_CHECKING

import click
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

if TYPE_CHECKING:
    from flask import Flask
    from libs.models import (
        AccountInDB,
        CompanyInDB,
        DepartmentInDB,
        PositionInDB,
        EmployeeInDB,
        AccountCompanyInDB,
    )


@click.command("init-dev-data", help="Initialize development data")
def command():
    """初始化开发环境数据，包括管理员、公司、部门、职位、员工和候选人"""
    click.echo("正在初始化开发环境数据...")
    try:
        from extensions.ext_database import db
        from libs.helper import get_sha256
        from services.account import AccountService
        from services.account._schema import AccountCreate
        from services.company import CompanyService, CompanyCreate
        from services.position import PositionService, PositionCreate
        from services.candidate import (
            CandidateService,
            CandidateCreate,
            CandidateStatus,
        )
        from libs.models import (
            AccountInDB,
            CompanyInDB,
            DepartmentInDB,
            PositionInDB,
            EmployeeInDB,
            AccountCompanyRole,
        )

        session: Session = db.session

        # 1. 创建管理员账户
        click.echo("创建管理员账户...")
        admin_account = create_admin_account(session)

        # 2. 创建示例公司
        click.echo("创建示例公司...")
        companies = create_sample_companies(session, admin_account)

        # 3. 创建部门和职位
        click.echo("创建部门和职位...")
        for company in companies:
            create_departments_and_positions(session, admin_account, company)

        # 4. 创建员工
        click.echo("创建员工...")
        for company in companies:
            create_employees(session, company)

        # 5. 创建候选人
        click.echo("创建候选人...")
        for company in companies:
            create_candidates(session, admin_account, company)

        # 提交所有更改
        session.commit()
        click.echo(click.style("开发数据初始化成功!", fg="green"))

    except Exception as e:
        click.echo(click.style(f"初始化开发数据失败: {e}", fg="red"))
        import traceback

        click.echo(traceback.format_exc())


def create_admin_account(session: Session) -> "AccountInDB":
    """创建管理员账户"""
    from libs.models import AccountInDB
    from libs.helper import get_sha256

    # 检查管理员是否已存在
    admin = session.query(AccountInDB).filter_by(username="admin").first()
    if admin:
        click.echo("管理员账户已存在，跳过创建")
        return admin

    # 创建管理员账户
    admin = AccountInDB(
        username="admin",
        email="admin@example.com",
        password=get_sha256("admin123"),  # 密码: admin123
        phone="13800138000",
        is_active=True,
        last_login_at=datetime.now(),
    )
    session.add(admin)
    session.flush()  # 获取生成的ID

    click.echo(f"创建管理员账户成功: id={admin.id}, username={admin.username}")
    return admin


def create_sample_companies(
    session: Session, admin_account: "AccountInDB"
) -> list["CompanyInDB"]:
    """创建示例公司和子公司"""
    from libs.models import CompanyInDB, AccountCompanyInDB, AccountCompanyRole

    companies = []

    # 主公司数据 [公司名称, 描述]
    parent_companies_data = [
        ["未来科技有限公司", "一家专注于科技创新的企业集团"],
        ["环球餐饮集团", "一家全球连锁的餐饮企业"],
        ["智慧教育联盟", "一家致力于教育创新的机构"],
    ]

    # 子公司数据 [父公司索引, 子公司名称, 描述]
    subsidiary_companies_data = [
        # 未来科技的子公司
        [0, "未来科技北京分公司", "负责华北地区业务"],
        [0, "未来科技上海分公司", "负责华东地区业务"],
        [0, "未来科技研发中心", "专注于技术研发"],
        # 环球餐饮的子公司
        [1, "环球餐饮A店", "位于市中心的主力门店"],
        [1, "环球餐饮B店", "位于商业区的旗舰店"],
        [1, "环球餐饮C店", "位于郊区的体验店"],
        # 智慧教育的子公司
        [2, "智慧教育培训中心", "专注于青少年教育培训"],
        [2, "智慧教育研究院", "专注于教育理论研究"],
    ]

    # 1. 创建主公司
    parent_companies = []
    for idx, (name, description) in enumerate(parent_companies_data):
        # 检查公司是否已存在
        existing = session.query(CompanyInDB).filter_by(name=name).first()
        if existing:
            click.echo(f"主公司 '{name}' 已存在，跳过创建")
            parent_companies.append(existing)
            companies.append(existing)
            continue

        # 创建新主公司
        company = CompanyInDB(
            name=name,
            description=description,
            parent_id=None,  # 主公司没有父公司
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(company)
        session.flush()  # 获取生成的ID

        # 创建管理员与公司的关系
        relation = AccountCompanyInDB(
            account_id=admin_account.id,
            company_id=company.id,
            role=AccountCompanyRole.OWNER,
        )
        session.add(relation)

        parent_companies.append(company)
        companies.append(company)
        click.echo(f"创建主公司成功: id={company.id}, name={company.name}")

    # 2. 创建子公司
    for parent_idx, name, description in subsidiary_companies_data:
        if parent_idx >= len(parent_companies):
            click.echo(f"父公司索引 {parent_idx} 超出范围，跳过创建子公司 '{name}'")
            continue

        parent_company = parent_companies[parent_idx]

        # 检查子公司是否已存在
        existing = session.query(CompanyInDB).filter_by(name=name).first()
        if existing:
            click.echo(f"子公司 '{name}' 已存在，跳过创建")
            companies.append(existing)
            continue

        # 创建新子公司
        subsidiary = CompanyInDB(
            name=name,
            description=description,
            parent_id=parent_company.id,  # 设置父公司ID
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(subsidiary)
        session.flush()  # 获取生成的ID

        # 创建管理员与子公司的关系
        relation = AccountCompanyInDB(
            account_id=admin_account.id,
            company_id=subsidiary.id,
            role=AccountCompanyRole.OWNER,
        )
        session.add(relation)

        companies.append(subsidiary)
        click.echo(
            f"创建子公司成功: id={subsidiary.id}, name={subsidiary.name}, 父公司={parent_company.name}"
        )

    return companies


def create_departments_and_positions(
    session: Session, admin_account: "AccountInDB", company: "CompanyInDB"
):
    """为公司创建部门和职位"""
    from libs.models import DepartmentInDB, PositionInDB

    # 部门信息
    departments_info = [
        {"name": "人力资源部", "parent_id": None},
        {"name": "技术部", "parent_id": None},
        {"name": "市场部", "parent_id": None},
        {"name": "财务部", "parent_id": None},
        {"name": "行政部", "parent_id": None},
    ]

    # 创建部门
    departments = []
    for dept_info in departments_info:
        dept = DepartmentInDB(
            name=dept_info["name"],
            company_id=company.id,
            parent_id=dept_info["parent_id"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(dept)
        session.flush()
        departments.append(dept)
        click.echo(f"创建部门成功: 公司={company.name}, 部门={dept.name}")

    # 职位信息 (部门ID索引, 职位名称)
    positions_info = [
        (0, "HR经理"),
        (0, "招聘专员"),
        (1, "技术总监"),
        (1, "高级开发工程师"),
        (1, "初级开发工程师"),
        (1, "产品经理"),
        (2, "市场总监"),
        (2, "营销经理"),
        (3, "财务总监"),
        (3, "会计"),
        (4, "行政主管"),
        (4, "前台"),
    ]

    # 创建职位
    positions = []
    for dept_idx, position_name in positions_info:
        if dept_idx < len(departments):
            position = PositionInDB(
                name=position_name,
                company_id=company.id,
                remark=f"此职位属于{departments[dept_idx].name}",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            session.add(position)
            session.flush()
            positions.append((departments[dept_idx], position))
            click.echo(
                f"创建职位成功: 公司={company.name}, 部门={departments[dept_idx].name}, 职位={position.name}"
            )

    return departments, positions


def create_employees(session: Session, company: "CompanyInDB"):
    """为公司创建员工"""
    from libs.models import (
        EmployeeInDB,
        DepartmentInDB,
        PositionInDB,
        EmployeePositionInDB,
    )

    # 获取公司的所有部门
    departments = session.query(DepartmentInDB).filter_by(company_id=company.id).all()

    # 获取公司的所有职位
    positions = session.query(PositionInDB).filter_by(company_id=company.id).all()

    # 姓氏列表
    surnames = ["张", "王", "李", "赵", "陈", "刘", "杨", "黄", "周", "吴", "郑", "孙"]

    # 名字列表
    names = [
        "伟",
        "芳",
        "娜",
        "秀英",
        "敏",
        "静",
        "强",
        "磊",
        "洋",
        "艳",
        "勇",
        "杰",
        "娟",
        "涛",
        "明",
        "超",
    ]

    # 随机生成5-15名员工
    num_employees = random.randint(5, 15)

    for i in range(num_employees):
        # 随机生成姓名
        full_name = random.choice(surnames) + random.choice(names)

        # 随机选择出生日期 (20-50岁)
        age = random.randint(20, 50)
        birthdate = datetime.now() - timedelta(days=age * 365)

        # 根据gender字段定义修改性别值为整数
        gender_value = random.randint(1, 2)  # 1-男, 2-女

        # 创建员工基本信息 - 添加company_id字段
        employee = EmployeeInDB(
            name=full_name,
            company_id=company.id,  # 添加company_id字段
            email=f"{full_name}{i + 1}@example.com",
            phone=f"138{random.randint(10000000, 99999999)}",
            birthdate=birthdate,
            address="中国某省某市某区某街道",
            gender=gender_value,  # 使用整数值
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(employee)
        session.flush()

        # 随机选择部门和职位
        if departments and positions:
            dept = random.choice(departments)
            position = random.choice(positions)

            # 创建员工-职位关系
            emp_position = EmployeePositionInDB(
                employee_id=employee.id,
                company_id=company.id,
                department_id=dept.id,
                position_id=position.id,
                start_date=datetime.now().date()
                - timedelta(days=random.randint(30, 365 * 3)),  # 1个月到3年前入职
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            session.add(emp_position)

            click.echo(
                f"创建员工成功: 公司={company.name}, 员工={employee.name}, 部门={dept.name}, 职位={position.name}"
            )
        else:
            click.echo(f"创建员工成功: 公司={company.name}, 员工={employee.name}")

    return


def create_candidates(
    session: Session, admin_account: "AccountInDB", company: "CompanyInDB"
):
    """为公司创建候选人"""
    from libs.models import CandidateInDB, PositionInDB, DepartmentInDB, CandidateStatus

    # 获取公司的所有部门
    departments = session.query(DepartmentInDB).filter_by(company_id=company.id).all()

    # 获取公司的所有职位
    positions = session.query(PositionInDB).filter_by(company_id=company.id).all()

    if not departments or not positions:
        click.echo(f"公司 {company.name} 没有部门或职位，跳过候选人创建")
        return

    # 姓氏列表
    surnames = ["张", "王", "李", "赵", "陈", "刘", "杨", "黄", "周", "吴", "郑", "孙"]

    # 名字列表
    names = [
        "伟",
        "芳",
        "娜",
        "秀英",
        "敏",
        "静",
        "强",
        "磊",
        "洋",
        "艳",
        "勇",
        "杰",
        "娟",
        "涛",
        "明",
        "超",
    ]

    # 候选人状态
    statuses = list(CandidateStatus)

    # 随机生成3-10名候选人
    num_candidates = random.randint(3, 10)

    for i in range(num_candidates):
        # 随机生成姓名
        full_name = random.choice(surnames) + random.choice(names)

        # 随机选择部门和职位
        dept = random.choice(departments)
        position = random.choice(positions)

        # 随机选择状态
        status = random.choice(statuses)

        # 随机选择面试日期
        interview_date = datetime.now() + timedelta(days=random.randint(-30, 30))

        candidate = CandidateInDB(
            name=full_name,
            company_id=company.id,
            phone=f"138{random.randint(10000000, 99999999)}",
            email=f"{full_name}{i + 100}@example.com",
            position_id=position.id,
            department_id=dept.id,
            interview_date=interview_date,
            status=status,
            remark=f"候选人应聘{position.name}职位，安排在{interview_date.strftime('%Y-%m-%d')}面试",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(candidate)

        click.echo(
            f"创建候选人成功: 公司={company.name}, 候选人={candidate.name}, 部门={dept.name}, 职位={position.name}, 状态={status}"
        )

    return
