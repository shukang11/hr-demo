"""
Schema相关API路由
用于自定义字段Schema定义的创建、查询、更新和删除操作
"""

from flask import request, Response, current_app
from flask_login import current_user, login_required
from sqlalchemy import text, or_, select

from extensions.ext_database import db
from libs.schema.http import ResponseSchema, make_api_response
from libs.schema.page import PageResponse
from libs.models.json_schema import SchemaEntityType
from libs.models.account import AccountInDB
from libs.models import JsonSchemaInDB, AccountCompanyInDB
from services.customfield import (
    JsonSchemaCreate,
    JsonSchemaUpdate,
    JsonSchemaSchema,
    JsonSchemaClone,
    CustomFieldService,
)
from services.permission import PermissionError

# 导入蓝图对象
from . import bp


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
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

        # 验证请求数据
        schema_data = JsonSchemaCreate.model_validate(request.json)
        current_app.logger.debug(f"创建JSON Schema，参数: {schema_data}")

        # 添加详细调试信息
        current_app.logger.debug(
            f"JsonSchemaCreate模型详情: schema_value={schema_data.schema_value}"
        )
        current_app.logger.debug(f"请求JSON原始数据: {request.json}")

        # 创建JSON Schema
        result = service.create_json_schema(schema_data)

        # 添加结果调试信息
        if result:
            current_app.logger.debug(f"创建成功，返回数据: {result}")
            current_app.logger.debug(f"返回数据模型类型: {type(result)}")
            current_app.logger.debug(
                f"返回的schema_value: {getattr(result, 'schema_value', '字段不存在')}"
            )

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
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

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
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

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
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

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

        # 创建自定义字段服务实例
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

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

        # 获取数据库表结构信息
        schemas, total_count = service.get_schemas_by_entity_type(
            schema_entity_type,
            company_id=company_id,
            page=page,
            limit=limit,
            include_system=include_system,
        )

        # 计算总页数
        total_page = (total_count + limit - 1) // limit

        # 创建分页响应
        pagination = PageResponse(
            total_page=total_page, cur_page=page, page_size=limit, data=schemas
        )

        return make_api_response(ResponseSchema[PageResponse](data=pagination))

    except PermissionError as e:
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message=str(e), status=403), 403
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
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

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


@bp.route("/schema/list_all", methods=["GET"])
@login_required
def list_all_json_schemas() -> Response:
    """获取所有JSON Schema列表

    获取所有实体类型的JSON Schema列表，支持分页和公司筛选。
    可选择是否包含系统预设的Schema。结果按更新时间倒序排列。

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
        user: AccountInDB = current_user._get_current_object()  # type: ignore

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
            f"列出所有JSON Schema，参数: page={page}, limit={limit}, company_id={company_id}, include_system={include_system}"
        )

        # 创建自定义字段服务实例
        service = CustomFieldService(session=db.session, account=user)  # type: ignore

        # 获取数据库表结构信息，确保表存在
        try:
            # 检查json_schemas表结构 - 使用text()函数包装SQL语句
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

        # 获取所有Schema - 直接使用会话查询，绕过实体类型限制
        # 构建基础查询
        query = db.session.query(JsonSchemaInDB)

        # 如果指定了公司ID
        if company_id:
            # 检查权限
            if not service._permission.can_view_company(company_id):
                raise PermissionError("您没有查看该公司自定义字段的权限")

            # 查询条件：属于该公司的Schema或系统Schema
            if include_system:
                query = query.filter(
                    or_(
                        JsonSchemaInDB.company_id == company_id,
                        JsonSchemaInDB.is_system,
                    )
                )
            else:
                query = query.filter(JsonSchemaInDB.company_id == company_id)
        else:
            # 没有指定公司ID，只返回当前用户有权限查看的公司的Schema和系统Schema
            if not service._permission.is_super_admin():
                # 获取用户有权限查看的所有公司ID
                # 从用户关联的公司中获取
                stmt = select(AccountCompanyInDB.company_id).where(
                    AccountCompanyInDB.account_id == user.id
                )
                company_ids_result = db.session.execute(stmt).all()
                company_ids = [row[0] for row in company_ids_result]

                current_app.logger.debug(f"用户可访问的公司ID: {company_ids}")

                if include_system:
                    query = query.filter(
                        or_(
                            JsonSchemaInDB.company_id.in_(company_ids)
                            if company_ids
                            else False,
                            JsonSchemaInDB.is_system,
                        )
                    )
                else:
                    if company_ids:
                        query = query.filter(JsonSchemaInDB.company_id.in_(company_ids))
                    else:
                        # 如果用户没有可访问的公司且不包含系统Schema，则返回空结果
                        return make_api_response(
                            ResponseSchema[PageResponse](
                                data=PageResponse(
                                    total_page=1,
                                    cur_page=page,
                                    page_size=limit,
                                    data=[],
                                )
                            )
                        )

        # 计算总数
        total = query.count()

        # 分页
        query = query.order_by(JsonSchemaInDB.updated_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        # 执行查询
        schema_entries = query.all()

        # 转换为API响应模型
        schemas = [JsonSchemaSchema.model_validate(schema) for schema in schema_entries]

        # 添加日志记录查询结果
        current_app.logger.debug(f"查询结果: 找到 {total} 个Schema")
        if total > 0 and schemas:
            current_app.logger.debug(
                f"包含的实体类型: {set(str(schema.entity_type) for schema in schemas)}"
            )

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
        current_app.logger.error(f"List all JSON schemas failed: {e}")
        return make_api_response(
            ResponseSchema[PageResponse].from_error(message="服务器错误", status=500),
            500,
        )
