use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;
use axum::{Router, routing::get};

#[derive(OpenApi)]
#[openapi(
    paths(
        // TODO: 在这里添加你的API路径
    ),
    components(
        schemas(
            // TODO: 在这里添加你的数据模型
        )
    ),
    tags(
        (name = "hr-demo", description = "HR Demo API")
    )
)]
pub struct ApiDoc;

pub fn create_swagger_routes() -> Router {
    Router::new()
        .merge(SwaggerUi::new("/swagger-ui")
            .url("/api-docs/openapi.json", ApiDoc::openapi()))
} 