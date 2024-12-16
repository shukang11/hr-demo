use axum::{routing::get, Router};

pub async fn health_check() -> &'static str {
    "OK"
}

pub(crate) fn build_routes() -> Router {
    Router::new().route("/", get(health_check))
}