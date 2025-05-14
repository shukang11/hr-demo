from flask import Blueprint, request, Response, current_app, jsonify
from flask_login import current_user, login_required
from typing import List, Optional

from libs.schema.http import ResponseSchema, make_api_response
from libs.helper import get_date_from_time_tuple
from extensions.ext_database import db
from services.dashboard import (
    DashboardService,
    EmployeeOverview,
    RecruitmentStats,
    OrganizationStats,
    DashboardStats,
    BirthdayEmployee,
)
from services.permission import PermissionError

# 创建看板相关的蓝图
bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.route("/stats/<int:company_id>", methods=["GET"])
@login_required
def get_dashboard_stats(company_id: int) -> Response:
    """获取看板完整统计数据

    Args:
        company_id: 公司ID

    Returns:
        Response: 包含看板统计数据的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )

    try:
        # 获取请求参数
        start_time = int(request.args.get("start_time", 0))
        end_time = int(request.args.get("end_time", 0))

        # 获取当前登录用户实例
        user = current_user._get_current_object()

        # 创建看板服务实例
        service = DashboardService(session=db.session, account=user)

        # 获取看板统计数据
        stats = service.get_dashboard_stats(company_id, start_time, end_time)

        # 返回成功响应
        return make_api_response(
            ResponseSchema[DashboardStats].from_success(
                data=stats,
                message="获取看板统计数据成功",
            )
        )

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=403),
            403,
        )
    except ValueError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=400),
            400,
        )
    except Exception as e:
        current_app.logger.error(f"获取看板统计数据失败: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="获取看板统计数据失败", status=500),
            500,
        )


@bp.route("/employee-overview/<int:company_id>", methods=["GET"])
@login_required
def get_employee_overview(company_id: int) -> Response:
    """获取员工概览数据

    Args:
        company_id: 公司ID

    Returns:
        Response: 包含员工概览数据的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )

    try:
        # 获取请求参数
        start_time = int(request.args.get("start_time", 0))
        end_time = int(request.args.get("end_time", 0))

        # 获取当前登录用户实例
        user = current_user._get_current_object()

        # 创建看板服务实例
        service = DashboardService(session=db.session, account=user)

        # 获取员工概览数据
        overview = service.get_employee_overview(company_id, start_time, end_time)

        # 返回成功响应
        return make_api_response(
            ResponseSchema[EmployeeOverview].from_success(
                data=overview,
                message="获取员工概览数据成功",
            )
        )

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=403),
            403,
        )
    except ValueError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=400),
            400,
        )
    except Exception as e:
        current_app.logger.error(f"获取员工概览数据失败: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="获取员工概览数据失败", status=500),
            500,
        )


@bp.route("/recruitment-stats/<int:company_id>", methods=["GET"])
@login_required
def get_recruitment_stats(company_id: int) -> Response:
    """获取招聘统计数据

    Args:
        company_id: 公司ID

    Returns:
        Response: 包含招聘统计数据的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )

    try:
        # 获取请求参数
        start_time = int(request.args.get("start_time", 0))
        end_time = int(request.args.get("end_time", 0))

        # 获取当前登录用户实例
        user = current_user._get_current_object()

        # 创建看板服务实例
        service = DashboardService(session=db.session, account=user)

        # 获取招聘统计数据
        stats = service.get_recruitment_stats(company_id, start_time, end_time)

        # 返回成功响应
        return make_api_response(
            ResponseSchema[RecruitmentStats].from_success(
                data=stats,
                message="获取招聘统计数据成功",
            )
        )

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=403),
            403,
        )
    except ValueError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=400),
            400,
        )
    except Exception as e:
        current_app.logger.error(f"获取招聘统计数据失败: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="获取招聘统计数据失败", status=500),
            500,
        )


@bp.route("/organization-stats/<int:company_id>", methods=["GET"])
@login_required
def get_organization_stats(company_id: int) -> Response:
    """获取组织发展统计数据

    Args:
        company_id: 公司ID

    Returns:
        Response: 包含组织发展统计数据的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )

    try:
        # 获取请求参数
        start_time = int(request.args.get("start_time", 0))
        end_time = int(request.args.get("end_time", 0))

        # 获取当前登录用户实例
        user = current_user._get_current_object()

        # 创建看板服务实例
        service = DashboardService(session=db.session, account=user)

        # 获取组织发展统计数据
        stats = service.get_organization_stats(company_id, start_time, end_time)

        # 返回成功响应
        return make_api_response(
            ResponseSchema[OrganizationStats].from_success(
                data=stats,
                message="获取组织发展统计数据成功",
            )
        )

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=403),
            403,
        )
    except ValueError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=400),
            400,
        )
    except Exception as e:
        current_app.logger.error(f"获取组织发展统计数据失败: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(
                message="获取组织发展统计数据失败", status=500
            ),
            500,
        )


