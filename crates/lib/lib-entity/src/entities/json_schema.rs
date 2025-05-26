use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use super::company;

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
    pub company_id: Option<i32>,      // 公司ID
    pub entity_type: String,          // Schema适用的实体类型
    pub is_system: bool,              // 是否为系统预设Schema
    pub version: i32,                 // Schema版本号
    pub parent_schema_id: Option<i32>, // 父Schema ID，用于版本管理
    pub ui_schema: Option<Value>,     // UI展示相关的配置
    pub remark: Option<String>,       // 备注
    #[serde(skip)]
    #[serde(serialize_with = "to_milli_tsopt")]
    pub created_at: NaiveDateTime,    // 创建时间
    #[serde(skip)]
    #[serde(serialize_with = "to_milli_tsopt")]
    pub updated_at: NaiveDateTime,    // 更新时间
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum Column {
    Id,
    Name,
    Schema,
    CompanyId,
    EntityType,
    IsSystem,
    Version,
    ParentSchemaId,
    UiSchema,
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
            Self::Name => ColumnType::String(StringLen::N(255)).def(),
            Self::Schema => ColumnType::Json.def(),
            Self::CompanyId => ColumnType::Integer.def().null(),
            Self::EntityType => ColumnType::String(StringLen::N(50)).def(),
            Self::IsSystem => ColumnType::Boolean.def(),
            Self::Version => ColumnType::Integer.def(),
            Self::ParentSchemaId => ColumnType::Integer.def().null(),
            Self::UiSchema => ColumnType::Json.def().null(),
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
    Company,
    ParentSchema,
}

impl RelationTrait for Relation {
    fn def(&self) -> RelationDef {
        match self {
            Self::Company => Entity::belongs_to(company::Entity)
                .from(Column::CompanyId)
                .to(company::Column::Id)
                .into(),
            Self::ParentSchema => Entity::belongs_to(Entity)
                .from(Column::ParentSchemaId)
                .to(Column::Id)
                .into(),
        }
    }
}

impl ActiveModelBehavior for ActiveModel {} 