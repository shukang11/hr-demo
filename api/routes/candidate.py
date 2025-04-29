from flask import Blueprint, request, Response, current_app
from flask_login import current_user, login_required
from typing import Optional
from pydantic import ValidationError

from libs.schema.http import ResponseSchema, make_api_response
from libs.schema.page import PageResponse
from extensions.ext_database import db
from services.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateStatusUpdate,
    CandidateSchema,
    CandidateStatus,
    CandidateService
)
from services.permission import PermissionError

# 创建候选人相关的蓝图
bp = Blueprint("candidate", __name__, url_prefix="/candidate")


@bp.route("/insert", methods=["POST"])
@login_required
def insert_candidate() -> Response:
    """创建或更新候选人
    
    如果请求数据中包含id字段，则更新现有候选人；否则创建新候选人。
    
    Returns:
        Response: 包含候选人信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建候选人服务实例
        service = CandidateService(session=db.session, account=user)
        
        # 获取请求数据
        request_data = request.json
        candidate_id = request_data.get("id")
        
        if candidate_id:
            # 更新现有候选人
            candidate_data = CandidateUpdate.model_validate(request_data)
            result = service.update_candidate(candidate_id, candidate_data)
            if not result:
                return make_api_response(
                    ResponseSchema[CandidateSchema].from_error(
                        message="更新候选人失败，候选人不存在或无权限", status=404
                    ),
                    404,
                )
        else:
            # 创建新候选人
            candidate_data = CandidateCreate.model_validate(request_data)
            result = service.create_candidate(candidate_data)
            if not result:
                return make_api_response(
                    ResponseSchema[CandidateSchema].from_error(
                        message="创建候选人失败", status=400
                    ),
                    400,
                )
                
        return make_api_response(ResponseSchema[CandidateSchema](data=result))
        
    except ValidationError as e:
        return make_api_response(
            ResponseSchema[CandidateSchema].from_error(
                message=f"无效的请求数据: {e}", status=400
            ),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[CandidateSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Candidate creation/update failed: {e}")
        return make_api_response(
            ResponseSchema[CandidateSchema].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/<int:candidate_id>/status", methods=["POST"])
@login_required
def update_candidate_status(candidate_id: int) -> Response:
    """更新候选人状态
    
    更新候选人的状态、评价和备注信息
    
    Args:
        candidate_id: 候选人ID
    
    Returns:
        Response: 包含更新后候选人信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建候选人服务实例
        service = CandidateService(session=db.session, account=user)
        
        # 验证请求数据
        status_data = CandidateStatusUpdate.model_validate(request.json)
        
        # 更新候选人状态
        result = service.update_candidate_status(candidate_id, status_data)
        if not result:
            return make_api_response(
                ResponseSchema[CandidateSchema].from_error(
                    message="更新候选人状态失败，候选人不存在或无权限", status=404
                ),
                404,
            )
            
        return make_api_response(ResponseSchema[CandidateSchema](data=result))
        
    except ValidationError:
        return make_api_response(
            ResponseSchema[CandidateSchema].from_error(
                message="无效的请求数据", status=400
            ),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[CandidateSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Candidate status update failed: {e}")
        return make_api_response(
            ResponseSchema[CandidateSchema].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/list/<int:company_id>", methods=["GET"])
@login_required
def list_candidates(company_id: int) -> Response:
    """获取候选人列表
    
    获取指定公司的候选人列表，支持分页、状态筛选和搜索
    
    Args:
        company_id: 公司ID
    
    Returns:
        Response: 包含候选人列表的JSON响应和HTTP状态码
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
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        status_str = request.args.get("status")
        search = request.args.get("search")
        
        # 解析状态参数
        status: Optional[CandidateStatus] = None
        if status_str:
            try:
                status = CandidateStatus(status_str)
            except ValueError:
                return make_api_response(
                    ResponseSchema[PageResponse].from_error(
                        message=f"无效的状态值: {status_str}", status=400
                    ),
                    400,
                )
        
        # 创建候选人服务实例
        service = CandidateService(session=db.session, account=user)
        
        # 获取候选人列表
        items, total = service.get_candidates_by_company(
            company_id=company_id,
            page=page,
            limit=limit,
            status=status,
            search=search
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
        current_app.logger.error(f"Get candidate list failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/get/<int:candidate_id>", methods=["GET"])
@login_required
def get_candidate(candidate_id: int) -> Response:
    """获取候选人详情
    
    Args:
        candidate_id: 候选人ID
    
    Returns:
        Response: 包含候选人详情的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )
        
    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()
        
        # 创建候选人服务实例
        service = CandidateService(session=db.session, account=user)
        
        # 查询候选人
        candidate = service.query_candidate_by_id(candidate_id)
        if not candidate:
            return make_api_response(
                ResponseSchema[CandidateSchema].from_error(message="候选人不存在", status=404),
                404,
            )
            
        # 转换为API响应模型
        result = CandidateSchema.model_validate(candidate)
        return make_api_response(ResponseSchema[CandidateSchema](data=result))
        
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[CandidateSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get candidate detail failed: {e}")
        return make_api_response(
            ResponseSchema[CandidateSchema].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/delete/<int:candidate_id>", methods=["POST"])
@login_required
def delete_candidate(candidate_id: int) -> Response:
    """删除候选人
    
    Args:
        candidate_id: 候选人ID
    
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
        
        # 创建候选人服务实例
        service = CandidateService(session=db.session, account=user)
        
        # 删除候选人
        success = service.delete_candidate(candidate_id)
        if not success:
            return make_api_response(
                ResponseSchema[None].from_error(
                    message="删除失败，候选人不存在或无权限", status=404
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
        current_app.logger.error(f"Delete candidate failed: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="服务器错误", status=500),
            500,
        )