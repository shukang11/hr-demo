use axum::Router;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

#[derive(OpenApi)]
#[openapi(
    paths(
        crate::handlers::health::health_check,
    ),
    components(
    ),
    tags(
        (name = "health", description = "健康检查接口"),
        (name = "users", description = "用户管理接口")
    )
)]
pub struct ApiDoc;

/// 创建 Swagger UI 路由
pub fn create_swagger_routes() -> Router {
    Router::new().merge(SwaggerUi::new("/docs")
        .url("/api-docs/openapi.json", ApiDoc::openapi()))
} 