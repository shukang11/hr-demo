use axum::{routing::get, Router};


// 健康检查处理函数
async fn health_check() -> &'static str {
    "OK"
} 

pub(crate) fn build_routes() -> axum::Router {
    Router::new().route("/health", get(health_check))
}