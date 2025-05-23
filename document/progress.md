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

### 2.4 API模块结构

#### 2.4.1 模块化设计 (2025年5月20日更新)

自定义字段API模块已重构为更模块化的结构，以提高代码的可维护性和可读性。新的结构将原来的单个文件拆分为以下组件：

```
api/routes/customfield/
├── __init__.py       # 蓝图定义和初始化
├── schema.py         # Schema定义相关路由
├── value.py          # 值管理相关路由
└── advanced.py       # 高级功能（搜索、迁移等）
```

每个子模块对应一个特定的功能域：
- **schema.py**: 处理JSON Schema的创建、更新、删除、查询和克隆
- **value.py**: 处理自定义字段值的创建、更新、删除和查询
- **advanced.py**: 处理高级功能，如基于自定义字段的搜索和Schema迁移

主文件 `customfield.py` 仍然保留，但仅用于导入和导出蓝图，确保向后兼容性。

这种模块化结构使开发团队能够独立处理每个功能域，减少了代码冲突的可能性，并提高了测试的隔离性。

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
|                                                 |
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

## 10. 实体自定义字段实现

### 10.1 员工自定义字段功能 (2025年5月21日)

在上述技术架构的基础上，我们完成了对员工(Employee)实体的自定义字段支持，包括以下功能：

#### 10.1.1 员工表单集成

在员工表单（创建/编辑）中集成了`CustomFieldEditor`组件，实现了：
- 自定义字段Schema选择器
- 根据选择的Schema动态渲染表单字段
- 表单验证与错误提示
- 保存时将自定义字段数据(`extra_value`)和Schema ID(`extra_schema_id`)一并存储

```tsx
// 在employee-form.tsx中添加的核心代码
const [customFieldSchemaId, setCustomFieldSchemaId] = useState<number | null>(null);
const [customFieldValue, setCustomFieldValue] = useState<Record<string, any> | null>(null);

// 表单中添加CustomFieldEditor组件
<CustomFieldEditor
  entityType="employee"
  companyId={companyId}
  schemaId={customFieldSchemaId}
  formData={customFieldValue || undefined}
  onSchemaChange={(id) => setCustomFieldSchemaId(id)}
  onFormDataChange={(data) => setCustomFieldValue(data)}
  disabled={false}
/>

// 提交时包含自定义字段数据
await createOrUpdateEmployee({
  // ...其他员工数据
  extra_value: customFieldValue || null,
  extra_schema_id: customFieldSchemaId || null,
});
```

#### 10.1.2 员工列表展示

在员工列表中展示自定义字段信息：
- 新增"扩展信息"列，显示自定义字段的概要信息
- 使用徽章(Badge)组件标识有自定义字段数据的员工
- 添加工具提示(Tooltip)，悬停时显示更详细的自定义字段数据

#### 10.1.3 员工详情页面

创建了完整的员工详情页，支持查看员工所有信息，包括：
- 基本信息卡片
- 自定义字段数据卡片（只读模式）
- 职位历史记录选项卡
- 附件文档选项卡（预留）

结构如下：
```
/employee/[id]/
├── page.tsx               # 入口页面组件
├── client.tsx             # 客户端详情组件
└── components/
    └── position-history.tsx  # 职位历史组件
```

#### 10.1.4 技术实现要点

1. **路由兼容性**
   - 确保客户端组件使用React Router而非Next.js的路由API，保持项目一致性

2. **数据获取模式**
   - 使用SWR库实现高效的数据获取和缓存策略
   - 添加加载状态和错误处理，提升用户体验

3. **自定义字段渲染**
   - 在只读模式下渲染自定义字段，保证数据格式一致性
   - 根据Schema定义的UI配置调整展示效果

_更新日期: 2025年5月21日_

### 10.2 员工模板自动选择功能 (2025年5月22日)

为了进一步优化用户体验，我们在员工表单中实现了自定义字段模板的自动选择功能：

