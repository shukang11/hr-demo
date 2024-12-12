
from typing import TYPE_CHECKING
from flask_cors import CORS

if TYPE_CHECKING:
    from flask import Flask


def init_app(app: 'Flask') -> None:
    from .health import bp as health_bp
    
    
    # CORS(
    #     account_bp,
    #     allow_headers=["Content-Type", "Authorization", "X-App-Code"],
    #     methods=["GET", "PUT", "POST", "OPTIONS", "PATCH"],
    # )
    # app.register_blueprint(account_bp)
    
    app.register_blueprint(health_bp)