use std::error::Error;

use lib_entity::migrations::*;
use sea_orm_migration::prelude::*;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::DEBUG)
        .with_test_writer()
        .init();

    let migrations = vec![
        Box::new(CreateCandidatesTable),
    ];

    let connection = sea_orm::Database::connect("sqlite://./hr-data.sqlite3?mode=rwc").await?;

    let schema_manager = SchemaManager::new(&connection);

    for migration in migrations {
        migration.up(&schema_manager).await?;
    }

    Ok(())
} 