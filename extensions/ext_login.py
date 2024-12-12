import json
from typing import Optional

from flask import Flask, Request, Response
from flask_login import LoginManager

login_manager = LoginManager()


def init_app(app: Flask) -> None:
    login_manager.init_app(app)

    from managers.account_manager import AccountService

    @login_manager.request_loader
    def load_user_from_request(request: Request):
        # get token
        token: Optional[str] = None
        token = request.headers.get("Authorization")
        if not token:
            token = request.headers.get("token")
        if not token:
            token = request.headers.get("Token")

        if not token:
            return None

        if token.startswith("Bearer "):
            token = token.removeprefix("Bearer ")
        account = AccountService.find_account_by_token(token)

        return account

    @login_manager.user_loader
    def load_user(user_id: int):
        account = AccountService.find_account_by_id(user_id)
        return account


    @login_manager.unauthorized_handler
    def unauthorized() -> Response:
        from schema.common.http import ResponseSchema
        return Response(
            ResponseSchema[str].from_error("未登录").model_dump_json(),
            status=401,
            content_type="application/json",
        )



    return None
