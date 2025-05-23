#!/usr/bin/env python3
# filepath: /Volumes/Storage/workspace/project/hr-demo/api/commands/update_employee_schemas.py
"""
更新员工记录的命令

此命令用于为没有 extra_schema_id 的员工记录添加默认的模板ID
"""

import click
from sqlalchemy import select, update
from app import db
from libs.models import EmployeeInDB, JsonSchemaInDB
from libs.models.json_schema import SchemaEntityType


@click.command()
@click.option(
    "--company-id", type=int, help="需要更新的公司ID。如果不提供，将更新所有公司"
)
@click.option("--dry-run", is_flag=True, help="仅显示将要更新的记录数，不实际更新")
@click.option("--force", is_flag=True, help="强制更新已有 extra_schema_id 的记录")
def update_employee_schemas(company_id, dry_run, force):
    """为没有 extra_schema_id 的员工记录添加默认的模板ID"""
    click.echo("正在查询需要更新的员工记录...")

    # 获取所有的员工模板(按公司分组)
    schema_query = select(JsonSchemaInDB).where(
        JsonSchemaInDB.entity_type == SchemaEntityType.EMPLOYEE
    )

    if company_id:
        schema_query = schema_query.where(JsonSchemaInDB.company_id == company_id)

    schemas = db.session.execute(schema_query).scalars().all()

    # 按公司ID分组
    schema_by_company = {}
    for schema in schemas:
        company = schema.company_id
        if company not in schema_by_company:
            schema_by_company[company] = []
        schema_by_company[company].append(schema)

    # 查询每个公司需要更新的员工数量
    total_to_update = 0
    updates_by_company = {}

    for company_id, company_schemas in schema_by_company.items():
        if not company_schemas:
            click.echo(f"公司 ID {company_id} 没有可用的员工模板，跳过")
            continue

        # 使用第一个模板作为默认模板
        default_schema = company_schemas[0]

        # 查询需要更新的员工
        employee_query = select(EmployeeInDB).where(
            EmployeeInDB.company_id == company_id
        )

        if not force:
            employee_query = employee_query.where(EmployeeInDB.extra_schema_id == None)

        employees = db.session.execute(employee_query).scalars().all()

        updates_by_company[company_id] = {
            "schema_id": default_schema.id,
            "employees": employees,
        }
        total_to_update += len(employees)

    # 显示更新概要
    click.echo(f"总共找到 {total_to_update} 条员工记录需要更新")
    for company_id, data in updates_by_company.items():
        click.echo(
            f"公司 ID {company_id}: {len(data['employees'])} 条记录将使用模板 ID {data['schema_id']}"
        )

    if dry_run:
        click.echo("这是一次预演，没有实际更新任何数据")
        return

    # 确认是否继续
    if not click.confirm("是否继续更新?"):
        click.echo("操作已取消")
        return

    # 执行更新
    for company_id, data in updates_by_company.items():
        schema_id = data["schema_id"]
        employees = data["employees"]

        if not employees:
            continue

        employee_ids = [e.id for e in employees]

        # 批量更新
        update_stmt = (
            update(EmployeeInDB)
            .where(EmployeeInDB.id.in_(employee_ids))
            .values(extra_schema_id=schema_id)
        )

        db.session.execute(update_stmt)

        click.echo(f"已更新公司 ID {company_id} 的 {len(employees)} 条员工记录")

    # 提交事务
    db.session.commit()
    click.echo("所有更新已完成")


if __name__ == "__main__":
    update_employee_schemas()
