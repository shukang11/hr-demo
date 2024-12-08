use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct Entity;

impl EntityName for Entity {
    fn table_name(&self) -> &str {
        "company"
    }
    fn schema_name(&self) -> Option<&str> {
        None
    }
}

#[derive(Clone, Debug, PartialEq, DeriveModel, DeriveActiveModel, Deserialize)]
pub struct Model {
    #[serde(skip)]
    pub id: i32,                      // 主键
    pub name: String,                 // 公司名称
    pub extra_value: Option<Value>,   // 额外JSON数据
    pub extra_schema_id: Option<i32>, // 额外数据schema ID
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
    ExtraValue,
    ExtraSchemaId,
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
            Self::ExtraValue => ColumnType::Json.def().nullable(),
            Self::ExtraSchemaId => ColumnType::Integer.def().nullable(),
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
    Department,
    Position,
    EmployeePosition,
}

impl RelationTrait for Relation {
    fn def(&self) -> RelationDef {
        match self {
            Self::Department => Entity::has_many(super::department::Entity).into(),
            Self::Position => Entity::has_many(super::position::Entity).into(),
            Self::EmployeePosition => Entity::has_many(super::employee_position::Entity).into(),
        }
    }
}

impl Related<super::department::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Department.def()
    }
}

impl Related<super::position::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Position.def()
    }
}

impl Related<super::employee_position::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::EmployeePosition.def()
    }
}

impl ActiveModelBehavior for ActiveModel {} 