from typing import Tuple
from flask import Blueprint, request, Response
from flask_login import login_required, current_user
from extensions.ext_database import db
from managers.company_manager import CompanyService
from schema.common.http import ResponseSchema, make_api_response
from schema.company import CompanyCreate, CompanyInResponse

# 创建公司相关的蓝图
bp = Blueprint('companies', __name__, url_prefix='/api/companies')

@bp.route('', methods=['POST'])
@login_required
def create_company() -> Tuple[Response, int]:
    """创建新公司接口
    
    处理创建新公司的请求，需要用户登录
    
    Returns:
        Tuple[Response, int]: 包含公司创建响应数据的JSON响应和HTTP状态码
    """
    try:
        # 验证请求数据
        company_data = CompanyCreate(**request.get_json())
    except ValueError:
        return make_api_response(
            ResponseSchema[CompanyInResponse].from_error(
                message='无效的请求数据',
                status=400
            ), 400
        )

    # 创建公司服务实例
    company_service = CompanyService(current_user, db.session)
    
    # 处理公司创建
    company, error_message = company_service.create_company(company_data)
    
    if error_message:
        return make_api_response(
            ResponseSchema[CompanyInResponse].from_error(
                message=error_message,
                status=400
            ), 400
        )

    # 返回成功响应
    return make_api_response(
        ResponseSchema[CompanyInResponse](
            data=company,
            context={"status": 200, "message": "公司创建成功"}
        )
    ) 