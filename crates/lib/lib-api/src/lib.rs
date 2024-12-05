mod config;
mod error;
mod handlers;
mod server;
mod middlewares;
mod routes;

pub use config::Config;
pub use error::{ApiError, ApiResult};
pub use server::Server;

use sqlx::sqlite::SqlitePool;

#[derive(Debug)]
pub struct AppState {
    pub pool: SqlitePool,
    pub setting: Config,
}
