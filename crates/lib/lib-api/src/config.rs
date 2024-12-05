use std::net::SocketAddr;

#[derive(Debug, Clone)]
pub struct Config {
    addr: SocketAddr,
    log_dir: Option<String>,
    database_url: String,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            addr: "127.0.0.1:3000".parse().unwrap(),
            log_dir: None,
            database_url: "sqlite:memory:".to_string(),
        }
    }
}

impl Config {

    pub fn with_addr(mut self, addr: impl AsRef<str>) -> Self {
        self.addr = addr.as_ref().parse().expect("Invalid address format");
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

    pub fn addr(&self) -> SocketAddr {
        self.addr
    }

    pub fn log_dir(&self) -> Option<&str> {
        self.log_dir.as_deref()
    }

    pub fn database_url(&self) -> &str {
        &self.database_url
    }
} 