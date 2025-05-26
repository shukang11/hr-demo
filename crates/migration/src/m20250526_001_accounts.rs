use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 创建 accounts 表
        manager
            .create_table(
                Table::create()
                    .table(Accounts::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Accounts::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(Accounts::Username)
                            .string_len(64)
                            .not_null()
                            .unique_key()
                            .comment("用户名，唯一".to_string()),
                    )
                    .col(
                        ColumnDef::new(Accounts::Email)
                            .string_len(255)
                            .not_null()
                            .unique_key()
                            .comment("电子邮箱，唯一".to_string()),
                    )
                    .col(
                        ColumnDef::new(Accounts::Phone)
                            .string_len(20)
                            .null()
                            .comment("手机号码".to_string()),
                    )
                    .col(
                        ColumnDef::new(Accounts::Gender)
                            .small_integer()
                            .null()
                            .comment("性别，0-未知，1-男，2-女".to_string()),
                    )
                    .col(
                        ColumnDef::new(Accounts::PasswordHashed)
                            .string_len(255)
                            .not_null()
                            .comment("密码哈希值".to_string()),
                    )
                    .col(
                        ColumnDef::new(Accounts::IsActive)
                            .boolean()
                            .not_null()
                            .comment("账户是否激活 (True: 激活, False: 禁用)".to_string()),
                    )
                    .col(
                        ColumnDef::new(Accounts::LastLoginAt)
                            .date_time()
                            .null()
                            .comment("最后登录时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(Accounts::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(Accounts::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 删除 accounts 表
        manager
            .drop_table(Table::drop().table(Accounts::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(Iden)]
pub enum Accounts {
    Table,
    Id,
    Username,
    Email,
    Phone,
    Gender,
    PasswordHashed,
    IsActive,
    LastLoginAt,
    CreatedAt,
    UpdatedAt,
}
