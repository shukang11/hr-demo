use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 创建 account_tokens 表
        manager
            .create_table(
                Table::create()
                    .table(AccountTokens::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(AccountTokens::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(AccountTokens::AccountId)
                            .integer()
                            .not_null()
                            .comment("关联的账户ID (accounts.id)，唯一".to_string()),
                    )
                    .col(
                        ColumnDef::new(AccountTokens::Token)
                            .string_len(255)
                            .not_null()
                            .unique_key()
                            .comment("API 访问令牌字符串，唯一".to_string()),
                    )
                    .col(
                        ColumnDef::new(AccountTokens::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(AccountTokens::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-account_tokens-account_id")
                            .from(AccountTokens::Table, AccountTokens::AccountId)
                            .to(Accounts::Table, Accounts::Id)
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
                    .name("uk_account_tokens_account_id")
                    .table(AccountTokens::Table)
                    .col(AccountTokens::AccountId)
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
                    .table(AccountTokens::Table)
                    .name("uk_account_tokens_account_id")
                    .to_owned(),
            )
            .await?;

        // 删除 account_tokens 表
        manager
            .drop_table(Table::drop().table(AccountTokens::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(Iden)]
pub enum AccountTokens {
    Table,
    Id,
    AccountId,
    Token,
    CreatedAt,
    UpdatedAt,
}

#[derive(Iden)]
pub enum Accounts {
    Table,
    Id,
}
