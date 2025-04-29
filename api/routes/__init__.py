from flask import Flask, Blueprint


def init_app(app: "Flask") -> None:
    from .health import bp as health_bp
    from .auth import bp as auth_bp
    from .position import bp as position_bp
    from .candidate import bp as candidate_bp

    api_bp = Blueprint("api", __name__, url_prefix="/api")

    api_bp.register_blueprint(auth_bp)
    api_bp.register_blueprint(position_bp)
    api_bp.register_blueprint(candidate_bp)
    # api_bp.register_blueprint(companies_bp)

    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)
