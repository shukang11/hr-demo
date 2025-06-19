use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct Entity;

impl EntityName for Entity {
    fn table_name(&self) -> &str {
        "json_values"
    }
    fn schema_name(&self) -> Option<&str> {
        None
    }
}

#[derive(Clone, Debug, PartialEq, DeriveModel, DeriveActiveModel, Deserialize, Serialize)]
pub struct Model {
    #[serde(skip)]
    pub id: i32, // 主键
    pub schema_id: i32,         // 关联的JSON Schema ID
    pub entity_id: i32,         // 关联的实体ID
    pub entity_type: String,    // 关联的实体类型
    pub value: Value,           // 实际存储的JSON数据
    pub remark: Option<String>, // 备注
    #[serde(skip)]
    #[serde(serialize_with = "to_milli_tsopt")]
    pub created_at: NaiveDateTime, // 创建时间
    #[serde(skip)]
    #[serde(serialize_with = "to_milli_tsopt")]
    pub updated_at: NaiveDateTime, // 更新时间
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum Column {
    Id,
    SchemaId,
    EntityId,
    EntityType,
    Value,
    Remark,
    CreatedAt,
    UpdatedAt,
}

#[derive(Copy, Clone, Debug, EnumIter, DerivePrimaryKey)]
pub enum PrimaryKey {
    Id,
}

impl PrimaryKeyTrait for PrimaryKey {
    type ValueType = i32;
    fn auto_increment() -> bool {
        true
    }
}

impl ColumnTrait for Column {
    type EntityName = Entity;
    fn def(&self) -> ColumnDef {
        match self {
            Self::Id => ColumnType::Integer.def(),
            Self::SchemaId => ColumnType::Integer.def(),
            Self::EntityId => ColumnType::Integer.def(),
            Self::EntityType => ColumnType::String(StringLen::N(50)).def(),
            Self::Value => ColumnType::Json.def(),
            Self::Remark => ColumnType::String(StringLen::N(255)).def().null(),
            Self::CreatedAt => ColumnType::DateTime
                .def()
                .default(Expr::current_timestamp()),
            Self::UpdatedAt => ColumnType::DateTime
                .def()
                .default(Expr::current_timestamp()),
        }
    }
}

#[derive(Copy, Clone, Debug, EnumIter)]
pub enum Relation {
    JsonSchema,
}

impl RelationTrait for Relation {
    fn def(&self) -> RelationDef {
        match self {
            Self::JsonSchema => Entity::belongs_to(super::json_schema::Entity)
                .from(Column::SchemaId)
                .to(super::json_schema::Column::Id)
                .into(),
        }
    }
}

impl ActiveModelBehavior for ActiveModel {}
