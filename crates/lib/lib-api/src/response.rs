use axum::{
    response::{IntoResponse, Response},
    Json,
};
use chrono::NaiveDateTime;
use serde::Serialize;
use utoipa::ToSchema;

use crate::error::APIError;

#[derive(Debug, Serialize, ToSchema)]
pub struct APIResponseContext {
    pub code: i32,
    pub message: Option<String>,
    pub server_at: NaiveDateTime,
}

#[derive(Debug, Serialize, ToSchema)]
pub struct APIResponse<T: Serialize> {
    #[serde(skip_serializing_if = "Option::is_none")]
    data: Option<T>,
    context: APIResponseContext,
}

impl<T: Serialize> APIResponse<T> {
    pub fn new() -> Self {
        let context = APIResponseContext {
            code: 200_i32,
            message: None,
            server_at: chrono::Utc::now().naive_utc(),
        };
        APIResponse {
            data: None,
            context,
        }
    }

    pub fn with_code(mut self, code: i32) -> Self {
        self.context.code = code;
        self
    }

    pub fn with_data(mut self, data: T) -> Self {
        self.data = Some(data);
        self
    }

    pub fn with_message(mut self, message: String) -> Self {
        self.context.message = Some(message);
        self
    }

    pub fn with_error(self, error: APIError) -> Self {
        self.with_code(code_for_error(&error))
            .with_message(format!("{}", error))
    }
}

impl<T: Serialize> IntoResponse for APIResponse<T> {
    fn into_response(self) -> Response {
        Json(self).into_response()
    }
}

pub fn code_for_error(e: &APIError) -> i32 {
    match e {
        APIError::Internal(_) => 99999,
    }
}
