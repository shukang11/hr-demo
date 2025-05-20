"""
自定义字段高级功能API路由
包含Schema迁移、自定义字段搜索等高级功能
"""

from flask import request, Response, current_app
from flask_login import current_user, login_required
from typing import Dict, Any

from extensions.ext_database import db
from libs.schema.http import ResponseSchema, make_api_response
from libs.schema.page import PageResponse
from services.customfield import (
    CustomFieldService,
)
from services.customfield.validator import ValidationError
from services.permission import PermissionError

# 导入蓝图对象
from . import bp


# 高级查询功能
@bp.route("/search", methods=["POST"])
@login_required
def search_by_custom_field() -> Response:
    """根据自定义字段值搜索实体

    根据自定义字段的值搜索符合条件的实体（如员工、公司等）。
    支持多条件组合查询和复杂的查询条件。

    请求体格式:
    {
        "entity_type": "employee",
        "conditions": [
            {
                "schema_id": 1,
                "operator": "eq",
                "value": "张三"
            },
            {
                "schema_id": 2,
                "operator": "contains",
                "value": "北京"
            }
        ],
        "logic": "and",
        "page": 1,
        "limit": 10
    }

    Returns:
        Response: 包含符合条件的实体ID列表的JSON响应和HTTP状态码
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

        # 解析查询条件
        query_data: dict = request.json  # type: ignore
        entity_type = query_data.get("entity_type")
        conditions = query_data.get("conditions", [])
        logic = query_data.get("logic", "and")
        page = int(query_data.get("page", 1))
        limit = int(query_data.get("limit", 10))

        # 验证必要参数
        if not entity_type:
            return make_api_response(
                ResponseSchema[PageResponse].from_error(
                    message="缺少entity_type参数", status=400
                ),
                400,
            )

        if not conditions:
            return make_api_response(
                ResponseSchema[PageResponse].from_error(
                    message="缺少conditions参数", status=400
                ),
                400,
            )

        # 执行搜索
        results, total = service.search_entities_by_custom_field(
            entity_type, conditions, logic, page, limit
        )

        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1

        # 构建分页响应
        pagination = PageResponse(
            total_page=total_page, cur_page=page, page_size=limit, data=results
        )

        return make_api_response(ResponseSchema[PageResponse](data=pagination))

    except ValidationError as e:
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message=str(e), status=400),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Search by custom field failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


# Schema迁移功能
@bp.route("/schema/migrate", methods=["POST"])
@login_required
def migrate_schema() -> Response:
    """迁移JSON Schema

    在现有数据基础上迁移Schema结构，系统会为符合条件的数据按新的Schema生成对应的值。
    适用于Schema结构变更较大，且需要保留已有数据的情况。

    请求体格式:
    {
        "source_schema_id": 1,
        "target_schema_id": 2,
        "mapping": {
            "old_field_name": "new_field_name",
            "another_old_field": "another_new_field"
        },
        "default_values": {
            "new_required_field": "default_value"
        }
    }

    Returns:
        Response: 迁移操作结果的JSON响应和HTTP状态码
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

        # 解析迁移参数
        migrate_data: dict = request.json  # type: ignore
        source_schema_id = migrate_data.get("source_schema_id")
        target_schema_id = migrate_data.get("target_schema_id")
        field_mapping = migrate_data.get("mapping", {})

        # 验证必要参数
        if not source_schema_id or not target_schema_id:
            return make_api_response(
                ResponseSchema[None].from_error(
                    message="缺少source_schema_id或target_schema_id参数", status=400
                ),
                400,
            )

        # 执行迁移
        migrated_count = service.migrate_schema(
            source_schema_id, target_schema_id, field_mapping
        )

        # 返回迁移结果
        return make_api_response(
            ResponseSchema[Dict[str, Any]](
                data={"migrated_count": migrated_count, "success": True}
            )
        )

    except ValidationError as e:
        return make_api_response(
            ResponseSchema[None].from_error(message=str(e), status=400),
            400,
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
        current_app.logger.error(f"Migrate schema failed: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="服务器错误", status=500),
            500,
        )
