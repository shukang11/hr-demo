pub mod candidate;
pub mod company;
pub mod dashboard;
pub mod department;
pub mod employee;
pub mod employee_position;
pub mod json_schema;
pub mod json_value;
pub mod position;

pub use candidate::{Candidate, InsertCandidate, UpdateCandidateStatus};
pub use company::{Company, InsertCompany};
pub use dashboard::*;
pub use department::{Department, InsertDepartment};
pub use employee::{Employee, Gender, InsertEmployee};
pub use employee_position::{EmployeePosition, InsertEmployeePosition};
pub use json_schema::{InsertJsonSchema, JsonSchema};
pub use json_value::{InsertJsonValue, JsonValue, QueryEntityValues};
pub use position::{InsertPosition, Position};
