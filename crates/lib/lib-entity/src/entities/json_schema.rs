use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct Entity;

impl EntityName for Entity {
    fn table_name(&self) -> &str {
        "json_schemas"
    }
    fn schema_name(&self) -> Option<&str> {
        None
    }
}

#[derive(Clone, Debug, PartialEq, DeriveModel, DeriveActiveModel, Deserialize, Serialize)]
pub struct Model {
    #[serde(skip)]
    pub id: i32,                      // 主键
    pub name: String,                 // schema名称
    pub schema: Value,                // JSON Schema
    #[serde(skip)]
    #[serde(serialize_with = "to_milli_tsopt")]
    pub created_at: NaiveDateTime,    // 创建时间
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum Column {
    Id,
    Name,
    Schema,
    CreatedAt,
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
            Self::Name => ColumnType::String(StringLen::N(255)).def(),
            Self::Schema => ColumnType::Json.def(),
            Self::CreatedAt => ColumnType::DateTime
                .def()
                .default(Expr::current_timestamp()),
        }
    }
}

#[derive(Copy, Clone, Debug, EnumIter)]
pub enum Relation {
}

impl RelationTrait for Relation {
    fn def(&self) -> RelationDef {
        unreachable!()
    }
}

impl ActiveModelBehavior for ActiveModel {} 