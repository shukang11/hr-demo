use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct Entity;

impl EntityName for Entity {
    fn table_name(&self) -> &str {
        "employee_position"
    }
    fn schema_name(&self) -> Option<&str> {
        None
    }
}

#[derive(Clone, Debug, PartialEq, DeriveModel, DeriveActiveModel, Deserialize, Serialize)]
pub struct Model {
    #[serde(skip)]
    pub id: i32,                      // 主键
    pub employee_id: i32,             // 员工ID
    pub company_id: i32,              // 公司ID
    pub department_id: i32,           // 部门ID
    pub position_id: i32,             // 职位ID
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
    EmployeeId,
    CompanyId,
    DepartmentId,
    PositionId,
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
            Self::EmployeeId => ColumnType::Integer.def(),
            Self::CompanyId => ColumnType::Integer.def(),
            Self::DepartmentId => ColumnType::Integer.def(),
            Self::PositionId => ColumnType::Integer.def(),
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
    Department,
    Employee,
    Position,
}

impl RelationTrait for Relation {
    fn def(&self) -> RelationDef {
        match self {
            Self::Company => Entity::belongs_to(super::company::Entity)
                .from(Column::CompanyId)
                .to(super::company::Column::Id)
                .into(),
            Self::Department => Entity::belongs_to(super::department::Entity)
                .from(Column::DepartmentId)
                .to(super::department::Column::Id)
                .into(),
            Self::Employee => Entity::belongs_to(super::employee::Entity)
                .from(Column::EmployeeId)
                .to(super::employee::Column::Id)
                .into(),
            Self::Position => Entity::belongs_to(super::position::Entity)
                .from(Column::PositionId)
                .to(super::position::Column::Id)
                .into(),
        }
    }
}

impl Related<super::company::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Company.def()
    }
}

impl Related<super::department::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Department.def()
    }
}

impl Related<super::employee::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Employee.def()
    }
}

impl Related<super::position::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Position.def()
    }
}

impl ActiveModelBehavior for ActiveModel {} 