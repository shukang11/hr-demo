use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 创建 json_schemas 表
        manager
            .create_table(
                Table::create()
                    .table(JsonSchemas::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(JsonSchemas::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonSchemas::Name)
                            .string_len(255)
                            .not_null()
                            .comment("schema名称".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonSchemas::Schema)
                            .json()
                            .not_null()
                            .comment("JSON Schema".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonSchemas::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        // 创建 company 表
        manager
            .create_table(
                Table::create()
                    .table(Company::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Company::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(Company::Name)
                            .string_len(255)
                            .not_null()
                            .comment("公司名称".to_string()),
                    )
                    .col(
                        ColumnDef::new(Company::ExtraValue)
                            .json()
                            .null()
                            .comment("额外JSON数据".to_string()),
                    )
                    .col(
                        ColumnDef::new(Company::ExtraSchemaId)
                            .integer()
                            .null()
                            .comment("额外数据schema ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Company::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(Company::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        // 创建 department 表
        manager
            .create_table(
                Table::create()
                    .table(Department::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Department::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(Department::ParentId)
                            .integer()
                            .null()
                            .comment("父部门ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Department::CompanyId)
                            .integer()
                            .not_null()
                            .comment("公司ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Department::Name)
                            .string_len(64)
                            .not_null()
                            .comment("部门名称".to_string()),
                    )
                    .col(
                        ColumnDef::new(Department::LeaderId)
                            .integer()
                            .null()
                            .comment("部门负责人ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Department::Remark)
                            .string_len(255)
                            .null()
                            .comment("备注".to_string()),
                    )
                    .col(
                        ColumnDef::new(Department::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(Department::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-department-company_id")
                            .from(Department::Table, Department::CompanyId)
                            .to(Company::Table, Company::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-department-parent_id")
                            .from(Department::Table, Department::ParentId)
                            .to(Department::Table, Department::Id)
                            .on_delete(ForeignKeyAction::SetNull)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        // 创建 position 表
        manager
            .create_table(
                Table::create()
                    .table(Position::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Position::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(Position::Name)
                            .string_len(64)
                            .not_null()
                            .comment("职位名称".to_string()),
                    )
                    .col(
                        ColumnDef::new(Position::CompanyId)
                            .integer()
                            .not_null()
                            .comment("公司ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Position::Remark)
                            .string_len(255)
                            .null()
                            .comment("备注".to_string()),
                    )
                    .col(
                        ColumnDef::new(Position::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(Position::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-position-company_id")
                            .from(Position::Table, Position::CompanyId)
                            .to(Company::Table, Company::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        // 创建 employee 表
        manager
            .create_table(
                Table::create()
                    .table(Employee::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Employee::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::CompanyId)
                            .integer()
                            .not_null()
                            .comment("公司ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::Name)
                            .string_len(255)
                            .not_null()
                            .comment("姓名".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::Email)
                            .string_len(255)
                            .null()
                            .comment("邮箱".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::Phone)
                            .string_len(20)
                            .null()
                            .comment("电话".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::Birthdate)
                            .date()
                            .null()
                            .comment("出生日期".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::Address)
                            .string_len(255)
                            .null()
                            .comment("地址".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::Gender)
                            .string_len(16)
                            .not_null()
                            .comment("性别".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::ExtraValue)
                            .json()
                            .null()
                            .comment("额外JSON数据".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::ExtraSchemaId)
                            .integer()
                            .null()
                            .comment("额外数据schema ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(Employee::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-employee-company_id")
                            .from(Employee::Table, Employee::CompanyId)
                            .to(Company::Table, Company::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        // 创建 employee_position 表
        manager
            .create_table(
                Table::create()
                    .table(EmployeePosition::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(EmployeePosition::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(EmployeePosition::EmployeeId)
                            .integer()
                            .not_null()
                            .comment("员工ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(EmployeePosition::CompanyId)
                            .integer()
                            .not_null()
                            .comment("公司ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(EmployeePosition::DepartmentId)
                            .integer()
                            .not_null()
                            .comment("部门ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(EmployeePosition::PositionId)
                            .integer()
                            .not_null()
                            .comment("职位ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(EmployeePosition::Remark)
                            .string_len(255)
                            .null()
                            .comment("备注".to_string()),
                    )
                    .col(
                        ColumnDef::new(EmployeePosition::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(EmployeePosition::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-employee_position-employee_id")
                            .from(EmployeePosition::Table, EmployeePosition::EmployeeId)
                            .to(Employee::Table, Employee::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-employee_position-company_id")
                            .from(EmployeePosition::Table, EmployeePosition::CompanyId)
                            .to(Company::Table, Company::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-employee_position-department_id")
                            .from(EmployeePosition::Table, EmployeePosition::DepartmentId)
                            .to(Department::Table, Department::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-employee_position-position_id")
                            .from(EmployeePosition::Table, EmployeePosition::PositionId)
                            .to(Position::Table, Position::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 按照依赖关系反向删除表
        manager
            .drop_table(Table::drop().table(EmployeePosition::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(Employee::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(Position::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(Department::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(Company::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(JsonSchemas::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(Iden)]
enum JsonSchemas {
    Table,
    Id,
    Name,
    Schema,
    CreatedAt,
}

#[derive(Iden)]
enum Company {
    Table,
    Id,
    Name,
    ExtraValue,
    ExtraSchemaId,
    CreatedAt,
    UpdatedAt,
}

#[derive(Iden)]
enum Department {
    Table,
    Id,
    ParentId,
    CompanyId,
    Name,
    LeaderId,
    Remark,
    CreatedAt,
    UpdatedAt,
}

#[derive(Iden)]
enum Position {
    Table,
    Id,
    Name,
    CompanyId,
    Remark,
    CreatedAt,
    UpdatedAt,
}

#[derive(Iden)]
enum Employee {
    Table,
    Id,
    CompanyId,
    Name,
    Email,
    Phone,
    Birthdate,
    Address,
    Gender,
    ExtraValue,
    ExtraSchemaId,
    CreatedAt,
    UpdatedAt,
}

#[derive(Iden)]
enum EmployeePosition {
    Table,
    Id,
    EmployeeId,
    CompanyId,
    DepartmentId,
    PositionId,
    Remark,
    CreatedAt,
    UpdatedAt,
}
