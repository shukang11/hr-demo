from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


def init_app(app: 'Flask') -> None:
    from .health import bp as health_bp
    from .auth import bp as auth_bp
    from .companies import bp as companies_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(companies_bp)
