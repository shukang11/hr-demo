from typing import Tuple
from flask import Blueprint, request, Response
from flask_login import login_user
from managers.account_manager import AccountService
from schema.common.http import ResponseSchema, make_api_response
from schema.user import LoginRequest, LoginResponse
from extensions.ext_database import db
# 创建认证相关的蓝图
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login() -> Tuple[Response, int]:
    """用户登录接口
    
    处理用户的登录请求，验证用户名和密码，生成认证令牌
    
    Returns:
        Tuple[Response, int]: 包含登录响应数据的JSON响应和HTTP状态码
    """
    service = AccountService(session=db.session)
    try:
        # 使用 Pydantic 模型验证请求数据
        login_data = LoginRequest(**request.get_json())
    except ValueError:
        return make_api_response(
            ResponseSchema[LoginResponse].from_error(
                message='无效的请求数据',
                status=400
            ), 400
        )

    # 处理登录请求
    response_data, error_message, status_code = service.process_login(login_data)
    
    # 处理错误情况
    if error_message:
        return make_api_response(
            ResponseSchema[LoginResponse].from_error(
                message=error_message,
                status=status_code
            ), status_code
        )

    # 在Flask-Login中记录用户登录状态
    user = service.find_account_by_token(response_data.token)
    if user:
        login_user(user)  # 确保这里调用了 login_user

    # 返回成功响应
    return make_api_response(
        ResponseSchema[LoginResponse](
            data=response_data,
            context={"status": 200, "message": "登录成功"}
        )
    )