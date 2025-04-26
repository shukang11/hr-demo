from pydantic import Field
from pydantic_settings import BaseSettings


class CompressionConfig(BaseSettings):
    API_COMPRESSION_ENABLED: bool = Field(
        description="API Compress Enable", default=False
    )