use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 创建 json_values 表
        manager
            .create_table(
                Table::create()
                    .table(JsonValues::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(JsonValues::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key()
                            .comment("主键".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonValues::Value)
                            .json()
                            .not_null()
                            .comment("JSON值".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonValues::SchemaId)
                            .integer()
                            .not_null()
                            .comment("关联的JSON Schema ID".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonValues::EntityId)
                            .integer()
                            .not_null()
                            .comment("关联的实体ID，如员工ID、候选人ID等".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonValues::EntityType)
                            .string_len(50)
                            .not_null()
                            .comment("关联的实体类型，如'employee'、'candidate'等".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonValues::Remark)
                            .string_len(255)
                            .null()
                            .comment("备注信息".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonValues::CreatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("创建时间".to_string()),
                    )
                    .col(
                        ColumnDef::new(JsonValues::UpdatedAt)
                            .date_time()
                            .not_null()
                            .default(Expr::current_timestamp())
                            .comment("更新时间".to_string()),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-json_values-schema_id")
                            .from(JsonValues::Table, JsonValues::SchemaId)
                            .to(JsonSchemas::Table, JsonSchemas::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        // 创建索引
        manager
            .create_index(
                Index::create()
                    .name("ix_json_value_entity")
                    .table(JsonValues::Table)
                    .col(JsonValues::EntityType)
                    .col(JsonValues::EntityId)
                    .to_owned(),
            )
            .await?;

        manager
            .create_index(
                Index::create()
                    .name("ix_json_value_schema")
                    .table(JsonValues::Table)
                    .col(JsonValues::SchemaId)
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // 先删除索引
        manager
            .drop_index(
                Index::drop()
                    .table(JsonValues::Table)
                    .name("ix_json_value_entity")
                    .to_owned(),
            )
            .await?;

        manager
            .drop_index(
                Index::drop()
                    .table(JsonValues::Table)
                    .name("ix_json_value_schema")
                    .to_owned(),
            )
            .await?;

        // 删除 json_values 表
        manager
            .drop_table(Table::drop().table(JsonValues::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(Iden)]
pub enum JsonValues {
    Table,
    Id,
    Value,
    SchemaId,
    EntityId,
    EntityType,
    Remark,
    CreatedAt,
    UpdatedAt,
}

#[derive(Iden)]
pub enum JsonSchemas {
    Table,
    Id,
}
