from flask import Flask
from configs import shared_config

def init_app(app: Flask):
    # 尝试获取配置惨呼，如果没有直接返回
    if not shared_config.API_COMPRESSION_ENABLED:
        return
    if shared_config.API_COMPRESSION_ENABLED:
        from flask_compress import Compress

        app.config["COMPRESS_MIMETYPES"] = [
            "application/json",
            "image/svg+xml",
            "text/html",
        ]

        compress = Compress()
        compress.init_app(app)