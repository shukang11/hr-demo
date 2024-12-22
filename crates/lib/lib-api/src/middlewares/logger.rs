use axum::{body::Body, http::Request, response::Response};
use futures::future::BoxFuture;
use std::{
    fmt::Display,
    task::{Context, Poll},
    time::{Duration, Instant},
};
use tower::{Layer, Service};

#[derive(Debug, Default)]
struct LoggerMessage {
    method: String,
    uri: String,
    status_code: u16,
    latency: Duration,
}

impl Display for LoggerMessage {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{} {} [{}] {:?}",
            self.method, self.uri, self.status_code, self.latency
        )
    }
}

#[derive(Clone)]
pub struct LoggerLayer;

impl<S> Layer<S> for LoggerLayer {
    type Service = LoggerMiddleware<S>;

    fn layer(&self, inner: S) -> Self::Service {
        LoggerMiddleware { inner }
    }
}

#[derive(Clone)]
pub struct LoggerMiddleware<S> {
    inner: S,
}

impl<S> Service<Request<Body>> for LoggerMiddleware<S>
where
    S: Service<Request<Body>, Response = Response> + Send + 'static,
    S::Future: Send + 'static,
{
    type Response = S::Response;
    type Error = S::Error;
    type Future = BoxFuture<'static, Result<Self::Response, Self::Error>>;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.inner.poll_ready(cx)
    }

    fn call(&mut self, req: Request<Body>) -> Self::Future {
        let now = Instant::now();

        let message = LoggerMessage {
            method: req.method().to_string(),
            uri: req.uri().to_string(),
            ..Default::default()
        };

        let future = self.inner.call(req);

        Box::pin(async move {
            let response: Response = future.await?;
            let mut message = message;
            message.status_code = response.status().as_u16();
            message.latency = now.elapsed();

            if message.status_code < 200 || message.status_code >= 300 {
                tracing::warn!("{}", message);
            } else if message.uri.contains("/api/") {
                tracing::info!("{}", message);
            }

            Ok(response)
        })
    }
}
