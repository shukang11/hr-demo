pub mod health;
pub mod users;

pub(crate) use health::build_routes as health_routes;
pub(crate) use users::build_routes as user_routes;