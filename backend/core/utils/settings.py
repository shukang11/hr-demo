import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = Path(os.path.join(os.getcwd(), ".env"))

if not env_file.exists():
    raise FileNotFoundError(f"env_file not found: {env_file}")

content = env_file.read_text(encoding="utf-8")


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str = "SECRET_KEY"
    ALGORITHM: str = "HS256"
    ECHO_SQL: bool = False

    model_config = SettingsConfigDict(
        env_file=env_file,
        case_sensitive=False,
    )


settings = Settings.model_validate({})
