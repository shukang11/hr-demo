mod error;
mod handlers;
mod middlewares;
mod response;
mod routes;
mod server;

use axum::Router;
pub use error::APIError;
pub use lib_core::DBConnection;
pub use lib_utils::Settings;
pub use server::Server;

#[derive(Debug)]
pub struct AppState {
    pub pool: DBConnection,
    pub setting: Settings,
}

/// 创建路由
pub fn create_router() -> Router {
    routes::create_router()
}
