"""
自定义字段值相关API路由
用于自定义字段值的创建、查询、更新和删除操作
"""

from flask import request, Response, current_app
from flask_login import current_user, login_required
from typing import List

from extensions.ext_database import db
from libs.schema.http import ResponseSchema, make_api_response
from services.customfield import (
    JsonValueCreate,
    JsonValueUpdate,
    JsonValueSchema,
    CustomFieldService,
)
from services.customfield.validator import ValidationError
from services.permission import PermissionError

# 导入蓝图对象
from . import bp


@bp.route("/value/create", methods=["POST"])
@login_required
def create_json_value() -> Response:
    """创建JSON值

    为实体创建自定义字段值。系统会根据关联的Schema验证提交的数据是否符合定义的结构和规则。

    请求体格式:
    {
        "schema_id": 1,
        "entity_type": "employee",
        "entity_id": 123,
        "value": {
            "emergency_contact_name": "张三",
            "emergency_contact_phone": "13800138000"
        },
        "remark": "紧急联系人信息"
    }

    Returns:
        Response: 包含值信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )

    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()

        # 创建自定义字段服务实例
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

        # 验证请求数据
        value_data = JsonValueCreate.model_validate(request.json)

        # 创建JSON值
        result = service.create_json_value(value_data)
        if not result:
            return make_api_response(
                ResponseSchema[JsonValueSchema].from_error(
                    message="创建失败，Schema不存在或无权限", status=404
                ),
                404,
            )

        return make_api_response(ResponseSchema[JsonValueSchema](data=result))

    except ValidationError as e:
        return make_api_response(
            ResponseSchema[JsonValueSchema].from_error(message=str(e), status=400),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[JsonValueSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Create JSON value failed: {e}")
        return make_api_response(
            ResponseSchema[JsonValueSchema].from_error(
                message="服务器错误", status=500
            ),
            500,
        )


@bp.route("/value/update/<int:value_id>", methods=["POST"])
@login_required
def update_json_value(value_id: int) -> Response:
    """更新JSON值

    更新现有的JSON值。系统会根据关联的Schema验证提交的数据是否符合定义的结构和规则。

    Args:
        value_id: 要更新的值ID

    请求体格式:
    {
        "value": {
            "emergency_contact_name": "李四",
            "emergency_contact_phone": "13900139000"
        },
        "remark": "更新后的紧急联系人信息"
    }

    Returns:
        Response: 包含更新后值信息的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )

    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()

        # 创建自定义字段服务实例
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

        # 验证请求数据
        value_data = JsonValueUpdate.model_validate(request.json)

        # 更新JSON值
        result = service.update_json_value(value_id, value_data)
        if not result:
            return make_api_response(
                ResponseSchema[JsonValueSchema].from_error(
                    message="更新失败，值不存在或无权限", status=404
                ),
                404,
            )

        return make_api_response(ResponseSchema[JsonValueSchema](data=result))

    except ValidationError as e:
        return make_api_response(
            ResponseSchema[JsonValueSchema].from_error(message=str(e), status=400),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[JsonValueSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Update JSON value failed: {e}")
        return make_api_response(
            ResponseSchema[JsonValueSchema].from_error(
                message="服务器错误", status=500
            ),
            500,
        )


@bp.route("/value/delete/<int:value_id>", methods=["POST"])
@login_required
def delete_json_value(value_id: int) -> Response:
    """删除JSON值

    删除现有的JSON值。

    Args:
        value_id: 要删除的值ID

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

        # 创建自定义字段服务实例
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

        # 删除JSON值
        success = service.delete_json_value(value_id)
        if not success:
            return make_api_response(
                ResponseSchema[None].from_error(
                    message="删除失败，值不存在或无权限", status=404
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
        current_app.logger.error(f"Delete JSON value failed: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/value/entity/<string:entity_type>/<int:entity_id>", methods=["GET"])
@login_required
def get_entity_values(entity_type: str, entity_id: int) -> Response:
    """获取实体的所有自定义字段值

    获取指定实体（如特定的员工、公司等）的所有自定义字段值。
    结果包括所有关联的Schema和值信息。

    Args:
        entity_type: 实体类型，如employee、company等
        entity_id: 实体ID

    Returns:
        Response: 包含实体所有自定义字段值的JSON响应和HTTP状态码
    """
    if not current_user:
        return make_api_response(
            ResponseSchema[None].from_error(message="未登录", status=401),
            401,
        )

    try:
        # 获取当前登录用户实例
        user = current_user._get_current_object()

        # 创建自定义字段服务实例
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

        # 获取实体的所有JSON值
        values = service.get_json_values(entity_type, entity_id)

        # 转换为API响应模型
        results = [JsonValueSchema.model_validate(value) for value in values]
        return make_api_response(ResponseSchema[List[JsonValueSchema]](data=results))

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[List[JsonValueSchema]].from_error(
                message=str(e), status=403
            ),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Get entity values failed: {e}")
        return make_api_response(
            ResponseSchema[List[JsonValueSchema]].from_error(
                message="服务器错误", status=500
            ),
            500,
        )
