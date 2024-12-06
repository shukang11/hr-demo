use axum::{routing::get, Router};

#[utoipa::path(
    get,
    path = "/health",
    tag = "health",
    responses(
        (status = 200, description = "健康检查成功", body = String)
    )
)]
pub async fn health_check() -> &'static str {
    "OK"
}

pub(crate) fn build_routes() -> Router {
    Router::new().route("/", get(health_check))
}