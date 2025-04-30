from flask import Blueprint, request, Response, current_app
from flask_login import current_user, login_required
from typing import List, Optional, Dict, Any

from libs.schema.http import ResponseSchema, make_api_response
from libs.schema.page import PageResponse
from extensions.ext_database import db
from services.employee import (
    EmployeeService,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeSchema,
    EmployeePositionCreate,
    EmployeePositionSchema,
    Gender
)
from services.permission import PermissionError

# 创建员工相关的蓝图
employee_bp = Blueprint("employee", __name__, url_prefix="/employee")


@employee_bp.route("/insert", methods=["POST"])
@login_required
def insert_employee() -> Response:
    """创建或更新员工
    
    如果请求数据中包含id字段，则更新现有员工；否则创建新员工。
    
    Returns:
        Response: 包含员工信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 获取请求数据
        request_data = request.json
        employee_id = request_data.get("id")
        
        # 处理性别字段 - 前端传入的是字符串枚举
        if "gender" in request_data and request_data.get("gender") is not None:
            # 如果前端没有指定性别，则默认为未知
            gender_str = request_data.get("gender", "Unknown")
            request_data["gender"] = Gender(gender_str)
        
        if employee_id:
            # 更新现有员工
            employee_data = EmployeeUpdate.model_validate(request_data)
            result = service.update_employee(employee_id, employee_data)
            if not result:
                return make_api_response(
                    ResponseSchema[EmployeeSchema].from_error(
                        message="更新员工失败，员工不存在或无权限", status=404
                    ),
                    404,
                )
        else:
            # 创建新员工
            employee_data = EmployeeCreate.model_validate(request_data)
            result = service.create_employee(employee_data)
            if not result:
                return make_api_response(
                    ResponseSchema[EmployeeSchema].from_error(
                        message="创建员工失败", status=400
                    ),
                    400,
                )
                
        return make_api_response(ResponseSchema[EmployeeSchema](data=result))
        
    except ValueError as e:
        current_app.logger.error(f"Insert employee validation error: {e}")
        return make_api_response(
            ResponseSchema[EmployeeSchema].from_error(
                message=f"无效的请求数据: {str(e)}", status=400
            ),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[EmployeeSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Insert employee failed: {e}")
        return make_api_response(
            ResponseSchema[EmployeeSchema].from_error(message="服务器错误", status=500),
            500,
        )


@employee_bp.route("/list/<int:company_id>", methods=["GET"])
@login_required
def get_employee_list(company_id: int) -> Response:
    """获取公司员工列表
    
    支持分页查询
    
    Returns:
        Response: 包含员工列表的JSON响应和HTTP状态码
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
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 使用分页查询方法
        items, total = service.get_employee_list(
            company_id=company_id, page=page, limit=limit
        )
        
        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1
        
        # 构建分页响应
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
        current_app.logger.error(f"Get employee list failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


@employee_bp.route("/list/department/<int:department_id>", methods=["GET"])
@login_required
def get_employees_by_department(department_id: int) -> Response:
    """获取部门员工列表
    
    支持分页查询
    
    Returns:
        Response: 包含员工列表的JSON响应和HTTP状态码
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
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 使用分页查询方法
        items, total = service.get_employees_by_department(
            department_id=department_id, page=page, limit=limit
        )
        
        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1
        
        # 构建分页响应
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
        current_app.logger.error(f"Get department employees failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


@employee_bp.route("/search/<int:company_id>", methods=["GET"])
@login_required
def search_employees(company_id: int) -> Response:
    """搜索员工
    
    按名称搜索员工，支持分页
    
    Returns:
        Response: 包含匹配员工列表的JSON响应和HTTP状态码
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
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 使用搜索方法
        items, total = service.search_employees(
            company_id=company_id, name=name, page=page, limit=limit
        )
        
        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1
        
        # 构建分页响应
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
        current_app.logger.error(f"Search employees failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


@employee_bp.route("/get/<int:employee_id>", methods=["GET"])
@login_required
def get_employee_detail(employee_id: int) -> Response:
    """获取员工详情
    
    Returns:
        Response: 包含员工详情的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 查询员工
        employee = service.query_employee_by_id(employee_id)
        if not employee:
            return make_api_response(
                ResponseSchema[EmployeeSchema].from_error(message="员工不存在", status=404),
                404,
            )
            
        # 转换为API响应模型
        result = EmployeeSchema.model_validate(employee)
        return make_api_response(ResponseSchema[EmployeeSchema](data=result))
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[EmployeeSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get employee detail failed: {e}")
        return make_api_response(
            ResponseSchema[EmployeeSchema].from_error(message="服务器错误", status=500),
            500,
        )


@employee_bp.route("/delete/<int:employee_id>", methods=["POST"])
@login_required
def delete_employee_endpoint(employee_id: int) -> Response:
    """删除员工
    
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
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 删除员工
        success = service.delete_employee(employee_id=employee_id)
        if not success:
            return make_api_response(
                ResponseSchema[None].from_error(
                    message="删除失败，员工不存在或无权限", status=404
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
        current_app.logger.error(f"Delete employee failed: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="服务器错误", status=500),
            500,
        )


# 员工职位关联接口

@employee_bp.route("/position/add", methods=["POST"])
@login_required
def add_employee_position() -> Response:
    """为员工添加职位
    
    Returns:
        Response: 包含职位关联信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 获取请求数据
        request_data = request.json
        
        # 创建职位关联
        position_data = EmployeePositionCreate.model_validate(request_data)
        result = service.add_employee_position(position_data)
        if not result:
            return make_api_response(
                ResponseSchema[EmployeePositionSchema].from_error(
                    message="添加职位失败", status=400
                ),
                400,
            )
                
        return make_api_response(ResponseSchema[EmployeePositionSchema](data=result))
        
    except ValueError as e:
        return make_api_response(
            ResponseSchema[EmployeePositionSchema].from_error(
                message=f"无效的请求数据: {str(e)}", status=400
            ),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[EmployeePositionSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Add employee position failed: {e}")
        return make_api_response(
            ResponseSchema[EmployeePositionSchema].from_error(message="服务器错误", status=500),
            500,
        )


@employee_bp.route("/position/remove/<int:position_id>", methods=["POST"])
@login_required
def remove_employee_position(position_id: int) -> Response:
    """移除员工职位关联
    
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
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 删除职位关联
        success = service.remove_employee_position(position_id=position_id)
        if not success:
            return make_api_response(
                ResponseSchema[None].from_error(
                    message="移除失败，职位关联不存在或无权限", status=404
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
        current_app.logger.error(f"Remove employee position failed: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="服务器错误", status=500),
            500,
        )


@employee_bp.route("/position/list/<int:employee_id>", methods=["GET"])
@login_required
def get_employee_positions(employee_id: int) -> Response:
    """获取员工职位列表
    
    Returns:
        Response: 包含职位关联列表的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 获取职位关联列表
        positions = service.get_employee_positions(employee_id=employee_id)
            
        return make_api_response(
            ResponseSchema[List[EmployeePositionSchema]](data=positions)
        )
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[List[EmployeePositionSchema]].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get employee positions failed: {e}")
        return make_api_response(
            ResponseSchema[List[EmployeePositionSchema]].from_error(message="服务器错误", status=500),
            500,
        )


@employee_bp.route("/position/<int:employee_id>", methods=["GET"])
@login_required
def get_employee_current_position(employee_id: int) -> Response:
    """获取员工当前职位
    
    Returns:
        Response: 包含当前职位关联信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 获取当前职位关联
        position = service.get_employee_current_position(employee_id=employee_id)
        if not position:
            return make_api_response(
                ResponseSchema[EmployeePositionSchema].from_error(message="员工无职位关联", status=404),
                404,
            )
            
        # 转换为API响应模型
        result = EmployeePositionSchema.model_validate(position)
        return make_api_response(
            ResponseSchema[EmployeePositionSchema](data=result)
        )
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[EmployeePositionSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get employee current position failed: {e}")
        return make_api_response(
            ResponseSchema[EmployeePositionSchema].from_error(message="服务器错误", status=500),
            500,
        )


@employee_bp.route("/position/history/<int:employee_id>", methods=["GET"])
@login_required
def get_employee_position_history(employee_id: int) -> Response:
    """获取员工职位历史
    
    Returns:
        Response: 包含职位历史列表的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建员工服务实例
        service = EmployeeService(session=db.session, account=user)
        
        # 获取职位历史列表
        positions = service.get_employee_position_history(employee_id=employee_id)
            
        return make_api_response(
            ResponseSchema[List[EmployeePositionSchema]](data=positions)
        )
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[List[EmployeePositionSchema]].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get employee position history failed: {e}")
        return make_api_response(
            ResponseSchema[List[EmployeePositionSchema]].from_error(message="服务器错误", status=500),
            500,
        )