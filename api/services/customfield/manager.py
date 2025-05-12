from typing import Optional, List, Tuple, Dict, Any, Union
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from libs.models import AccountInDB, JsonSchemaInDB, JsonValueInDB
from libs.models.json_schema import SchemaEntityType
from services.permission import PermissionService, PermissionError

from ._schema import (
    JsonSchemaCreate,
    JsonSchemaUpdate,
    JsonSchemaSchema,
    JsonValueCreate,
    JsonValueUpdate,
    JsonValueSchema,
    JsonSchemaClone,
)
from .validator import validate_against_schema, ValidationError


class CustomFieldService:
    """自定义字段服务类，封装与自定义字段相关的数据库操作"""

    session: Session  # 数据库会话对象
    account: AccountInDB  # 当前登录的用户对象
    _permission: PermissionService  # 权限服务对象

    def __init__(self, session: Session, account: AccountInDB):
        """初始化自定义字段服务

        Args:
            session: SQLAlchemy数据库会话
            account: 当前登录用户
        """
        self.session = session
        self.account = account
        self._permission = PermissionService(session, account)

    def create_json_schema(
        self, schema_data: JsonSchemaCreate
    ) -> Optional[JsonSchemaSchema]:
        """创建新的JSON Schema

        Args:
            schema_data: 包含JSON Schema信息的Pydantic模型

        Returns:
            成功创建则返回Schema信息模型，失败则返回None

        Raises:
            PermissionError: 当用户没有权限创建Schema时
        """
        # 添加调试输出，查看传入的schema_data内容
        print(f"DEBUG - create_json_schema 接收到的数据: {schema_data}")
        print(f"DEBUG - schema_value的内容: {schema_data.schema_value}")
        print(f"DEBUG - schema_value的类型: {type(schema_data.schema_value)}")

        # 如果有公司ID，检查权限
        if schema_data.company_id:
            if not self._permission.can_manage_company(schema_data.company_id):
                raise PermissionError("您没有在此公司创建自定义字段的权限")

        # 创建Schema数据库模型实例
        schema = JsonSchemaInDB(
            name=schema_data.name,
            schema=schema_data.schema_value,
            entity_type=schema_data.entity_type,
            ui_schema=schema_data.ui_schema,
            company_id=schema_data.company_id,
            is_system=schema_data.is_system,
            remark=schema_data.remark,
            version=1,  # 初始版本为1
        )

        # 添加到数据库会话
        self.session.add(schema)
        try:
            # 提交事务，保存到数据库
            self.session.commit()
            # 刷新对象，获取生成的ID等
            self.session.refresh(schema)

            # 添加调试输出，查看数据库对象
            print(f"DEBUG - 创建的数据库对象: {schema}")
            print(f"DEBUG - schema.schema字段: {schema.schema}")

            try:
                # 将数据库模型转换为API响应模型
                result = JsonSchemaSchema.model_validate(schema)
                print(f"DEBUG - 成功转换为API模型: {result}")
                return result
            except Exception as e:
                print(f"ERROR - 模型转换失败: {e}")
                import traceback

                print(traceback.format_exc())
                return None

        except IntegrityError:
            # 处理数据库完整性错误
            self.session.rollback()
            return None

    def update_json_schema(
        self, schema_id: int, schema_data: JsonSchemaUpdate
    ) -> Optional[JsonSchemaSchema]:
        """更新JSON Schema

        Args:
            schema_id: Schema ID
            schema_data: 包含要更新的字段的Pydantic模型

        Returns:
            成功更新则返回更新后的Schema信息模型，失败或未找到则返回None

        Raises:
            PermissionError: 当用户没有权限更新指定Schema时
        """
        # 先获取Schema信息
        schema = self.query_schema_by_id(schema_id)
        if not schema:
            return None

        # 检查权限
        if schema.company_id and not self._permission.can_manage_company(
            schema.company_id
        ):
            raise PermissionError("您没有更新该Schema的权限")

        # 如果是系统Schema且当前用户不是超级管理员，禁止修改
        if schema.is_system and not self._permission.is_super_admin():
            raise PermissionError("您没有修改系统Schema的权限")

        # 创建新版本Schema
        if (
            schema_data.schema_value is not None
            and schema_data.schema_value != schema.schema
        ):
            # Schema内容发生变化，创建新版本
            new_schema = JsonSchemaInDB(
                name=schema_data.name or schema.name,
                schema=schema_data.schema_value,
                entity_type=schema.entity_type,
                ui_schema=schema_data.ui_schema
                if schema_data.ui_schema is not None
                else schema.ui_schema,
                company_id=schema.company_id,
                is_system=schema.is_system,
                remark=schema_data.remark
                if schema_data.remark is not None
                else schema.remark,
                version=schema.version + 1,  # 版本号加1
                parent_schema_id=schema.id,  # 关联到父Schema
            )
            self.session.add(new_schema)

            # 提交事务，保存新版本
            try:
                self.session.commit()
                self.session.refresh(new_schema)
                return JsonSchemaSchema.model_validate(new_schema)
            except IntegrityError:
                self.session.rollback()
                return None
        else:
            # 仅更新名称、UI配置或备注等元数据，不创建新版本
            if schema_data.name is not None:
                schema.name = schema_data.name
            if schema_data.ui_schema is not None:
                schema.ui_schema = schema_data.ui_schema
            if schema_data.remark is not None:
                schema.remark = schema_data.remark

            # 更新时间
            schema.updated_at = datetime.now()

            try:
                # 提交事务，保存更改
                self.session.commit()
                # 刷新对象，获取最新状态
                self.session.refresh(schema)
                # 转换为API响应模型
                return JsonSchemaSchema.model_validate(schema)
            except IntegrityError:
                # 处理数据库完整性错误
                self.session.rollback()
                return None

    def delete_json_schema(self, schema_id: int) -> bool:
        """删除JSON Schema

        Args:
            schema_id: Schema ID

        Returns:
            删除成功返回True，失败或未找到返回False

        Raises:
            PermissionError: 当用户没有权限删除指定Schema时
        """
        # 先获取Schema信息
        schema = self.query_schema_by_id(schema_id)
        if not schema:
            return False

        # 检查权限
        if schema.company_id and not self._permission.can_manage_company(
            schema.company_id
        ):
            raise PermissionError("您没有删除该Schema的权限")

        # 如果是系统Schema且当前用户不是超级管理员，禁止删除
        if schema.is_system and not self._permission.is_super_admin():
            raise PermissionError("您没有删除系统Schema的权限")

        try:
            # 先查询是否有关联的JSON值
            json_values = (
                self.session.query(JsonValueInDB).filter_by(schema_id=schema_id).count()
            )
            if json_values > 0:
                # 如果有关联的JSON值，不允许删除
                return False

            # 从数据库中删除
            self.session.delete(schema)
            # 提交事务
            self.session.commit()
            return True
        except Exception:
            # 处理可能的错误
            self.session.rollback()
            return False

    def clone_json_schema(
        self, clone_data: JsonSchemaClone
    ) -> Optional[JsonSchemaSchema]:
        """克隆JSON Schema到另一个公司

        Args:
            clone_data: 包含克隆信息的Pydantic模型

        Returns:
            成功克隆则返回新的Schema信息模型，失败则返回None

        Raises:
            PermissionError: 当用户没有权限克隆Schema时
        """
        # 获取源Schema
        source_schema = self.query_schema_by_id(clone_data.source_schema_id)
        if not source_schema:
            return None

        # 检查目标公司权限
        if not self._permission.can_manage_company(clone_data.target_company_id):
            raise PermissionError("您没有在目标公司创建自定义字段的权限")

        # 创建新Schema
        new_schema = JsonSchemaInDB(
            name=clone_data.name or source_schema.name,
            schema=source_schema.schema,
            entity_type=source_schema.entity_type,
            ui_schema=source_schema.ui_schema,
            company_id=clone_data.target_company_id,
            is_system=False,  # 克隆的Schema不是系统Schema
            remark=source_schema.remark,
            version=1,  # 克隆的Schema版本从1开始
        )

        # 添加到数据库
        self.session.add(new_schema)
        try:
            # 提交事务
            self.session.commit()
            # 刷新对象
            self.session.refresh(new_schema)
            # 转换为API响应模型
            return JsonSchemaSchema.model_validate(new_schema)
        except IntegrityError:
            self.session.rollback()
            return None

    def query_schema_by_id(self, schema_id: int) -> Optional[JsonSchemaInDB]:
        """根据ID查询JSON Schema

        Args:
            schema_id: Schema ID

        Returns:
            找到则返回Schema数据库模型对象，否则返回None
        """
        schema = self.session.query(JsonSchemaInDB).get(schema_id)

        # 检查权限（但不抛出异常，因为这是内部方法）
        if (
            schema
            and schema.company_id
            and not self._permission.can_view_company(schema.company_id)
        ):
            return None

        return schema

    def get_schemas_by_entity_type(
        self,
        entity_type: SchemaEntityType,
        company_id: Optional[int] = None,
        page: int = 1,
        limit: int = 10,
        include_system: bool = True,
    ) -> Tuple[List[JsonSchemaSchema], int]:
        """获取指定实体类型和公司的JSON Schema列表

        Args:
            entity_type: 实体类型
            company_id: 公司ID，可选
            page: 页码，从1开始
            limit: 每页显示数量
            include_system: 是否包含系统预设Schema

        Returns:
            包含Schema列表和总数的元组
        """
        # 构建基础查询
        query = self.session.query(JsonSchemaInDB).filter_by(entity_type=entity_type)

        # 如果指定了公司ID
        if company_id:
            # 检查权限
            if not self._permission.can_view_company(company_id):
                raise PermissionError("您没有查看该公司自定义字段的权限")

            # 查询条件：属于该公司的Schema或系统Schema
            if include_system:
                query = query.filter(
                    or_(
                        JsonSchemaInDB.company_id == company_id,
                        JsonSchemaInDB.is_system == True,
                    )
                )
            else:
                query = query.filter(JsonSchemaInDB.company_id == company_id)
        else:
            # 没有指定公司ID，只返回当前用户有权限查看的公司的Schema和系统Schema
            if not self._permission.is_super_admin():
                # 获取用户有权限查看的所有公司ID
                company_ids = [ac.company_id for ac in self.account.account_companies]
                if include_system:
                    query = query.filter(
                        or_(
                            JsonSchemaInDB.company_id.in_(company_ids),
                            JsonSchemaInDB.is_system == True,
                        )
                    )
                else:
                    query = query.filter(JsonSchemaInDB.company_id.in_(company_ids))

        # 计算总数
        total = query.count()

        # 分页
        query = query.order_by(JsonSchemaInDB.updated_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        # 执行查询
        schemas = query.all()

        # 转换为API响应模型
        result = [JsonSchemaSchema.model_validate(schema) for schema in schemas]

        return result, total

    def create_json_value(
        self, value_data: JsonValueCreate
    ) -> Optional[JsonValueSchema]:
        """创建新的JSON值

        Args:
            value_data: 包含JSON值信息的Pydantic模型

        Returns:
            成功创建则返回值信息模型，失败则返回None

        Raises:
            PermissionError: 当用户没有权限创建值时
            ValidationError: 当提交的数据不符合Schema定义时
        """
        # 验证Schema是否存在
        schema = self.query_schema_by_id(value_data.schema_id)
        if not schema:
            return None

        # 检查权限
        if schema.company_id:
            if not self._permission.can_manage_company(schema.company_id):
                raise PermissionError("您没有使用该Schema的权限")

        # 验证数据是否符合Schema定义
        validate_against_schema(schema.schema, value_data.value)

        # 创建JSON值数据库模型实例
        json_value = JsonValueInDB(
            schema_id=value_data.schema_id,
            entity_id=value_data.entity_id,
            entity_type=value_data.entity_type,
            value=value_data.value,
            remark=value_data.remark,
        )

        # 添加到数据库会话
        self.session.add(json_value)
        try:
            # 提交事务，保存到数据库
            self.session.commit()
            # 刷新对象，获取生成的ID等
            self.session.refresh(json_value)
            # 将数据库模型转换为API响应模型
            return JsonValueSchema.model_validate(json_value)
        except IntegrityError:
            # 处理数据库完整性错误
            self.session.rollback()
            return None

    def update_json_value(
        self, value_id: int, value_data: JsonValueUpdate
    ) -> Optional[JsonValueSchema]:
        """更新JSON值

        Args:
            value_id: 值ID
            value_data: 包含要更新的字段的Pydantic模型

        Returns:
            成功更新则返回更新后的值信息模型，失败或未找到则返回None

        Raises:
            PermissionError: 当用户没有权限更新指定值时
            ValidationError: 当提交的数据不符合Schema定义时
        """
        # 先获取值信息
        json_value = self.session.query(JsonValueInDB).get(value_id)
        if not json_value:
            return None

        # 获取关联的Schema
        schema = self.query_schema_by_id(json_value.schema_id)
        if not schema:
            return None

        # 检查权限
        if schema.company_id and not self._permission.can_manage_company(
            schema.company_id
        ):
            raise PermissionError("您没有更新该值的权限")

        # 验证数据是否符合Schema定义
        validate_against_schema(schema.schema, value_data.value)

        # 更新字段
        json_value.value = value_data.value
        if value_data.remark is not None:
            json_value.remark = value_data.remark

        # 更新时间
        json_value.updated_at = datetime.now()

        try:
            # 提交事务，保存更改
            self.session.commit()
            # 刷新对象，获取最新状态
            self.session.refresh(json_value)
            # 转换为API响应模型
            return JsonValueSchema.model_validate(json_value)
        except IntegrityError:
            # 处理数据库完整性错误
            self.session.rollback()
            return None

    def delete_json_value(self, value_id: int) -> bool:
        """删除JSON值

        Args:
            value_id: 值ID

        Returns:
            删除成功返回True，失败或未找到返回False

        Raises:
            PermissionError: 当用户没有权限删除指定值时
        """
        # 先获取值信息
        json_value = self.session.query(JsonValueInDB).get(value_id)
        if not json_value:
            return False

        # 获取关联的Schema
        schema = self.query_schema_by_id(json_value.schema_id)
        if not schema:
            return False

        # 检查权限
        if schema.company_id and not self._permission.can_manage_company(
            schema.company_id
        ):
            raise PermissionError("您没有删除该值的权限")

        try:
            # 从数据库中删除
            self.session.delete(json_value)
            # 提交事务
            self.session.commit()
            return True
        except Exception:
            # 处理可能的错误
            self.session.rollback()
            return False

    def get_json_values(
        self, entity_type: str, entity_id: int, schema_id: Optional[int] = None
    ) -> List[JsonValueSchema]:
        """获取实体的JSON值

        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            schema_id: Schema ID，可选，如果提供则只返回指定Schema的值

        Returns:
            值信息模型列表
        """
        # 构建查询
        query = self.session.query(JsonValueInDB).filter_by(
            entity_type=entity_type, entity_id=entity_id
        )

        # 如果指定了Schema ID
        if schema_id:
            query = query.filter_by(schema_id=schema_id)

        # 添加关联加载
        query = query.options(joinedload(JsonValueInDB.schema))

        # 执行查询
        values = query.all()

        # 检查权限
        result = []
        for value in values:
            schema = value.schema
            if (
                schema
                and schema.company_id
                and not self._permission.can_view_company(schema.company_id)
            ):
                continue
            result.append(JsonValueSchema.model_validate(value))

        return result

    def get_json_values_batch(
        self, entity_type: str, entity_ids: List[int], schema_id: Optional[int] = None
    ) -> Dict[int, List[JsonValueSchema]]:
        """批量获取多个实体的JSON值

        Args:
            entity_type: 实体类型
            entity_ids: 实体ID列表
            schema_id: Schema ID，可选，如果提供则只返回指定Schema的值

        Returns:
            以实体ID为键，值信息模型列表为值的字典
        """
        if not entity_ids:
            return {}

        # 构建查询
        query = self.session.query(JsonValueInDB).filter(
            JsonValueInDB.entity_type == entity_type,
            JsonValueInDB.entity_id.in_(entity_ids),
        )

        # 如果指定了Schema ID
        if schema_id:
            query = query.filter_by(schema_id=schema_id)

        # 添加关联加载
        query = query.options(joinedload(JsonValueInDB.schema))

        # 执行查询
        values = query.all()

        # 按实体ID分组，并检查权限
        result = {}
        for value in values:
            schema = value.schema
            if (
                schema
                and schema.company_id
                and not self._permission.can_view_company(schema.company_id)
            ):
                continue

            entity_id = value.entity_id
            if entity_id not in result:
                result[entity_id] = []

            result[entity_id].append(JsonValueSchema.model_validate(value))

        return result

    # 添加高级查询功能
    def search_entities_by_custom_field(
        self,
        entity_type: str,
        company_id: int,
        conditions: List[Dict[str, Any]],
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[int], int]:
        """根据自定义字段条件搜索实体

        Args:
            entity_type: 实体类型
            company_id: 公司ID
            conditions: 搜索条件列表，每个条件是一个字典，包含schema_id, path, operator, value
                schema_id: Schema ID
                path: 字段路径，用点分隔，如"emergency_contact.name"
                operator: 操作符，支持eq, neq, gt, gte, lt, lte, like, in
                value: 比较值
            page: 页码，从1开始
            limit: 每页显示数量

        Returns:
            符合条件的实体ID列表和总数的元组

        Raises:
            PermissionError: 当用户没有权限查询该公司数据时
        """
        # 检查权限
        if not self._permission.can_view_company(company_id):
            raise PermissionError("您没有查询该公司数据的权限")

        # 基础查询：获取指定公司和实体类型的所有值
        base_query = (
            self.session.query(
                JsonValueInDB.entity_id, JsonValueInDB.schema_id, JsonValueInDB.value
            )
            .join(JsonSchemaInDB, JsonValueInDB.schema_id == JsonSchemaInDB.id)
            .filter(
                JsonValueInDB.entity_type == entity_type,
                or_(
                    JsonSchemaInDB.company_id == company_id,
                    JsonSchemaInDB.is_system == True,
                ),
            )
        )

        # 应用条件过滤
        filtered_entity_ids = set()
        all_entity_ids = set()

        # 首先获取所有匹配实体类型的ID
        entity_id_query = (
            self.session.query(JsonValueInDB.entity_id)
            .filter(JsonValueInDB.entity_type == entity_type)
            .distinct()
        )
        all_entity_ids = {row[0] for row in entity_id_query.all()}

        # 如果没有条件，直接返回所有ID
        if not conditions:
            filtered_entity_ids = all_entity_ids
        else:
            # 处理每个条件
            for condition in conditions:
                schema_id = condition.get("schema_id")
                path = condition.get("path", "")
                operator = condition.get("operator", "eq")
                value = condition.get("value")

                # 构建SQL查询条件
                query = base_query.filter(JsonValueInDB.schema_id == schema_id)

                # 根据操作符构建过滤条件
                filtered_ids = set()

                # 执行查询
                results = query.all()
                for entity_id, _, json_value in results:
                    # 解析路径
                    field_value = self._get_value_by_path(json_value, path)

                    # 应用操作符
                    if self._compare_values(field_value, operator, value):
                        filtered_ids.add(entity_id)

                # 与之前的结果取交集
                if not filtered_entity_ids:
                    filtered_entity_ids = filtered_ids
                else:
                    filtered_entity_ids &= filtered_ids

                # 如果已经没有匹配的ID，提前返回
                if not filtered_entity_ids:
                    break

        # 转换为列表并排序
        entity_ids = sorted(list(filtered_entity_ids))
        total = len(entity_ids)

        # 应用分页
        start = (page - 1) * limit
        end = start + limit
        paged_ids = entity_ids[start:end]

        return paged_ids, total

    def _get_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """根据路径获取JSON值中的字段值

        Args:
            data: JSON值
            path: 字段路径，用点分隔，如"emergency_contact.name"

        Returns:
            字段值，如果路径无效则返回None
        """
        if not path:
            return data

        parts = path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def _compare_values(
        self, field_value: Any, operator: str, compare_value: Any
    ) -> bool:
        """比较字段值与比较值

        Args:
            field_value: 字段值
            operator: 操作符
            compare_value: 比较值

        Returns:
            比较结果
        """
        if field_value is None:
            return (
                (operator == "eq" and compare_value is None)
                or operator == "neq"
                and compare_value is not None
            )

        if operator == "eq":
            return field_value == compare_value
        elif operator == "neq":
            return field_value != compare_value
        elif operator == "gt":
            return isinstance(field_value, (int, float)) and field_value > compare_value
        elif operator == "gte":
            return (
                isinstance(field_value, (int, float)) and field_value >= compare_value
            )
        elif operator == "lt":
            return isinstance(field_value, (int, float)) and field_value < compare_value
        elif operator == "lte":
            return (
                isinstance(field_value, (int, float)) and field_value <= compare_value
            )
        elif operator == "like":
            return (
                isinstance(field_value, str)
                and isinstance(compare_value, str)
                and compare_value.lower() in field_value.lower()
            )
        elif operator == "in":
            return isinstance(compare_value, list) and field_value in compare_value
        else:
            return False

    # 添加Schema迁移功能
    def migrate_schema(
        self, old_schema_id: int, new_schema_id: int, migration_map: Dict[str, str]
    ) -> Tuple[int, List[int]]:
        """迁移数据从旧Schema到新Schema

        Args:
            old_schema_id: 旧Schema ID
            new_schema_id: 新Schema ID
            migration_map: 字段映射，键为旧字段路径，值为新字段路径

        Returns:
            成功迁移的数据数量和失败的实体ID列表

        Raises:
            PermissionError: 当用户没有权限迁移数据时
        """
        # 获取新旧Schema
        old_schema = self.query_schema_by_id(old_schema_id)
        new_schema = self.query_schema_by_id(new_schema_id)

        if not old_schema or not new_schema:
            return 0, []

        # 检查权限
        if old_schema.company_id and not self._permission.can_manage_company(
            old_schema.company_id
        ):
            raise PermissionError("您没有迁移旧Schema数据的权限")

        if new_schema.company_id and not self._permission.can_manage_company(
            new_schema.company_id
        ):
            raise PermissionError("您没有使用新Schema的权限")

        # 确保两个Schema的实体类型一致
        if old_schema.entity_type != new_schema.entity_type:
            raise ValueError("新旧Schema的实体类型必须一致")

        # 查询旧Schema的所有值
        old_values = (
            self.session.query(JsonValueInDB).filter_by(schema_id=old_schema_id).all()
        )

        success_count = 0
        failed_ids = []

        # 为每个旧值创建新值
        for old_value in old_values:
            try:
                # 创建新的值结构
                new_value = {}

                # 应用字段映射
                for old_path, new_path in migration_map.items():
                    old_field_value = self._get_value_by_path(old_value.value, old_path)
                    if old_field_value is not None:
                        self._set_value_by_path(new_value, new_path, old_field_value)

                # 验证新值是否符合新Schema
                try:
                    validate_against_schema(new_schema.schema, new_value)

                    # 创建新的JSON值
                    json_value = JsonValueInDB(
                        schema_id=new_schema_id,
                        entity_id=old_value.entity_id,
                        entity_type=old_value.entity_type,
                        value=new_value,
                        remark=f"由Schema ID {old_schema_id} 迁移而来",
                    )

                    self.session.add(json_value)
                    success_count += 1

                except ValidationError:
                    failed_ids.append(old_value.entity_id)

            except Exception:
                failed_ids.append(old_value.entity_id)

        # 提交事务
        try:
            self.session.commit()
            return success_count, failed_ids
        except IntegrityError:
            self.session.rollback()
            return 0, [old_value.entity_id for old_value in old_values]

    def _set_value_by_path(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """根据路径设置JSON值中的字段值

        Args:
            data: JSON值
            path: 字段路径，用点分隔，如"emergency_contact.name"
            value: 要设置的值
        """
        if not path:
            return

        parts = path.split(".")
        current = data

        # 遍历路径中间部分
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]

        # 设置最后一个部分的值
        current[parts[-1]] = value
