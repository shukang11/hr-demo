from flask import Blueprint
from libs.schema.http import make_api_response, ResponseSchema

bp = Blueprint("health", __name__, url_prefix="/health")


@bp.route("/ping", methods=["GET", "POST"])
def ping() -> dict:
    return make_api_response(ResponseSchema(data={"ping": "pong"}))
