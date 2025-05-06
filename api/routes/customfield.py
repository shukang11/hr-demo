from flask import Blueprint, request, Response, current_app, jsonify
from flask_login import current_user, login_required
from typing import Optional, List, Dict, Any

from libs.schema.http import ResponseSchema, make_api_response
from libs.schema.page import PageResponse
from extensions.ext_database import db
from libs.models.json_schema import SchemaEntityType
from services.customfield import (
    JsonSchemaCreate,
    JsonSchemaUpdate,
    JsonSchemaSchema,
    JsonValueCreate,
    JsonValueUpdate,
    JsonValueSchema,
    JsonSchemaClone,
    CustomFieldService,
)
from services.customfield.validator import ValidationError
from services.permission import PermissionError

# 创建自定义字段相关的蓝图
bp = Blueprint("customfield", __name__, url_prefix="/customfield")


@bp.route("/schema/create", methods=["POST"])
@login_required
def create_json_schema() -> Response:
    """创建JSON Schema

    创建一个新的JSON Schema定义，用于自定义字段。Schema定义了自定义字段的结构、
    验证规则和UI呈现方式。

    请求体格式:
    {
        "name": "员工紧急联系人",
        "entity_type": "Employee",
        "company_id": 1,
        "schema": {
            "type": "object",
            "properties": {
                "emergency_contact_name": {
                    "type": "string",
                    "title": "紧急联系人姓名"
                }
            }
        },
        "ui_schema": {
            "emergency_contact_name": {
                "ui:widget": "text",
                "ui:placeholder": "请输入姓名"
            }
        },
        "remark": "用于存储员工紧急联系人信息"
    }

    Returns:
        Response: 包含Schema信息的JSON响应和HTTP状态码
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
        service = CustomFieldService(session=db.session, account=user)

        # 验证请求数据
        schema_data = JsonSchemaCreate.model_validate(request.json)

        # 创建JSON Schema
        result = service.create_json_schema(schema_data)
        if not result:
            return make_api_response(
                ResponseSchema[JsonSchemaSchema].from_error(
                    message="创建Schema失败", status=400
                ),
                400,
            )

        return make_api_response(ResponseSchema[JsonSchemaSchema](data=result))

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[JsonSchemaSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Create JSON schema failed: {e}")
        return make_api_response(
            ResponseSchema[JsonSchemaSchema].from_error(
                message="服务器错误", status=500
            ),
            500,
        )


@bp.route("/schema/update/<int:schema_id>", methods=["POST"])
@login_required
def update_json_schema(schema_id: int) -> Response:
    """更新JSON Schema

    更新现有的JSON Schema定义。如果更新涉及Schema的结构变化，
    会创建新版本的Schema并保留对旧版本的引用。如果只更新UI配置或元数据，
    则直接修改当前版本。

    Args:
        schema_id: Schema ID

    请求体格式:
    {
        "name": "更新的Schema名称",
        "schema": {
            "type": "object",
            "properties": { ... }
        },
        "ui_schema": { ... },
        "remark": "更新的备注"
    }

    Returns:
        Response: 包含更新后Schema信息的JSON响应和HTTP状态码
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
        service = CustomFieldService(session=db.session, account=user)

        # 验证请求数据
        schema_data = JsonSchemaUpdate.model_validate(request.json)

        # 更新JSON Schema
        result = service.update_json_schema(schema_id, schema_data)
        if not result:
            return make_api_response(
                ResponseSchema[JsonSchemaSchema].from_error(
                    message="更新Schema失败，Schema不存在或无权限", status=404
                ),
                404,
            )

        return make_api_response(ResponseSchema[JsonSchemaSchema](data=result))

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[JsonSchemaSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Update JSON schema failed: {e}")
        return make_api_response(
            ResponseSchema[JsonSchemaSchema].from_error(
                message="服务器错误", status=500
            ),
            500,
        )


@bp.route("/schema/delete/<int:schema_id>", methods=["POST"])
@login_required
def delete_json_schema(schema_id: int) -> Response:
    """删除JSON Schema

    删除现有的JSON Schema定义。只有当没有数据使用该Schema时才能删除。
    系统预设的Schema只能由超级管理员删除。

    Args:
        schema_id: 要删除的Schema ID

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
        service = CustomFieldService(session=db.session, account=user)

        # 删除JSON Schema
        success = service.delete_json_schema(schema_id)
        if not success:
            return make_api_response(
                ResponseSchema[None].from_error(
                    message="删除失败，Schema不存在、无权限或已有关联数据", status=404
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
        current_app.logger.error(f"Delete JSON schema failed: {e}")
        return make_api_response(
            ResponseSchema[None].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/schema/clone", methods=["POST"])
@login_required
def clone_json_schema() -> Response:
    """克隆JSON Schema

    将现有的JSON Schema克隆到另一个公司。新创建的Schema是独立的副本，
    不会受源Schema后续变更的影响。克隆的Schema版本号会重置为1，且不是系统Schema。

    请求体格式:
    {
        "source_schema_id": 1,
        "target_company_id": 2,
        "name": "克隆后的Schema名称（可选）"
    }

    Returns:
        Response: 包含新Schema信息的JSON响应和HTTP状态码
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
        service = CustomFieldService(session=db.session, account=user)

        # 验证请求数据
        clone_data = JsonSchemaClone.model_validate(request.json)

        # 克隆JSON Schema
        result = service.clone_json_schema(clone_data)
        if not result:
            return make_api_response(
                ResponseSchema[JsonSchemaSchema].from_error(
                    message="克隆Schema失败，源Schema不存在或无权限", status=404
                ),
                404,
            )

        return make_api_response(ResponseSchema[JsonSchemaSchema](data=result))

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[JsonSchemaSchema].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Clone JSON schema failed: {e}")
        return make_api_response(
            ResponseSchema[JsonSchemaSchema].from_error(
                message="服务器错误", status=500
            ),
            500,
        )


@bp.route("/schema/list/<string:entity_type>", methods=["GET"])
@login_required
def list_json_schemas(entity_type: str) -> Response:
    """获取JSON Schema列表

    获取指定实体类型的JSON Schema列表，支持分页和公司筛选。
    可选择是否包含系统预设的Schema。结果按更新时间倒序排列。

    Args:
        entity_type: 实体类型，如Employee, Candidate等

    查询参数:
        page: 页码，从1开始，默认1
        limit: 每页记录数，默认10
        company_id: 公司ID，可选。若提供，则筛选该公司的Schema
        include_system: 是否包含系统Schema，默认为true

    Returns:
        Response: 包含Schema列表的JSON响应和HTTP状态码
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
        company_id_str = request.args.get("company_id")
        include_system_str = request.args.get("include_system", "true")

        # 解析参数
        company_id = int(company_id_str) if company_id_str else None
        include_system = include_system_str.lower() == "true"

        # 添加详细日志
        current_app.logger.debug(
            f"列出JSON Schema，参数: entity_type={entity_type}, page={page}, limit={limit}, company_id={company_id}, include_system={include_system}"
        )

        # 验证实体类型
        try:
            schema_entity_type = SchemaEntityType(entity_type)
            current_app.logger.debug(f"实体类型验证通过: {schema_entity_type}")
        except ValueError:
            current_app.logger.error(f"无效的实体类型: {entity_type}")
            return make_api_response(
                ResponseSchema[PageResponse].from_error(
                    message=f"无效的实体类型: {entity_type}", status=400
                ),
                400,
            )

        # 创建自定义字段服务实例
        service = CustomFieldService(session=db.session, account=user)

        # 获取数据库表结构信息
        try:
            # 检查json_schemas表结构 - 使用text()函数包装SQL语句
            from sqlalchemy import text

            result = db.session.execute(
                text("PRAGMA table_info(json_schemas)")
            ).fetchall()
            columns = [row[1] for row in result]  # 第二个元素是列名
            current_app.logger.debug(f"json_schemas表的列: {columns}")

            if "entity_type" not in columns:
                current_app.logger.error(
                    "数据库中缺少entity_type列。这可能是数据库迁移未完成导致的问题。"
                )
                # 返回错误响应，避免执行后续查询
                return make_api_response(
                    ResponseSchema[PageResponse].from_error(
                        message="数据库结构不完整，请联系管理员运行数据库迁移",
                        status=500,
                    ),
                    500,
                )
        except Exception as table_error:
            current_app.logger.error(f"检查表结构出错: {table_error}")

        # 获取JSON Schema列表
        try:
            schemas, total = service.get_schemas_by_entity_type(
                entity_type=schema_entity_type,
                company_id=company_id,
                page=page,
                limit=limit,
                include_system=include_system,
            )
        except Exception as query_error:
            current_app.logger.error(f"查询失败详情: {query_error}")
            raise query_error

        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1

        # 构建分页响应
        pagination = PageResponse(
            total_page=total_page, cur_page=page, page_size=limit, data=schemas
        )

        return make_api_response(ResponseSchema[PageResponse](data=pagination))

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"List JSON schemas failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )


@bp.route("/schema/get/<int:schema_id>", methods=["GET"])
@login_required
def get_json_schema(schema_id: int) -> Response:
    """获取JSON Schema详情

    获取指定ID的JSON Schema详细信息，包括结构定义、UI配置和元数据。

    Args:
        schema_id: Schema ID

    Returns:
        Response: 包含Schema详情的JSON响应和HTTP状态码
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
        service = CustomFieldService(session=db.session, account=user)

        # 获取JSON Schema
        schema = service.query_schema_by_id(schema_id)
        if not schema:
            return make_api_response(
                ResponseSchema[JsonSchemaSchema].from_error(
                    message="Schema不存在或无权限查看", status=404
                ),
                404,
            )

        # 转换为API响应模型
        result = JsonSchemaSchema.model_validate(schema)
        return make_api_response(ResponseSchema[JsonSchemaSchema](data=result))

    except Exception as e:
        current_app.logger.error(f"Get JSON schema failed: {e}")
        return make_api_response(
            ResponseSchema[JsonSchemaSchema].from_error(
                message="服务器错误", status=500
            ),
            500,
        )


@bp.route("/value/create", methods=["POST"])
@login_required
def create_json_value() -> Response:
    """创建JSON值

    为实体创建自定义字段值。系统会根据关联的Schema验证提交的数据是否符合定义的结构和规则。

    请求体格式:
    {
        "schema_id": 1,
        "entity_type": "employee",
        "entity_id": 42,
        "value": {
            "emergency_contact_name": "张三",
            "emergency_relation": "配偶",
            "emergency_phone": "13800138000"
        },
        "remark": "备注信息"
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
        service = CustomFieldService(session=db.session, account=user)

        # 验证请求数据
        value_data = JsonValueCreate.model_validate(request.json)

        # 创建JSON值
        result = service.create_json_value(value_data)
        if not result:
            return make_api_response(
                ResponseSchema[JsonValueSchema].from_error(
                    message="创建自定义字段值失败，Schema不存在或无权限", status=400
                ),
                400,
            )

        return make_api_response(ResponseSchema[JsonValueSchema](data=result))

    except ValidationError as e:
        return make_api_response(
            ResponseSchema[JsonValueSchema].from_error(
                message=f"数据验证失败: {str(e)}", status=400
            ),
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

    更新实体的自定义字段值。系统会根据关联的Schema验证更新后的数据是否符合规则。

    Args:
        value_id: 值ID

    请求体格式:
    {
        "value": {
            "emergency_contact_name": "李四",
            "emergency_relation": "父母",
            "emergency_phone": "13900139000"
        },
        "remark": "更新的备注信息"
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
        service = CustomFieldService(session=db.session, account=user)

        # 验证请求数据
        value_data = JsonValueUpdate.model_validate(request.json)

        # 更新JSON值
        result = service.update_json_value(value_id, value_data)
        if not result:
            return make_api_response(
                ResponseSchema[JsonValueSchema].from_error(
                    message="更新自定义字段值失败，值不存在或无权限", status=404
                ),
                404,
            )

        return make_api_response(ResponseSchema[JsonValueSchema](data=result))

    except ValidationError as e:
        return make_api_response(
            ResponseSchema[JsonValueSchema].from_error(
                message=f"数据验证失败: {str(e)}", status=400
            ),
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

    删除实体的自定义字段值。这将永久删除该数据，不可恢复。

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
        service = CustomFieldService(session=db.session, account=user)

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
    """获取实体的自定义字段值

    获取指定实体的所有自定义字段值，或者筛选特定Schema的值。

    Args:
        entity_type: 实体类型，如employee, candidate等
        entity_id: 实体ID

    查询参数:
        schema_id: 可选，指定Schema ID，只返回该Schema的值

    Returns:
        Response: 包含值列表的JSON响应和HTTP状态码
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
        service = CustomFieldService(session=db.session, account=user)

        # 获取查询参数
        schema_id_str = request.args.get("schema_id")
        schema_id = int(schema_id_str) if schema_id_str else None

        # 获取实体的JSON值
        values = service.get_json_values(
            entity_type=entity_type, entity_id=entity_id, schema_id=schema_id
        )

        return make_api_response(ResponseSchema[List[JsonValueSchema]](data=values))

    except Exception as e:
        current_app.logger.error(f"Get entity values failed: {e}")
        return make_api_response(
            ResponseSchema[List[JsonValueSchema]].from_error(
                message="服务器错误", status=500
            ),
            500,
        )


# 高级查询功能
@bp.route("/search", methods=["POST"])
@login_required
def search_by_custom_field() -> Response:
    """根据自定义字段搜索实体

    基于自定义字段值条件搜索实体。支持多条件组合查询（与逻辑），各种比较操作符，
    以及对嵌套JSON数据的路径查询。结果以分页方式返回实体ID列表，可与其他API结合使用。

    请求体格式:
    {
        "entity_type": "employee",         // 实体类型
        "company_id": 1,                   // 公司ID
        "conditions": [                    // 查询条件数组
            {
                "schema_id": 1,            // Schema ID
                "path": "emergency_contact.name",  // 字段路径
                "operator": "like",        // 操作符
                "value": "张"              // 比较值
            },
            {
                "schema_id": 1,
                "path": "emergency_relation",
                "operator": "eq",
                "value": "配偶"
            }
        ],
        "page": 1,                         // 页码
        "limit": 10                        // 每页记录数
    }

    支持的操作符:
    - eq: 等于
    - neq: 不等于
    - gt: 大于
    - gte: 大于等于
    - lt: 小于
    - lte: 小于等于
    - like: 包含（字符串）
    - in: 在列表中

    Returns:
        Response: 包含实体ID列表和分页信息的JSON响应和HTTP状态码
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
        service = CustomFieldService(session=db.session, account=user)

        # 获取请求数据
        data = request.json
        entity_type = data.get("entity_type")
        company_id = data.get("company_id")
        conditions = data.get("conditions", [])
        page = data.get("page", 1)
        limit = data.get("limit", 10)

        # 验证必要参数
        if not entity_type or not company_id:
            return make_api_response(
                ResponseSchema[Dict].from_error(
                    message="缺少必要参数：entity_type或company_id", status=400
                ),
                400,
            )

        # 执行搜索
        entity_ids, total = service.search_entities_by_custom_field(
            entity_type=entity_type,
            company_id=company_id,
            conditions=conditions,
            page=page,
            limit=limit,
        )

        # 计算总页数
        total_page = (total + limit - 1) // limit if total > 0 else 1

        # 构建结果
        result = {
            "entity_ids": entity_ids,
            "total": total,
            "page": page,
            "limit": limit,
            "total_page": total_page,
        }

        return make_api_response(ResponseSchema[Dict](data=result))

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[Dict].from_error(message=str(e), status=403),
            403,
        )
    except Exception as e:
        current_app.logger.error(f"Search by custom field failed: {e}")
        return make_api_response(
            ResponseSchema[Dict].from_error(
                message=f"服务器错误: {str(e)}", status=500
            ),
            500,
        )


# Schema迁移功能
@bp.route("/schema/migrate", methods=["POST"])
@login_required
def migrate_schema() -> Response:
    """迁移Schema数据

    将旧Schema的数据迁移到新Schema。支持字段映射，可以将旧结构的数据转换为新结构。
    系统会验证迁移后的数据是否符合新Schema的定义。

    请求体格式:
    {
        "old_schema_id": 1,           // 旧Schema ID
        "new_schema_id": 2,           // 新Schema ID
        "migration_map": {            // 字段映射
            "old_field.path": "new_field.path",
            "simple_field": "new_simple_field"
        }
    }

    示例：迁移从扁平结构到嵌套结构
    {
        "old_schema_id": 1,
        "new_schema_id": 2,
        "migration_map": {
            "emergency_contact_name": "emergency.name",
            "emergency_relation": "emergency.relation",
            "emergency_phone": "emergency.phone"
        }
    }

    Returns:
        Response: 包含迁移结果统计的JSON响应和HTTP状态码
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
        service = CustomFieldService(session=db.session, account=user)

        # 获取请求数据
        data = request.json
        old_schema_id = data.get("old_schema_id")
        new_schema_id = data.get("new_schema_id")
        migration_map = data.get("migration_map", {})

        # 验证必要参数
        if not old_schema_id or not new_schema_id or not migration_map:
            return make_api_response(
                ResponseSchema[Dict].from_error(
                    message="缺少必要参数：old_schema_id、new_schema_id或migration_map",
                    status=400,
                ),
                400,
            )

        # 执行迁移
        success_count, failed_ids = service.migrate_schema(
            old_schema_id=old_schema_id,
            new_schema_id=new_schema_id,
            migration_map=migration_map,
        )

        # 构建结果
        result = {
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_entity_ids": failed_ids,
        }

        return make_api_response(ResponseSchema[Dict](data=result))

    except ValidationError as e:
        return make_api_response(
            ResponseSchema[Dict].from_error(
                message=f"数据验证失败: {str(e)}", status=400
            ),
            400,
        )
    except PermissionError as e:
        return make_api_response(
            ResponseSchema[Dict].from_error(message=str(e), status=403),
            403,
        )
    except ValueError as e:
        return make_api_response(
            ResponseSchema[Dict].from_error(message=str(e), status=400),
            400,
        )
    except Exception as e:
        current_app.logger.error(f"Schema migration failed: {e}")
        return make_api_response(
            ResponseSchema[Dict].from_error(
                message=f"服务器错误: {str(e)}", status=500
            ),
            500,
        )
