use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("配置加载失败: {0}")]
    LoadError(#[from] config::ConfigError),
    #[error("配置未初始化")]
    NotInitialized,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Settings {
    pub addr: String,
    pub log_dir: Option<String>,
    pub database_url: String,
    pub workspace: String,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            addr: "localhost:5000".to_string(),
            log_dir: None,
            database_url: "sqlite:memory:".to_string(),
            workspace: "./workspace".to_string(),
        }
    }
}

impl Settings {
    pub fn with_addr(mut self, addr: impl AsRef<str>) -> Self {
        self.addr = addr.as_ref().to_string();
        self
    }

    pub fn with_database_url(mut self, database_url: impl Into<String>) -> Self {
        self.database_url = database_url.into();
        self
    }

    pub fn with_log_dir(mut self, dir: impl Into<String>) -> Self {
        self.log_dir = Some(dir.into());
        self
    }

    pub fn log_dir(&self) -> Option<&str> {
        self.log_dir.as_deref()
    }

    pub fn workspace(&self) -> &str {
        &self.workspace
    }

    pub fn database_url(&self) -> &str {
        &self.database_url
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_config() {
        let config = Settings::default()
            .with_addr("127.0.0.1:8080")
            .with_database_url("sqlite:test.db")
            .with_log_dir("logs");

        assert_eq!(config.database_url(), "sqlite:test.db");
        assert_eq!(config.log_dir(), Some("logs"));
    }
}
