
mod error;
mod handlers;
mod server;
mod middlewares;
mod routes;
mod docs;

pub use lib_utils::Settings;
pub use error::{ApiError, ApiResult};
pub use server::Server;
pub use docs::ApiDoc;
pub use lib_core::DBPool;
use axum::Router;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

#[derive(Debug)]
pub struct AppState {
    pub pool: DBPool,
    pub setting: Settings,
}

/// 创建包含 Swagger UI 的路由
pub fn create_router() -> Router {
    routes::create_router()
        .merge(SwaggerUi::new("/swagger-ui")
            .url("/api-docs/openapi.json", docs::ApiDoc::openapi()))
}
