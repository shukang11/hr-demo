use axum::Router;

use crate::handlers;

pub fn create_router() -> Router {
    Router::new()
        .nest("/health", handlers::build_routes())
}
