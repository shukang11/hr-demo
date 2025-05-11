# HR系统自定义字段功能技术文档

## 1. 功能概述

自定义字段功能允许系统管理员和公司管理员为各类实体（如员工、候选人、公司、部门等）定义额外的、非标准化的数据结构。这种灵活性使得系统能够适应不同公司的独特需求，存储和管理各种自定义信息。

**开发进度:** ▇▇▇▇▇ 100%

## 2. 系统架构与设计理念

### 2.1 数据模型设计

系统采用双层设计模式实现自定义字段功能：

#### 核心数据模型

1. **JsonSchemaInDB**：定义字段结构
   ```python
   class JsonSchemaInDB(BaseModel):
       __tablename__ = "json_schemas"
       
       name: Mapped[str]                      # Schema 名称
       schema: Mapped[dict]                   # JSON Schema 定义
       entity_type: Mapped[SchemaEntityType]  # 适用实体类型(Employee, Candidate等)
       is_system: Mapped[bool]                # 是否为系统预设Schema
       version: Mapped[int]                   # Schema版本号
       parent_schema_id: Mapped[Optional[int]]  # 父Schema ID，用于版本管理
       company_id: Mapped[Optional[int]]      # 所属公司ID
       remark: Mapped[Optional[str]]          # 备注信息
       ui_schema: Mapped[Optional[dict]]      # UI展示相关配置
   ```

2. **JsonValueInDB**：存储字段值
   ```python
   class JsonValueInDB(BaseModel):
       __tablename__ = "json_values"
       
       schema_id: Mapped[int]      # 关联的JSON Schema ID
       entity_id: Mapped[int]      # 关联的实体ID
       entity_type: Mapped[str]    # 关联的实体类型
       value: Mapped[dict]         # JSON格式的数据值
       remark: Mapped[Optional[str]]  # 备注信息
   ```

#### 实体模型中的引用方式

系统支持两种自定义字段的应用方式：

1. **直接内联方式**：在实体表中直接包含自定义字段
   ```python
   class EmployeeInDB(BaseModel):
       # 基本字段...
       
       extra_value: Mapped[Optional[dict]]      # 内联的JSON数据
       extra_schema_id: Mapped[Optional[int]]   # 关联的Schema ID
       
       # 关系定义
       extra_schema: Mapped["JsonSchemaInDB"]   # 关联的Schema对象
   ```

2. **独立存储方式**：通过JsonValueInDB表关联多组自定义字段
   ```python
   # 通过JsonValueInDB表，一个实体可以关联多个不同的Schema和值
   ```

### 2.2 关系设计

系统支持两种关系模式：

1. **一对一关系**：通过实体表中的`extra_value`和`extra_schema_id`字段，将一组自定义字段直接关联到实体
2. **多对多关系**：通过`JsonValueInDB`表实现一个实体关联多组自定义字段，每组字段对应不同的Schema

### 2.3 版本控制机制

为了支持Schema的演进而不破坏现有数据，系统实现了Schema版本控制：

- 每个Schema有一个`version`字段标识版本号
- 当Schema结构发生变化时，创建新版本并通过`parent_schema_id`关联到旧版本
- 元数据修改（名称、UI配置、备注）不创建新版本，直接更新当前版本

## 3. 技术实现原理

### 3.1 JSON Schema验证机制

系统使用`jsonschema`库实现对数据的验证，确保提交的数据符合Schema定义：

```python
def validate_against_schema(schema_definition: Dict[str, Any], value: Dict[str, Any]) -> None:
    schema = schema_definition.get("schema", {})
    is_valid, errors = validate_value_against_schema(schema, value)
    if not is_valid:
        raise ValidationError(errors)
```

验证过程详细错误信息：
```python
def validate_value_against_schema(schema, value):
    errors = []
    validator = jsonschema.Draft7Validator(schema)
    for error in validator.iter_errors(value):
        path = ".".join([str(p) for p in error.path]) if error.path else "root"
        errors.append({
            "path": path,
            "message": error.message,
            "schema_path": ".".join([str(p) for p in error.schema_path]),
        })
    return len(errors) == 0, errors
```

### 3.2 多对多关系的实现

多对多关系通过`JsonValueInDB`表实现，关键特点：

1. 使用组合键`(entity_type, entity_id)`标识关联的实体
2. 使用`schema_id`关联到特定的Schema定义
3. 每个实体可以有多个不同Schema的值记录
4. 已创建索引优化查询性能：
   ```python
   __table_args__ = (
       db.Index("ix_json_value_entity", "entity_type", "entity_id"),
       db.Index("ix_json_value_schema", "schema_id"),
   )
   ```

### 3.3 高级查询功能

系统支持基于自定义字段内容的高级查询：

1. **路径查询**：支持访问嵌套JSON结构中的特定字段
   ```python
   def _get_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
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
   ```

2. **丰富的比较操作符**：
   - `eq`: 等于
   - `neq`: 不等于
   - `gt`, `gte`: 大于，大于等于
   - `lt`, `lte`: 小于，小于等于
   - `like`: 包含（字符串）
   - `in`: 在列表中

## 4. API设计

### 4.1 Schema管理API

| 端点                                            | 方法 | 描述                             |
| ----------------------------------------------- | ---- | -------------------------------- |
| `/customfield/schema/create`                    | POST | 创建新的JSON Schema              |
| `/customfield/schema/update/<int:schema_id>`    | POST | 更新现有Schema                   |
| `/customfield/schema/delete/<int:schema_id>`    | POST | 删除Schema（前提是没有关联数据） |
| `/customfield/schema/clone`                     | POST | 克隆Schema到另一个公司           |
| `/customfield/schema/list/<string:entity_type>` | GET  | 获取指定实体类型的Schema列表     |
| `/customfield/schema/get/<int:schema_id>`       | GET  | 获取Schema详情                   |

