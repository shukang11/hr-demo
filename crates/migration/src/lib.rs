pub use sea_orm_migration::prelude::*;

mod m20241207_161705_init_tables;
mod m20241223_candidates;
mod m20250212_001017_add_marital_emergency_contact;
mod m20250526_001_accounts;
mod m20250526_002_json_values;
mod m20250526_003_account_company;
mod m20250526_004_account_tokens;
mod m20250526_005_extend_json_schemas;

pub struct Migrator;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![
            Box::new(m20241207_161705_init_tables::Migration),
            Box::new(m20241223_candidates::Migration),
            Box::new(m20250212_001017_add_marital_emergency_contact::Migration),
            Box::new(m20250526_001_accounts::Migration),
            Box::new(m20250526_002_json_values::Migration),
            Box::new(m20250526_003_account_company::Migration),
            Box::new(m20250526_004_account_tokens::Migration),
            Box::new(m20250526_005_extend_json_schemas::Migration),
        ]
    }
}
