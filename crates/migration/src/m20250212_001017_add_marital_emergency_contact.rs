use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 分别添加两个列，因为SQLite不支持在一个ALTER语句中添加多个列
        manager
            .alter_table(
                Table::alter()
                    .table(Employee::Table)
                    .add_column_if_not_exists(
                        ColumnDef::new(Employee::MaritalStatus)
                            .string_len(10)
                            .null()
                            .comment("婚姻状况".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(Employee::Table)
                    .add_column_if_not_exists(
                        ColumnDef::new(Employee::EmergencyContact)
                            .string_len(255)
                            .null()
                            .comment("紧急联系人".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Replace the sample below with your own migration scripts

        manager
            .alter_table(
                Table::alter()
                    .table(Employee::Table)
                    .drop_column(Employee::MaritalStatus)
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(Employee::Table)
                    .drop_column(Employee::EmergencyContact)
                    .to_owned(),
            )
            .await?;

        Ok(())
    }
}

#[derive(Iden)]
pub enum Employee {
    Table,
    MaritalStatus,
    EmergencyContact,
}