### 4.2 自定义字段值API

| 端点                                                             | 方法 | 描述                       |
| ---------------------------------------------------------------- | ---- | -------------------------- |
| `/customfield/value/create`                                      | POST | 创建新的自定义字段值       |
| `/customfield/value/update/<int:value_id>`                       | POST | 更新自定义字段值           |
| `/customfield/value/delete/<int:value_id>`                       | POST | 删除自定义字段值           |
| `/customfield/value/entity/<string:entity_type>/<int:entity_id>` | GET  | 获取实体的所有自定义字段值 |

### 4.3 高级功能API

| 端点                          | 方法 | 描述                           |
| ----------------------------- | ---- | ------------------------------ |
| `/customfield/search`         | POST | 基于自定义字段内容搜索实体     |
| `/customfield/schema/migrate` | POST | 将数据从旧Schema迁移到新Schema |

## 5. 权限管理

系统通过`PermissionService`实现精细的权限控制：

1. **公司级权限**
   - 普通用户只能查看/管理自己有权限的公司的Schema和值
   - 使用`can_view_company`和`can_manage_company`方法验证权限

2. **系统级权限**
   - 系统预设Schema（`is_system=True`）只能由超级管理员修改
   - 使用`is_super_admin`方法验证超级管理员权限

3. **错误处理**
   - 抛出`PermissionError`异常，包含详细错误信息
   - API层捕获并返回403状态码给客户端

## 6. 使用场景示例

### 6.1 员工紧急联系人信息

```json
{
  "name": "员工紧急联系人",
  "entity_type": "Employee",
  "schema": {
    "type": "object",
    "properties": {
      "emergency_contact": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "title": "联系人姓名"},
          "relation": {"type": "string", "title": "关系"},
          "phone": {"type": "string", "title": "联系电话"}
        },
        "required": ["name", "phone"]
      }
    }
  },
  "ui_schema": {
    "emergency_contact": {
      "name": {"ui:placeholder": "请输入联系人姓名"},
      "phone": {"ui:widget": "phone"}
    }
  }
}
```

### 6.2 候选人技能评估

```json
{
  "name": "技能评估表",
  "entity_type": "Candidate",
  "schema": {
    "type": "object",
    "properties": {
      "skills": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string", "title": "技能名称"},
            "level": {"type": "integer", "minimum": 1, "maximum": 5, "title": "技能等级"},
            "years": {"type": "number", "title": "使用年限"}
          }
        }
      },
      "overall_rating": {"type": "integer", "minimum": 1, "maximum": 10, "title": "综合评分"}
    }
  }
}
```

## 7. 自定义字段关系模式评估

当前系统同时支持一对一关系（通过实体表中的`extra_value`和`extra_schema_id`）和多对多关系（通过`JsonValueInDB`表）。这种混合设计提供了以下优势：

1. **简单常用场景的高效处理**：对于每个实体最常用的一组自定义字段，可直接存储在实体表中，避免额外的表连接
2. **复杂多变场景的灵活支持**：当需要为实体配置多组不同用途的自定义字段时，可通过`JsonValueInDB`表实现
3. **查询性能优化**：常用字段直接存储在实体表中，查询性能更优

因此，系统当前的设计已经同时满足"一对一"和"多对多"的需求，无需额外修改数据模型。

## 8. 未来扩展方向

1. **字段索引**：为常用的自定义字段创建数据库索引，提高查询性能
2. **字段统计**：添加统计分析功能，对自定义字段数据进行汇总分析
3. **条件工作流**：基于自定义字段值触发特定的业务流程
4. **导入导出**：支持自定义字段数据的批量导入导出

## 9. 功能改进与修复

### 9.1 稳定性与错误处理增强 (2025年5月6日)

1. **增强的日志记录**
   - 在Schema列表API中添加详细的调试和错误日志
   - 记录关键参数和操作流程，便于问题排查

2. **数据库结构验证**
   - 添加运行时表结构验证，确保关键列（如`entity_type`）存在
   - 提前检测数据库迁移问题，避免运行时错误
   - 提供用户友好的错误信息，引导管理员进行数据库迁移

3. **完善异常处理机制**
   - 捕获并记录查询异常的详细信息
   - 防止异常传播到外层影响其他功能模块

### 9.2 代码质量改进 (2025年5月6日)

1. **Pydantic模型更新**
   - 将`validator`装饰器更新为`field_validator`，适配Pydantic新版本
   - 将模型中的`schema`字段重命名为`schema_value`，避免与内部属性命名冲突

2. **参数命名规范化**
   - 统一字段命名约定，提高代码可读性和可维护性
   - 确保API请求和数据库字段映射正确

### 9.3 前端组件优化 (2025年5月6日)

1. **Schema选择器空值处理修复**
   - 修复了选择器中无选项值的处理逻辑
   - 将空值标识从空字符串`""`改为明确的`"null"`字符串值
   - 确保值为null时选择器显示正确的默认选项

### 9.4 主题适配与UI增强 (2025年5月10日)

1. **暗黑模式兼容性改进**
   - 修复了公司详情页在暗黑模式下的显示问题
   - 更新卡片组件样式，确保在所有主题下保持一致的视觉效果
   - 增强文本和背景色的对比度，提高可读性

2. **自适应布局优化**
   - 改进移动端显示，优化表单在小屏幕设备上的布局
   - 实现响应式设计，确保在不同尺寸的设备上都能良好展示

3. **交互体验提升**
   - 添加表单提交和数据加载时的过渡动画
   - 优化错误提示样式，使其更加醒目且易于理解
   - 为关键操作增加确认对话框，避免误操作

_更新日期: 2025年5月10日_