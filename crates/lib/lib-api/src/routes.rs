use axum::Router;

use crate::handlers;

pub fn create_router() -> Router {
    Router::new()
        .nest("/health", handlers::health_routes())
        .nest("/api/v1", handlers::user_routes())
}
