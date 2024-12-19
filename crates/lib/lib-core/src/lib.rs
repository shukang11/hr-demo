pub mod services;

pub use sea_orm::DbErr;
pub type DBConnection = sea_orm::DatabaseConnection;

// Re-export commonly used types
pub use services::company::CompanyService;
pub use services::department::DepartmentService;
pub use services::employee::EmployeeService;
pub use services::position::PositionService;

use sea_orm::{ConnectOptions, Database};
use std::time::Duration;

pub async fn get_db_conn(uri: String) -> DBConnection {
    let mut opt = ConnectOptions::new(uri.to_owned());
    opt.max_connections(1000)
        .min_connections(5)
        .connect_timeout(Duration::from_secs(30))
        .idle_timeout(Duration::from_secs(8))
        .sqlx_logging(false);
    let db = Database::connect(opt)
        .await
        .expect(format!("Failed to connect to database: {}", uri).as_str());
    println!("Database connected, {}", uri);
    tracing::info!("Database connected");
    db
}

#[cfg(test)]
mod test_runner {
    use super::DBConnection;
    use migration::{Migrator, MigratorTrait};

    pub(crate) async fn setup_database() -> DBConnection {
        let base_url =
            std::env::var("DATABASE_URL").unwrap_or_else(|_| "sqlite::memory:?mode=rwc".to_owned());
        let db = crate::get_db_conn(base_url).await;
        // 假设 `Migrator` 是你的迁移模块，它实现了 `MigratorTrait`
        if let Err(e) = Migrator::up(&db, None).await {
            println!("error: {:?}", e);
        }
        db
    }
}
