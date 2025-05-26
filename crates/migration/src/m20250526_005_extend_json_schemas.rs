use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 扩展 json_schemas 表，添加新增字段
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
                    .add_column(
                        ColumnDef::new(JsonSchemas::IsSystem)
                            .boolean()
                            .not_null()
                            .default(false)
                            .comment("是否为系统预设Schema".to_string()),
                    )
                    .add_column(
                        ColumnDef::new(JsonSchemas::Version)
                            .integer()
                            .not_null()
                            .default(1)
                            .comment("Schema版本号".to_string()),
                    )
                    .add_column(
                        ColumnDef::new(JsonSchemas::ParentSchemaId)
                            .integer()
                            .null()
                            .comment("父Schema ID，用于版本管理".to_string()),
                    )
                    .add_column(
                        ColumnDef::new(JsonSchemas::UiSchema)
                            .json()
                            .null()
                            .comment("UI展示相关的配置".to_string()),
                    )
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

        // 添加外键约束
        manager
            .create_foreign_key(
                ForeignKey::create()
                    .name("fk-json_schemas-parent_schema_id")
                    .from(JsonSchemas::Table, JsonSchemas::ParentSchemaId)
                    .to(JsonSchemas::Table, JsonSchemas::Id)
                    .on_delete(ForeignKeyAction::SetNull)
                    .on_update(ForeignKeyAction::Cascade)
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 首先删除外键约束
        manager
            .drop_foreign_key(
                ForeignKey::drop()
                    .name("fk-json_schemas-parent_schema_id")
                    .table(JsonSchemas::Table)
                    .to_owned(),
            )
            .await?;

        // 删除添加的列
        manager
            .alter_table(
                Table::alter()
                    .table(JsonSchemas::Table)
                    .drop_column(JsonSchemas::EntityType)
                    .drop_column(JsonSchemas::IsSystem)
                    .drop_column(JsonSchemas::Version)
                    .drop_column(JsonSchemas::ParentSchemaId)
                    .drop_column(JsonSchemas::UiSchema)
                    .drop_column(JsonSchemas::UpdatedAt)
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
