from flask import Blueprint, Response
from libs.schema.http import make_api_response, ResponseSchema

bp = Blueprint("health", __name__, url_prefix="/health")


@bp.route("/ping", methods=["GET", "POST"])
def ping() -> Response:
    return make_api_response(ResponseSchema(data={"ping": "pong"}))