#### 10.2.1 功能概述

- 员工创建/编辑表单中自动选择员工类型的第一个可用模板
- 隐藏手动模板选择器，简化表单操作流程
- 保留编辑现有员工时的原有模板和数据

#### 10.2.2 实现细节

1. **自动选择逻辑**
   - 在表单打开时自动查询员工类型的模板列表
   - 选择第一个可用的模板应用于新员工
   - 编辑现有员工时保留原有模板设置

2. **组件增强**
   - 增强`CustomFieldEditor`组件，添加`hideSchemaSelector`选项
   - 修改员工表单，隐藏模板选择器，使用自动选择的模板
   - 保留模板切换能力，但默认隐藏以简化界面

#### 10.2.3 实现代码

```tsx
// 自动选择员工模板的辅助hook
function useFirstEmployeeSchema(companyId?: number) {
  const { data } = useSchemaList(
    "employee", 
    { page: 1, limit: 10 },
    companyId,
    true
  );
  return { firstSchemaId: data?.items?.[0]?.id || null };
}

// 在表单打开时自动选择模板
useEffect(() => {
  if (open && !id && firstSchemaId && !customFieldSchemaId) {
    setCustomFieldSchemaId(firstSchemaId);
  }
}, [open, id, firstSchemaId, customFieldSchemaId]);

// 隐藏模板选择器
<CustomFieldEditor
  entityType="employee"
  companyId={companyId}
  schemaId={customFieldSchemaId}
  formData={customFieldValue || undefined}
  onSchemaChange={(id) => setCustomFieldSchemaId(id)}
  onFormDataChange={(data) => setCustomFieldValue(data)}
  hideSchemaSelector={true}
/>
```

_更新日期: 2025年5月22日_

### 10.3 员工信息编辑功能改进 (2025年5月23日)

#### 10.3.1 问题描述
用户在编辑员工信息时发现以下问题：
- 员工表单中存在单一的部门和职位选择，与多职位管理功能冲突。
- 编辑已有员工时，自定义字段的值未能正确加载到表单中。

#### 10.3.2 解决方案
1.  **员工表单 (`employee-form.tsx`) 调整**:
    *   移除员工表单中的 `department_id` 和 `position_id` 字段及其相关逻辑。员工的部门和职位信息通过 `EmployeePositionManager` 组件进行管理，该组件支持为员工关联多个职位，每个职位均包含部门信息。
    *   修复自定义字段加载逻辑：确保在编辑员工时，从 `employee` 或 `initialData` 对象中的 `extra_value` 属性正确加载自定义字段的值到 `customFieldValue` 状态，并传递给 `CustomFieldEditor` 组件。

2.  **员工职位管理 (`EmployeePositionManager.tsx`)**:
    *   该组件已支持多职位管理，无需修改。

#### 10.3.3 预期效果
- 员工表单不再包含单一的部门和职位选择，避免与多职位管理功能混淆。
- 编辑员工时，已填写的自定义字段能够正确显示在表单中。

_更新日期: 2025年5月23日_

## 5. 实现挑战与解决方案

### 5.1 数据验证与类型安全

在自定义字段功能的初始实现中，由于涉及动态的JSON Schema和多种数据类型，导致数据验证和类型安全成为挑战。特别是在处理复杂嵌套结构和数组时，如何确保数据符合预期的Schema定义，成为一个关键问题。

#### 解决方案

我们引入了`jsonschema`库对数据进行严格的JSON Schema验证。同时，在Pydantic模型中使用`Field`和`validator`装饰器，确保字段的类型和约束得到正确应用。

### 5.2 性能优化

在多对多关系的实现中，由于一个实体可能关联多个自定义字段，初期查询性能未达预期，尤其是在数据量较大时，查询速度明显下降。

#### 解决方案

