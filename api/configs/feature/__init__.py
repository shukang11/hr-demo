from .compress_config import CompressionConfig
from .log_config import LoggingConfig


class FeatureConfig(
    LoggingConfig,
    CompressionConfig,
):
    pass