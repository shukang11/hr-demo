use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct Entity;

impl EntityName for Entity {
    fn table_name(&self) -> &str {
        "position"
    }
    fn schema_name(&self) -> Option<&str> {
        None
    }
}

#[derive(Clone, Debug, PartialEq, DeriveModel, DeriveActiveModel, Deserialize, Serialize)]
pub struct Model {
    #[serde(skip)]
    pub id: i32,                      // 主键
    pub name: String,                 // 职位名称
    pub company_id: i32,              // 公司ID
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
    CompanyId,
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
            Self::Name => ColumnType::String(StringLen::N(64)).def(),
            Self::CompanyId => ColumnType::Integer.def(),
            Self::Remark => ColumnType::String(StringLen::N(255)).def().nullable(),
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
    EmployeePosition,
}

impl RelationTrait for Relation {
    fn def(&self) -> RelationDef {
        match self {
            Self::Company => Entity::belongs_to(super::company::Entity)
                .from(Column::CompanyId)
                .to(super::company::Column::Id)
                .into(),
            Self::EmployeePosition => Entity::has_many(super::employee_position::Entity).into(),
        }
    }
}

impl Related<super::company::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Company.def()
    }
}

impl Related<super::employee_position::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::EmployeePosition.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}