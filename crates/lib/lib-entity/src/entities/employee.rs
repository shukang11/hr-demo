use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

// Gender
#[derive(Debug, Clone, PartialEq, Eq, EnumIter, DeriveActiveEnum, Deserialize, Serialize)]
#[sea_orm(rs_type = "String", db_type = "String(StringLen::N(16))")]
pub enum Gender {
    #[sea_orm(string_value = "Male")]
    Male,
    #[sea_orm(string_value = "Female")]
    Female,
    #[sea_orm(string_value = "Unknown")]
    Unknown,
}

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct Entity;

impl EntityName for Entity {
    fn table_name(&self) -> &str {
        "employee"
    }
    fn schema_name(&self) -> Option<&str> {
        None
    }
}

#[derive(Clone, Debug, PartialEq, DeriveModel, DeriveActiveModel, Deserialize, Serialize)]
pub struct Model {
    #[serde(skip)]
    pub id: i32,                      // 主键
    pub name: String,                 // 姓名
    pub email: Option<String>,        // 邮箱
    pub phone: Option<String>,        // 电话
    pub birthdate: Option<NaiveDateTime>, // 出生日期
    pub address: Option<String>,      // 地址
    pub gender: Gender,               // 性别
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
    Email,
    Phone,
    Birthdate,
    Address,
    Gender,
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
            Self::Email => ColumnType::String(StringLen::N(255)).def().nullable(),
            Self::Phone => ColumnType::String(StringLen::N(20)).def().nullable(),
            Self::Birthdate => ColumnType::Date.def().nullable(),
            Self::Address => ColumnType::String(StringLen::N(255)).def().nullable(),
            Self::Gender => ColumnType::String(StringLen::None).def(),
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
    EmployeePosition,
}

impl RelationTrait for Relation {
    fn def(&self) -> RelationDef {
        match self {
            Self::EmployeePosition => Entity::has_many(super::employee_position::Entity).into(),
        }
    }
}

impl Related<super::employee_position::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::EmployeePosition.def()
    }
}

impl ActiveModelBehavior for ActiveModel {} 