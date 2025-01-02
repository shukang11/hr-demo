use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum APIError {
    #[error("Internal server error")]
    Internal(#[from] anyhow::Error),
    #[error("{0}")]
    BadRequest(String),
}

impl IntoResponse for APIError {
    fn into_response(self) -> Response {
        let status = match self {
            APIError::Internal(_) => StatusCode::INTERNAL_SERVER_ERROR,
            APIError::BadRequest(_) => StatusCode::BAD_REQUEST,
        };

        (status, self.to_string()).into_response()
    }
}
