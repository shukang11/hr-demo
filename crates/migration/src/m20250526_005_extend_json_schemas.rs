use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 扩展 json_schemas 表，分别添加新增字段（SQLite不支持一次添加多个列）
        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .add_column(
                        ColumnDef::new(JsonSchemas::EntityType)
                            .string_len(50)
                            .not_null()
                            .default("GENERAL".to_string())
                            .comment("Schema适用的实体类型".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .add_column(
                        ColumnDef::new(JsonSchemas::IsSystem)
                            .boolean()
                            .not_null()
                            .default(false)
                            .comment("是否为系统预设Schema".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .add_column(
                        ColumnDef::new(JsonSchemas::Version)
                            .integer()
                            .not_null()
                            .default(1)
                            .comment("Schema版本号".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .add_column(
                        ColumnDef::new(JsonSchemas::ParentSchemaId)
                            .integer()
                            .null()
                            .comment("父Schema ID，用于版本管理".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .add_column(
                        ColumnDef::new(JsonSchemas::UiSchema)
                            .json()
                            .null()
                            .comment("UI展示相关的配置".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .add_column(
                        ColumnDef::new(JsonSchemas::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .to_owned(),
            )
            .await?;

        // 注意：SQLite 不支持在已存在的表上添加外键约束
        // 如果需要外键约束，应该在创建表时定义
        // 这里我们跳过外键约束的创建

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 由于我们没有创建外键约束，所以这里也不需要删除

        // 分别删除添加的列（SQLite不支持一次删除多个列）
        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .drop_column(JsonSchemas::UpdatedAt)
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .drop_column(JsonSchemas::UiSchema)
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .drop_column(JsonSchemas::ParentSchemaId)
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .drop_column(JsonSchemas::Version)
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .drop_column(JsonSchemas::IsSystem)
                    .to_owned(),
            )
            .await?;

        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .drop_column(JsonSchemas::EntityType)
                    .to_owned(),
            )
            .await?;

        Ok(())
    }
}

#[derive(Iden)]
enum JsonSchemas {
    Table,
    Id,
    EntityType,
    IsSystem,
    Version,
    ParentSchemaId,
    UiSchema,
    UpdatedAt,
}
