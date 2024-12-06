use axum::Router;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;
use lib_schema::models::user::{CreateUser, User};

#[derive(OpenApi)]
#[openapi(
    paths(
        crate::handlers::health::health_check,
        crate::handlers::users::create_user,
    ),
    components(
        schemas(User, CreateUser)
    ),
    tags(
        (name = "health", description = "健康检查接口"),
        (name = "users", description = "用户管理接口")
    )
)]
pub struct ApiDoc;

/// 创建 Swagger UI 路由
pub fn create_swagger_routes() -> Router {
    Router::new().merge(SwaggerUi::new("/swagger-ui")
        .url("/api-docs/openapi.json", ApiDoc::openapi()))
} 