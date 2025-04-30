from flask import Blueprint, request, Response, current_app
from flask_login import current_user, login_required
from typing import Optional
from pydantic import ValidationError

from libs.schema.http import ResponseSchema, make_api_response
from libs.schema.page import PageResponse
from extensions.ext_database import db
from services.department import (
    DepartmentService,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentSchema,
)
from services.permission import PermissionError

# 创建部门路由蓝图
department_bp = Blueprint("department", __name__, url_prefix="/department")


@department_bp.route("/insert", methods=["POST"])
@login_required
def insert_department() -> Response:
    """创建或更新部门接口
    
    当请求中包含部门ID时为更新操作，否则为创建操作
    
    Returns:
        Response: 包含部门信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 获取数据库会话
        session = db.session
        
        # 创建部门服务实例
        department_service = DepartmentService(session, user)
        
        # 获取请求数据
        data = request.json
        
        # 检查是否为更新操作（是否提供了 ID）
        if data.get("id"):
            # 验证更新数据
            department_data = DepartmentUpdate.model_validate(data)
            # 调用更新方法
            result = department_service.update_department(data["id"], department_data)
            if not result:
                return make_api_response(
                    ResponseSchema[DepartmentSchema].from_error(
                        message="更新部门失败，部门不存在或无权限", status=404
                    ),
                    404,
                )
        else:
            # 验证创建数据
            department_data = DepartmentCreate.model_validate(data)
            # 调用创建方法
            result = department_service.create_department(department_data)
            if not result:
                return make_api_response(
                    ResponseSchema[DepartmentSchema].from_error(
                        message="创建部门失败", status=400
                    ),
                    400,
                )
        
        # 返回成功响应
        return make_api_response(ResponseSchema[DepartmentSchema](data=result))
        
    except ValidationError:
        return make_api_response(
            ResponseSchema[DepartmentSchema].from_error(
                message="无效的请求数据", status=400
            ),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[DepartmentSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Department creation/update failed: {e}")
        return make_api_response(
            ResponseSchema[DepartmentSchema].from_error(message="服务器错误", status=500),
            500,
        )


@department_bp.route("/list/<int:company_id>", methods=["GET"])
@login_required
def list_department(company_id: int) -> Response:
    """获取部门列表接口
    
    返回指定公司的所有部门列表，支持分页
    
    Returns:
        Response: 包含部门列表的JSON响应和HTTP状态码
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
        
        # 获取数据库会话
        session = db.session
        
        # 创建部门服务实例
        department_service = DepartmentService(session, user)
        
        # 调用列出部门方法
        departments = department_service.list_departments(company_id)
        
        # 对结果进行分页处理
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        items = departments[start_idx:end_idx]
        total = len(departments)
        
        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1
        
        # 构建分页响应
        pagination = PageResponse(
            total_page=total_page,
            cur_page=page,
            page_size=limit,
            data=items
        )
        
        # 返回成功响应
        return make_api_response(
            ResponseSchema[PageResponse](data=pagination)
        )
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get department list failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


@department_bp.route("/search/<int:company_id>", methods=["GET"])
@login_required
def search_department(company_id: int) -> Response:
    """搜索部门接口
    
    根据名称搜索部门，支持模糊匹配和分页
    
    Returns:
        Response: 包含匹配部门列表的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 获取查询参数
        name = request.args.get("name", "")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        
        # 获取数据库会话
        session = db.session
        
        # 创建部门服务实例
        department_service = DepartmentService(session, user)
        
        # 调用搜索部门方法
        departments = department_service.search_departments(company_id, name)
        
        # 对结果进行分页处理
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        items = departments[start_idx:end_idx]
        total = len(departments)
        
        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1
        
        # 构建分页响应
        pagination = PageResponse(
            total_page=total_page,
            cur_page=page,
            page_size=limit,
            data=items
        )
        
        # 返回成功响应
        return make_api_response(
            ResponseSchema[PageResponse](data=pagination)
        )
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Search departments failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


@department_bp.route("/get/<int:department_id>", methods=["GET"])
@login_required
def get_department(department_id: int) -> Response:
    """获取部门详情接口
    
    根据部门ID获取部门详细信息
    
    Returns:
        Response: 包含部门详情的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 获取数据库会话
        session = db.session
        
        # 创建部门服务实例
        department_service = DepartmentService(session, user)
        
        # 调用查询部门方法
        department = department_service.query_department_by_id(department_id)
        
        # 检查是否找到部门
        if not department:
            return make_api_response(
                ResponseSchema[DepartmentSchema].from_error(message="部门不存在", status=404),
                404,
            )
        
        # 将数据库模型转换为响应模型
        result = DepartmentSchema.model_validate(department)
        
        # 返回成功响应
        return make_api_response(ResponseSchema[DepartmentSchema](data=result))
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[DepartmentSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get department detail failed: {e}")
        return make_api_response(
            ResponseSchema[DepartmentSchema].from_error(message="服务器错误", status=500),
            500,
        )


@department_bp.route("/delete/<int:department_id>", methods=["POST"])
@login_required
def delete_department(department_id: int) -> Response:
    """删除部门接口
    
    根据部门ID删除部门
    
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
        
        # 获取数据库会话
        session = db.session
        
        # 创建部门服务实例
        department_service = DepartmentService(session, user)
        
        # 调用删除部门方法
        result = department_service.delete_department(department_id)
        
        # 检查删除是否成功
        if not result:
            return make_api_response(
                ResponseSchema[None].from_error(
                    message="删除失败，部门不存在或无权限", status=404
                ),
                404,
            )
            
        # 返回成功响应
        return make_api_response(ResponseSchema[None](data=None, message="部门删除成功"))
        
    except ValueError as e:
        # 返回业务逻辑错误
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=400),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Delete department failed: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="服务器错误", status=500),
            500,
        )