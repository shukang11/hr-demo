from flask import Blueprint, request, Response, current_app
from flask_login import current_user, login_required
from typing import Optional, List
from pydantic import ValidationError

from libs.schema.http import ResponseSchema, make_api_response
from extensions.ext_database import db
from services.company import CompanyService, CompanyCreate, CompanyUpdate, CompanySchema

# 创建公司相关的蓝图
bp = Blueprint("company", __name__, url_prefix="/company")


@bp.route("/insert", methods=["POST"])
@login_required
def insert_company() -> Response:
    """创建或更新公司
    
    如果请求数据中包含id字段，则更新现有公司；否则创建新公司。
    
    Returns:
        Response: 包含公司信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建公司服务实例
        service = CompanyService(session=db.session, account=user)
        
        # 获取请求数据
        request_data = request.json
        company_id = request_data.get("id")
        
        if company_id:
            # 更新现有公司
            company_data = CompanyUpdate.model_validate(request_data)
            result = service.update_company(company_id, company_data)
            if not result:
                return make_api_response(
                    ResponseSchema[CompanySchema].from_error(
                        message="更新公司失败，公司不存在或无权限", status=404
                    ),
                    404,
                )
        else:
            # 创建新公司
            company_data = CompanyCreate.model_validate(request_data)
            result = service.insert_company(company_data)
            if not result:
                return make_api_response(
                    ResponseSchema[CompanySchema].from_error(
                        message="创建公司失败", status=400
                    ),
                    400,
                )
                
        return make_api_response(ResponseSchema[CompanySchema](data=result))
        
    except ValidationError:
        return make_api_response(
            ResponseSchema[CompanySchema].from_error(
                message="无效的请求数据", status=400
            ),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[CompanySchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Company creation/update failed: {e}")
        return make_api_response(
            ResponseSchema[CompanySchema].from_error(message="服务器错误", status=500),
            500,
        )


# 定义分页结果模型用于API响应
class PaginationSchema:
    def __init__(self, items: List[CompanySchema], total: int, page: int, limit: int):
        self.items = items
        self.total = total
        self.page = page
        self.limit = limit


@bp.route("/list", methods=["GET"])
@login_required
def get_company_list() -> Response:
    """获取公司列表
    
    支持分页查询
    
    Returns:
        Response: 包含公司列表的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 获取分页参数
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        
        # 创建公司服务实例
        service = CompanyService(session=db.session, account=user)
        
        # 使用新的分页查询方法
        items, total = service.get_companies_paginated(page=page, limit=limit)
        
        # 构建分页响应
        pagination = PaginationSchema(
            items=items,
            total=total,
            page=page,
            limit=limit,
        )
        
        return make_api_response(
            ResponseSchema[PaginationSchema](data=pagination)
        )
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PaginationSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get company list failed: {e}")
        return make_api_response(
            ResponseSchema[PaginationSchema].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/search", methods=["GET"])
@login_required
def search_companies() -> Response:
    """搜索公司
    
    按名称搜索公司，支持分页
    
    Returns:
        Response: 包含匹配公司列表的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 获取搜索参数
        name = request.args.get("name", "")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        
        # 创建公司服务实例
        service = CompanyService(session=db.session, account=user)
        
        # 使用新的搜索方法
        items, total = service.search_companies_by_name(
            name=name, page=page, limit=limit
        )
        
        # 构建分页响应
        pagination = PaginationSchema(
            items=items,
            total=total,
            page=page,
            limit=limit,
        )
        
        return make_api_response(
            ResponseSchema[PaginationSchema](data=pagination)
        )
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PaginationSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Search companies failed: {e}")
        return make_api_response(
            ResponseSchema[PaginationSchema].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/<int:company_id>", methods=["GET"])
@login_required
def get_company_detail(company_id: int) -> Response:
    """获取公司详情
    
    Returns:
        Response: 包含公司详情的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建公司服务实例
        service = CompanyService(session=db.session, account=user)
        
        # 查询公司
        company = service.query_company_by(company_id=company_id)
        if not company:
            return make_api_response(
                ResponseSchema[CompanySchema].from_error(message="公司不存在", status=404),
                404,
            )
            
        # 转换为API响应模型
        result = CompanySchema.model_validate(company)
        return make_api_response(ResponseSchema[CompanySchema](data=result))
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[CompanySchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get company detail failed: {e}")
        return make_api_response(
            ResponseSchema[CompanySchema].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/<int:company_id>", methods=["DELETE"])
@login_required
def delete_company_endpoint(company_id: int) -> Response:
    """删除公司
    
    Returns:
        Response: 删除操作结果的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建公司服务实例
        service = CompanyService(session=db.session, account=user)
        
        # 删除公司
        success = service.delete_company(company_id=company_id)
        if not success:
            return make_api_response(
                ResponseSchema[None].from_error(
                    message="删除失败，公司不存在或无权限", status=404
                ),
                404,
            )
            
        return make_api_response(ResponseSchema[None](data=None))
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Delete company failed: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="服务器错误", status=500),
            500,
        )