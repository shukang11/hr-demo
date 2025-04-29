from typing import Optional
import logging
import os
import sys
from configs import shared_config
from logging.handlers import RotatingFileHandler

from flask import Flask


def init_app(app: Flask):
    if shared_config.LOG_ENABLED is False:
        return

    log_handlers = []

    # 如果设置了日志文件，添加文件处理器
    log_file: Optional[str] = shared_config.LOG_FILE
    if log_file:
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        log_handlers.append(
            RotatingFileHandler(
                filename=log_file,
                maxBytes=shared_config.LOG_FILE_MAX_SIZE * 1024 * 1024,
                backupCount=shared_config.LOG_FILE_BACKUP_COUNT,
            )
        )

    # 总是添加控制台处理器，不再依赖于LOG_FILE的存在
    log_handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        level=shared_config.LOG_LEVEL,
        format=shared_config.LOG_FORMAT,
        datefmt=shared_config.LOG_DATEFORMAT,
        handlers=log_handlers,
        force=True,
    )
    log_tz = shared_config.LOG_TZ
    if log_tz:
        from datetime import datetime

        import pytz

        timezone = pytz.timezone(log_tz)

        def time_converter(seconds):
            return (
                datetime.fromtimestamp(seconds, tz=pytz.utc)
                .astimezone(timezone)
                .timetuple()
            )

        for handler in logging.root.handlers:
            if handler.formatter is not None:
                handler.formatter.converter = time_converter
