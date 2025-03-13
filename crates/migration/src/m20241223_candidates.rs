use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 创建 candidates 表
        manager
            .create_table(
                Table::create()
                    .table(Candidates::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Candidates::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::CompanyId)
                            .integer()
                            .not_null()
                            .comment("公司ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::Name)
                            .string_len(64)
                            .not_null()
                            .comment("候选人姓名".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::Phone)
                            .string_len(20)
                            .null()
                            .comment("联系电话".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::Email)
                            .string_len(255)
                            .null()
                            .comment("电子邮箱".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::PositionId)
                            .integer()
                            .null()
                            .comment("应聘职位ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::DepartmentId)
                            .integer()
                            .null()
                            .comment("目标部门ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::InterviewDate)
                            .date_time()
                            .null()
                            .comment("面试日期".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::Status)
                            .string_len(20)
                            .null()
                            .comment("状态".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::InterviewerId)
                            .integer()
                            .null()
                            .comment("面试官ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::Evaluation)
                            .text()
                            .null()
                            .comment("面试评价".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::Remark)
                            .string_len(255)
                            .null()
                            .comment("备注".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::ExtraValue)
                            .json()
                            .null()
                            .comment("额外JSON数据".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::ExtraSchemaId)
                            .integer()
                            .null()
                            .comment("额外数据schema ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(Candidates::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-candidates-company_id")
                            .from(Candidates::Table, Candidates::CompanyId)
                            .to(Company::Table, Company::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-candidates-position_id")
                            .from(Candidates::Table, Candidates::PositionId)
                            .to(Position::Table, Position::Id)
                            .on_delete(ForeignKeyAction::Restrict)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-candidates-department_id")
                            .from(Candidates::Table, Candidates::DepartmentId)
                            .to(Department::Table, Department::Id)
                            .on_delete(ForeignKeyAction::Restrict)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-candidates-interviewer_id")
                            .from(Candidates::Table, Candidates::InterviewerId)
                            .to(Employee::Table, Employee::Id)
                            .on_delete(ForeignKeyAction::Restrict)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-candidates-extra_schema_id")
                            .from(Candidates::Table, Candidates::ExtraSchemaId)
                            .to(JsonSchemas::Table, JsonSchemas::Id)
                            .on_delete(ForeignKeyAction::SetNull)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 删除 candidates 表
        manager
            .drop_table(Table::drop().table(Candidates::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(Iden)]
pub enum JsonSchemas {
    Table,
    Id,
}

#[derive(Iden)]
pub enum Company {
    Table,
    Id,
}

#[derive(Iden)]
pub enum Position {
    Table,
    Id,
}

#[derive(Iden)]
pub enum Department {
    Table,
    Id,
}

#[derive(Iden)]
pub enum Employee {
    Table,
    Id,
}

#[derive(Iden)]
pub enum Candidates {
    Table,
    Id,
    CompanyId,
    Name,
    Phone,
    Email,
    PositionId,
    DepartmentId,
    InterviewDate,
    Status,
    InterviewerId,
    Evaluation,
    Remark,
    ExtraValue,
    ExtraSchemaId,
    CreatedAt,
    UpdatedAt,
}