通过在`JsonValueInDB`表的`entity_type`和`entity_id`字段上创建组合索引，显著提升了查询性能。同时，优化了API层的查询逻辑，减少不必要的数据库访问。

### 5.3 版本控制复杂性

Schema的版本控制引入了额外的复杂性，尤其是在处理Schema演变和数据迁移时，如何确保不同版本之间的兼容性成为挑战。

#### 解决方案

通过在Schema中引入`version`和`parent_schema_id`字段，实现对Schema版本的管理。同时，提供了Schema克隆和迁移的API，方便管理员进行Schema的版本升级和数据迁移。

### 5.4 历史数据兼容性处理

#### 问题描述

在实现员工自定义字段功能后，发现历史数据（即在功能实现前创建的员工记录）没有关联的 `extra_schema_id`，导致这些员工的详情无法正确显示自定义字段编辑组件。

#### 解决方案

为了解决这个问题，我们采用了双管齐下的方法：

1. **前端自动适配**：
   在员工表单组件 (`employee-form.tsx`) 中，当加载已存在的员工数据时，如果该员工没有关联 `extra_schema_id`，系统会自动选择当前公司下第一个可用的员工自定义字段模板。这样可以确保在编辑老数据时，自定义字段功能依然可用。
   ```tsx
   // 员工表单组件中的代码片段
   useEffect(() => {
     if (open && (employee || initialData) && id) {
       const data = initialData || employee
       // ...其他表单数据重置代码...

       // 设置自定义字段信息
       if (data?.extra_schema_id) {
         setCustomFieldSchemaId(data.extra_schema_id);
       } else if (firstSchemaId) {
         // 如果员工没有关联的模板，自动选择第一个可用的模板
         // 这样处理之前创建的员工记录
         setCustomFieldSchemaId(firstSchemaId);
         console.log(`为已有员工自动选择模板: ${firstSchemaId}`);
       }

       if (data?.extra_value) {
         setCustomFieldValue(data.extra_value);
       }
     }
     // ...其他逻辑...
   }, [employee, initialData, form, open, id, firstSchemaId, customFieldSchemaId])
   ```

