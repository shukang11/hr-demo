from flask import Blueprint, request, Response, current_app
from flask_login import current_user, login_required
from typing import List
from pydantic import ValidationError

from libs.schema.http import ResponseSchema, make_api_response
from libs.schema.page import PageResponse
from extensions.ext_database import db
from services.position import PositionService
from services.position._schema import PositionCreate, PositionUpdate, PositionSchema
from services.permission import PermissionError

# 创建职位相关的蓝图
bp = Blueprint("position", __name__, url_prefix="/position")


@bp.route("/create", methods=["POST"])
@login_required
def create_position() -> Response:
    """创建或更新职位
    
    如果请求数据中包含id字段，则更新现有职位；否则创建新职位。
    
    Returns:
        Response: 包含职位信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建职位服务实例
        service = PositionService(session=db.session, account=user)
        
        # 获取请求数据
        request_data = request.json
        position_id = request_data.get("id")
        
        if position_id:
            # 更新现有职位
            position_data = PositionUpdate.model_validate(request_data)
            result = service.update_position(position_id, position_data)
            if not result:
                return make_api_response(
                    ResponseSchema[PositionSchema].from_error(
                        message="更新职位失败，职位不存在或无权限", status=404
                    ),
                    404,
                )
        else:
            # 创建新职位
            position_data = PositionCreate.model_validate(request_data)
            result = service.create_position(position_data)
            if not result:
                return make_api_response(
                    ResponseSchema[PositionSchema].from_error(
                        message="创建职位失败", status=400
                    ),
                    400,
                )
                
        return make_api_response(ResponseSchema[PositionSchema](data=result))
        
    except ValidationError:
        return make_api_response(
            ResponseSchema[PositionSchema].from_error(
                message="无效的请求数据", status=400
            ),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PositionSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Position creation/update failed: {e}")
        return make_api_response(
            ResponseSchema[PositionSchema].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/list/<int:company_id>", methods=["GET"])
@login_required
def list_positions(company_id: int) -> Response:
    """获取职位列表
    
    获取指定公司的所有职位，支持分页
    
    Returns:
        Response: 包含职位列表的JSON响应和HTTP状态码
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
        
        # 创建职位服务实例
        service = PositionService(session=db.session, account=user)
        
        # 获取职位列表
        positions = service.list_positions(company_id)
        
        # 简单的内存分页 (实际项目中应考虑数据库级分页)
        start_index = (page - 1) * limit
        end_index = start_index + limit
        items = positions[start_index:end_index]
        total = len(positions)
        
        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1
        
        # 构建分页响应 - 使用 PageResponse 替代 PaginationSchema
        pagination = PageResponse(
            total_page=total_page,
            cur_page=page,
            page_size=limit,
            data=items
        )
        
        return make_api_response(
            ResponseSchema[PageResponse](data=pagination)
        )
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get position list failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/search/<int:company_id>", methods=["GET"])
@login_required
def search_positions(company_id: int) -> Response:
    """搜索职位
    
    根据名称搜索职位，支持分页
    
    Returns:
        Response: 包含匹配职位列表的JSON响应和HTTP状态码
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
        
        # 创建职位服务实例
        service = PositionService(session=db.session, account=user)
        
        # 先获取所有职位列表
        all_positions = service.list_positions(company_id)
        
        # 按名称过滤
        filtered_positions = [
            p for p in all_positions if name.lower() in p.name.lower()
        ]
        
        # 简单的内存分页
        start_index = (page - 1) * limit
        end_index = start_index + limit
        items = filtered_positions[start_index:end_index]
        total = len(filtered_positions)
        
        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1
        
        # 构建分页响应 - 使用 PageResponse 替代 PaginationSchema
        pagination = PageResponse(
            total_page=total_page,
            cur_page=page,
            page_size=limit,
            data=items
        )
        
        return make_api_response(
            ResponseSchema[PageResponse](data=pagination)
        )
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Search positions failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/get/<int:position_id>", methods=["GET"])
@login_required
def get_position(position_id: int) -> Response:
    """获取职位详情
    
    Returns:
        Response: 包含职位详情的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建职位服务实例
        service = PositionService(session=db.session, account=user)
        
        # 查询职位
        position = service.query_position_by_id(position_id)
        if not position:
            return make_api_response(
                ResponseSchema[PositionSchema].from_error(message="职位不存在", status=404),
                404,
            )
            
        # 将数据库对象转换为API响应模型
        result = PositionSchema.model_validate(position)
        return make_api_response(ResponseSchema[PositionSchema](data=result))
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PositionSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get position detail failed: {e}")
        return make_api_response(
            ResponseSchema[PositionSchema].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/delete/<int:position_id>", methods=["POST"])
@login_required
def delete_position(position_id: int) -> Response:
    """删除职位
    
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
        
        # 创建职位服务实例
        service = PositionService(session=db.session, account=user)
        
        # 删除职位
        success = service.delete_position(position_id)
        if not success:
            return make_api_response(
                ResponseSchema[None].from_error(
                    message="删除失败，职位不存在或无权限", status=404
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
        current_app.logger.error(f"Delete position failed: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="服务器错误", status=500),
            500,
        )