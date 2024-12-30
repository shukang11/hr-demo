pub mod health;
pub mod company;
pub mod department;
pub mod employee;
pub mod position;
pub mod candidate;
pub mod dashboard;

pub(crate) use health::build_routes as health_routes;
pub(crate) use company::build_routes as company_routes;
pub(crate) use department::build_routes as department_routes;
pub(crate) use employee::build_routes as employee_routes;
pub(crate) use position::build_routes as position_routes;
pub(crate) use candidate::build_routes as candidate_routes;
pub(crate) use dashboard::build_routes as dashboard_routes;
