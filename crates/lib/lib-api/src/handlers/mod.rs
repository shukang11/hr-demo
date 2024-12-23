pub mod health;
pub mod company;
pub mod department;
pub mod employee;
pub mod position;
pub mod candidate;

pub(crate) use health::build_routes as health_routes;
pub(crate) use company::build_routes as company_routes;
pub(crate) use department::build_routes as department_routes;
pub(crate) use employee::build_routes as employee_routes;
pub(crate) use position::build_routes as position_routes;
pub(crate) use candidate::build_routes as candidate_routes;

use axum::Router;

pub fn build_routes() -> Router {
    Router::new()
        .nest("/company", company::build_routes())
        .nest("/department", department::build_routes())
        .nest("/employee", employee::build_routes())
        .nest("/position", position::build_routes())
        .nest("/candidate", candidate::build_routes())
}