from flask import Blueprint, Response, current_app, request
from flask_login import login_user, login_required, current_user
from pydantic import ValidationError
from libs.schema.http import ResponseSchema, make_api_response
from extensions.ext_database import db
from services.account import (
    AccountService,
    LoginRequest,
    LoginResponse,
    AccountSchema,
    AccountLoginError,
)
from libs.models.account import AccountInDB

# 创建认证相关的蓝图
bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["POST"])
def login() -> Response:
    """用户登录接口
    ResponseSchema[LoginResponse]

    处理用户的登录请求，验证用户名和密码，生成认证令牌

    Returns:
        Response: 包含登录响应数据的JSON响应和HTTP状态码
    """

    try:
        parameters: LoginRequest = LoginRequest.model_validate(request.json)
        service = AccountService(session=db.session)
        response_data: LoginResponse = service.process_login(parameters)

        # 在Flask-Login中记录用户登录状态
        user = service.find_account_by_token(response_data.token)
        if user:
            login_user(user)  # 确保这里调用了 login_user
        return make_api_response(
            ResponseSchema[LoginResponse](
                data=response_data,
            )
        )
    except ValidationError as _e:
        return make_api_response(
            ResponseSchema[LoginResponse].from_error(
                message="无效的请求数据", status=400
            ),
            400,  # 确保HTTP状态码也设置为400
        )
    except AccountLoginError as e:
        current_app.logger.error(f"Login failed: {e}")
        return make_api_response(
            ResponseSchema[LoginResponse].from_error(message=str(e), status=401),
            401,  # 修正状态码为401，与message保持一致
        )
    except ValueError as e:
        current_app.logger.error(f"Invalid login data: {e}")
        # 500
        return make_api_response(
            ResponseSchema[LoginResponse].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/logout", methods=["POST"])
def logout() -> Response:
    """用户登出接口

    处理用户的登出请求，清除认证令牌

    Returns:
        Response: 包含登出响应数据的JSON响应和HTTP状态码
    """
    # 清除用户登录状态
    from flask_login import logout_user

    logout_user()

    return make_api_response(ResponseSchema[None](data=None))


# user info
@bp.route("/info", methods=["GET"])
@login_required
def info() -> Response:
    """获取用户信息接口

    Returns:
        Response: 包含用户信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401)
        )

    # 获取当前用户信息 - 从LocalProxy转为实际的对象
    user: AccountInDB = current_user._get_current_object()

    print(f"当前用户: {user}")
    # 创建AccountSchema实例而不是使用model_validate
    account = AccountSchema.from_entity(user)

    return make_api_response(
        ResponseSchema[AccountSchema](data=account),
    )