@bp.route("/birthday-employees/<int:company_id>", methods=["GET"])
@login_required
def get_birthday_employees(company_id: int) -> Response:
    """获取指定时间范围内过生日的员工

    Args:
        company_id: 公司ID

    Returns:
        Response: 包含过生日员工列表的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )

    try:
        # 获取请求参数
        start_time = int(request.args.get("start_time", 0))
        end_time = int(request.args.get("end_time", 0))

        # 获取当前登录用户实例
        user = current_user._get_current_object()

        # 创建看板服务实例
        service = DashboardService(session=db.session, account=user)

        # 获取过生日员工列表
        employees = service.get_birthday_employees(company_id, start_time, end_time)
        try:
            start_time_str = get_date_from_time_tuple(str(start_time))
            end_time_str = get_date_from_time_tuple(str(end_time))
            employee_infos = [
                {
                    "name": employee.name,
                    "birthday_ts": employee.birthdate,
                    "birthday": get_date_from_time_tuple(str(employee.birthdate)),
                }
                for employee in employees
            ]
            current_app.logger.info(
                f"获取过生日的员工列表，参数: company_id={company_id}, start_time={start_time_str}, end_time={end_time_str} employees={employee_infos}"
            )
        except Exception as e:
            current_app.logger.error(f"获取过生日的员工列表失败: {e}")
        # 返回成功响应
        return make_api_response(
            ResponseSchema[list[BirthdayEmployee]].from_success(
                data=employees,
                message="获取过生日员工列表成功",
            )
        )

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=403),
            403,
        )
    except ValueError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=400),
            400,
        )
    except Exception as e:
        current_app.logger.error(f"获取过生日员工列表失败: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(
                message="获取过生日员工列表失败", status=500
            ),
            500,
        )


@bp.route("/subsidiaries-stats/<int:parent_id>", methods=["GET"])
@login_required
def get_subsidiaries_stats(parent_id: int) -> Response:
    """获取母公司及其子公司的聚合统计数据

    Args:
        parent_id: 母公司ID

    Returns:
        Response: 包含聚合统计数据的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )

    try:
        # 获取请求参数
        start_time = int(request.args.get("start_time", 0))
        end_time = int(request.args.get("end_time", 0))

        # 获取所有指定的子公司ID
        subsidiary_ids_str = request.args.get("subsidiary_ids", "")
        subsidiary_ids: List[int] = []

        if subsidiary_ids_str:
            try:
                subsidiary_ids = [
                    int(id_str) for id_str in subsidiary_ids_str.split(",") if id_str
                ]
            except ValueError:
                return make_api_response(
                    ResponseSchema[None].from_error(
                        message="子公司ID格式错误", status=400
                    ),
                    400,
                )

        # 获取当前登录用户实例
        user = current_user._get_current_object()

        # 创建看板服务实例
        service = DashboardService(session=db.session, account=user)

        # 获取子公司聚合统计数据
        stats = service.get_subsidiaries_stats(
            parent_id, subsidiary_ids, start_time, end_time
        )

        # 返回成功响应
        return make_api_response(
            ResponseSchema[DashboardStats].from_success(
                data=stats,
                message="获取子公司聚合统计数据成功",
            )
        )

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=403),
            403,
        )
    except ValueError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=400),
            400,
        )
    except Exception as e:
        current_app.logger.error(f"获取子公司聚合统计数据失败: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(
                message="获取子公司聚合统计数据失败", status=500
            ),
            500,
        )
