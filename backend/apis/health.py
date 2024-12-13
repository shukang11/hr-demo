from flask import Blueprint


bp = Blueprint("health", __name__, url_prefix="/health")

@bp.route("/ping", methods=["GET"])
def ping() -> dict:
    return {
        "ping": "pong"
    }