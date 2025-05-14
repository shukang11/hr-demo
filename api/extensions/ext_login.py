from typing import Optional
from sqlalchemy import text

from flask import Flask, Request, Response
from flask_login import LoginManager
from flask import current_app

login_manager = LoginManager()


def init_app(app: Flask) -> None:
    login_manager.init_app(app)

    from services.account import AccountService
    from extensions.ext_database import db

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
            current_app.logger.warning("请求中未找到认证令牌")
            return None

        if token.startswith("Bearer "):
            token = token.removeprefix("Bearer ")

        account_service = AccountService(session=db.session)
        account = account_service.find_account_by_token(token)

        return account

    @login_manager.user_loader
    def load_user(user_id: int):
        current_app.logger.info(f"load user {user_id}")
        try:
            account = AccountService(session=db.session).find_account_by_id(user_id)
            if account:
                current_app.logger.info(
                    f"通过ID成功加载用户: id={user_id}, username={account.username}"
                )
            else:
                current_app.logger.warning(f"未找到ID为 {user_id} 的用户")
            return account
        except Exception as e:
            current_app.logger.error(
                f"通过ID加载用户时发生异常: {str(e)}", exc_info=True
            )
            return None

    @login_manager.unauthorized_handler
    def unauthorized() -> Response:
        current_app.logger.info("unauthorized")
        from libs.schema.http import ResponseSchema

        return Response(
            ResponseSchema[str].from_error("未登录").model_dump_json(),
            status=401,
            content_type="application/json",
        )

    return None