2. **批量数据迁移工具**：
   为了从数据库层面解决历史数据问题，我们创建了一个 Flask CLI 命令 `update_employee_schemas`。该命令位于 `api/commands/update_employee_schemas.py`。

   ```python
   # api/commands/update_employee_schemas.py
   import click
   from sqlalchemy import select, update
   from app import db # 假设您的 Flask app 和 SQLAlchemy 实例可以通过 app 模块导入
   from libs.models import EmployeeInDB, JsonSchemaInDB
   from libs.models.json_schema import SchemaEntityType

   @click.command()
   @click.option('--company-id', type=int, help='需要更新的公司ID。如果不提供，将更新所有公司')
   @click.option('--dry-run', is_flag=True, help='仅显示将要更新的记录数，不实际更新')
   @click.option('--force', is_flag=True, help='强制更新已有 extra_schema_id 的记录')
   def update_employee_schemas(company_id, dry_run, force):
       """为没有 extra_schema_id 的员工记录添加默认的模板ID"""
       click.echo('正在查询需要更新的员工记录...')
       
       # 获取所有的员工模板(按公司分组)
       schema_query = select(JsonSchemaInDB).where(
           JsonSchemaInDB.entity_type == SchemaEntityType.EMPLOYEE
       )
       
       if company_id:
           schema_query = schema_query.where(JsonSchemaInDB.company_id == company_id)
       
       schemas = db.session.execute(schema_query).scalars().all()
       
       schema_by_company = {}
       for schema in schemas:
           company = schema.company_id
           if company not in schema_by_company:
               schema_by_company[company] = []
           schema_by_company[company].append(schema)
       
       total_to_update = 0
       updates_by_company = {}
       
       for comp_id, company_schemas in schema_by_company.items():
           if not company_schemas:
               click.echo(f'公司 ID {comp_id} 没有可用的员工模板，跳过')
               continue
           
           default_schema = company_schemas[0] # 使用第一个模板作为默认模板
           
           employee_query = select(EmployeeInDB).where(
               EmployeeInDB.company_id == comp_id
           )
           
           if not force:
               employee_query = employee_query.where(
                   EmployeeInDB.extra_schema_id == None
               )
           
           employees = db.session.execute(employee_query).scalars().all()
           
           updates_by_company[comp_id] = {
               'schema_id': default_schema.id,
               'employees': employees
           }
           total_to_update += len(employees)
       
       click.echo(f'总共找到 {total_to_update} 条员工记录需要更新')
       for comp_id, data in updates_by_company.items():
           click.echo(f'公司 ID {comp_id}: {len(data["employees"])} 条记录将使用模板 ID {data["schema_id"]}')
       
       if dry_run:
           click.echo('这是一次预演，没有实际更新任何数据')
           return
       
       if not click.confirm('是否继续更新?'):
           click.echo('操作已取消')
           return
       
       for comp_id, data in updates_by_company.items():
           schema_id_to_assign = data['schema_id']
           employees_to_update = data['employees']
           
           if not employees_to_update:
               continue
           
           employee_ids = [e.id for e in employees_to_update]
           
           update_stmt = update(EmployeeInDB).where(
               EmployeeInDB.id.in_(employee_ids)
           ).values(
               extra_schema_id=schema_id_to_assign
           )
           
           db.session.execute(update_stmt)
           click.echo(f'已更新公司 ID {comp_id} 的 {len(employees_to_update)} 条员工记录')
       
       db.session.commit()
       click.echo('所有更新已完成')
   ```

   该工具已在 `api/commands/__init__.py` 中注册，可以通过 Flask CLI 调用。

   ```python
   # api/commands/__init__.py
   # ... 其他导入 ...
   def register_commands(app: "Flask") -> None:
       from . import init_dev_data, upgrade_db, update_employee_schemas # 确保导入
       app.cli.add_command(upgrade_db.command)
       app.cli.add_command(init_dev_data.command)
       app.cli.add_command(update_employee_schemas.update_employee_schemas) # 注册命令
   ```

#### 使用方式

管理员可以在项目API的根目录下，通过终端运行以下命令来更新历史数据：

```bash
# 预演：查看将要更新的记录，不实际执行数据库操作
flask update-employee-schemas --dry-run

# 更新指定公司 (例如公司ID为1) 的员工记录
flask update-employee-schemas --company-id=1

# 强制更新指定公司 (例如公司ID为1) 的员工记录，包括那些已有模板ID的记录
flask update-employee-schemas --company-id=1 --force

# 更新所有公司的员工记录 (仅更新没有模板ID的记录)
flask update-employee-schemas
```

#### 实现效果

通过前端的自动适配和后端的批量迁移工具，我们确保了：
- **用户体验的连续性**：所有员工（无论新旧）在前端编辑时都能无缝使用自定义字段功能。
- **数据完整性**：通过批量工具，可以为历史数据补充必要的 `extra_schema_id`，确保数据的一致性。
- **灵活性和可控性**：管理员可以通过命令行工具灵活地管理历史数据的迁移，并可以选择预演模式来避免误操作。

## 变更记录

- [x] 修复 `employee-form.tsx` 中的自定义字段回显问题。
- [x] 移除 `employee-form.tsx` 中冗余的 `department_id` 和 `position_id` 字段。
- [x] 添加 `timestampToDateObject` 工具函数并在 `employee-form.tsx` 中使用。
- [x] 为 `employee-form.tsx` 中的回调和状态添加类型注解。
- [x] 创建 `candidate-search-dialog.tsx` 组件用于从候选人列表导入员工信息。
- [x] 在 `employee-form.tsx` 中将 `DatePicker` 组件替换为 `Calendar` 组件，并修复相关类型错误。