use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 创建 account_company 表
        manager
            .create_table(
                Table::create()
                    .table(AccountCompany::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(AccountCompany::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(AccountCompany::AccountId)
                            .integer()
                            .not_null()
                            .comment("账户ID，关联 accounts.id".to_string()),
                    )
                    .col(
                        ColumnDef::new(AccountCompany::CompanyId)
                            .integer()
                            .not_null()
                            .comment("公司ID，关联 company.id".to_string()),
                    )
                    .col(
                        ColumnDef::new(AccountCompany::Role)
                            .string_len(32)
                            .not_null()
                            .comment("账户在该公司中的角色 (owner, admin, user)".to_string()),
                    )
                    .col(
                        ColumnDef::new(AccountCompany::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(AccountCompany::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-account_company-account_id")
                            .from(AccountCompany::Table, AccountCompany::AccountId)
                            .to(Accounts::Table, Accounts::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-account_company-company_id")
                            .from(AccountCompany::Table, AccountCompany::CompanyId)
                            .to(Company::Table, Company::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        // 创建唯一约束
        manager
            .create_index(
                Index::create()
                    .unique()
                    .name("uk_account_company")
                    .table(AccountCompany::Table)
                    .col(AccountCompany::AccountId)
                    .col(AccountCompany::CompanyId)
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 删除唯一约束索引
        manager
            .drop_index(
                Index::drop()
                    .table(AccountCompany::Table)
                    .name("uk_account_company")
                    .to_owned(),
            )
            .await?;

        // 删除 account_company 表
        manager
            .drop_table(Table::drop().table(AccountCompany::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(Iden)]
pub enum AccountCompany {
    Table,
    Id,
    AccountId,
    CompanyId,
    Role,
    CreatedAt,
    UpdatedAt,
}

#[derive(Iden)]
pub enum Accounts {
    Table,
    Id,
}

#[derive(Iden)]
pub enum Company {
    Table,
    Id,
}
