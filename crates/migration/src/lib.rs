pub use sea_orm_migration::prelude::*;

mod m20241207_161705_init_tables;
mod m20241223_candidates;
mod m20250212_001017_add_marital_emergency_contact;

pub struct Migrator;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![
            Box::new(m20241207_161705_init_tables::Migration),
            Box::new(m20241223_candidates::Migration),
            Box::new(m20250212_001017_add_marital_emergency_contact::Migration),
        ]
    }
}
