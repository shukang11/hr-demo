pub mod health;
pub mod company;
pub mod department;

pub(crate) use health::build_routes as health_routes;
pub(crate) use company::build_routes as company_routes;
pub(crate) use department::build_routes as department_routes;