use axum::Router;

use crate::handlers;

pub fn create_router() -> Router {
    Router::new()
        .nest("/health", handlers::health_routes())
        .nest("/company", handlers::company_routes())
        .nest("/department", handlers::department_routes())
        .nest("/employee", handlers::employee_routes())
        .nest("/position", handlers::position_routes())
        .nest("/candidate", handlers::candidate_routes())
        .nest("/dashboard", handlers::dashboard_routes())
}
