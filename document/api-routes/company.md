# 公司管理接口文档

本文档描述了HR系统的公司管理相关接口，包括公司的创建、更新、查询和删除等功能。

## 基础信息

- 基础路径: `/company`
- 内容类型: `application/json`
- 认证要求: 所有接口都需要用户先登录

## 接口列表

### 1. 创建或更新公司

**接口描述**: 创建新公司或更新现有公司信息

- **URL**: `/company/insert`
- **方法**: `POST`
- **请求体**:

```json
{
  "id": 1,             // 可选，如果提供则表示更新现有公司
  "name": "公司名称",    // 必填，公司名称
  "extra_value": {},   // 可选，附加JSON数据
  "extra_schema_id": 1, // 可选，关联的JSON Schema ID
  "description": "公司描述" // 可选，公司描述文本
}
```

- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 1,
    "name": "公司名称",
    "extra_value": {},
    "extra_schema_id": 1,
    "description": "公司描述",
    "created_at": "2025-04-29T10:00:00Z",
    "updated_at": "2025-04-29T10:00:00Z"
  }
}
```

- **错误响应**:
  - `400 Bad Request`: 请求数据无效
  - `403 Forbidden`: 无权限执行此操作
  - `404 Not Found`: 更新时公司不存在或无访问权限 
  - `500 Internal Server Error`: 服务器内部错误

### 2. 获取公司列表

**接口描述**: 获取用户有权访问的公司列表，支持分页

- **URL**: `/company/list`
- **方法**: `GET`
- **查询参数**:
  - `page`: 当前页码，默认为1
  - `limit`: 每页显示数量，默认为10
- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "公司名称",
        "extra_value": {},
        "extra_schema_id": 1,
        "description": "公司描述",
        "created_at": "2025-04-29T10:00:00Z",
        "updated_at": "2025-04-29T10:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 10
  }
}
```

- **错误响应**:
  - `401 Unauthorized`: 未登录
  - `500 Internal Server Error`: 服务器内部错误

### 3. 搜索公司

**接口描述**: 根据名称搜索公司，支持分页

- **URL**: `/company/search`
- **方法**: `GET`
- **查询参数**:
  - `name`: 搜索关键词 
  - `page`: 当前页码，默认为1
  - `limit`: 每页显示数量，默认为10
- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "公司名称",
        "extra_value": {},
        "extra_schema_id": 1,
        "description": "公司描述",
        "created_at": "2025-04-29T10:00:00Z",
        "updated_at": "2025-04-29T10:00:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "limit": 10
  }
}
```

- **错误响应**:
  - `401 Unauthorized`: 未登录
  - `500 Internal Server Error`: 服务器内部错误

### 4. 获取公司详情

**接口描述**: 获取指定公司的详细信息

- **URL**: `/company/{id}`
- **方法**: `GET`
- **URL参数**:
  - `id`: 公司ID
- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 1,
    "name": "公司名称",
    "extra_value": {},
    "extra_schema_id": 1,
    "description": "公司描述",
    "created_at": "2025-04-29T10:00:00Z",
    "updated_at": "2025-04-29T10:00:00Z"
  }
}
```

- **错误响应**:
  - `401 Unauthorized`: 未登录 
  - `403 Forbidden`: 无权限访问此公司
  - `404 Not Found`: 公司不存在
  - `500 Internal Server Error`: 服务器内部错误

### 5. 删除公司

**接口描述**: 删除指定的公司

- **URL**: `/company/{id}`
- **方法**: `DELETE`
- **URL参数**:
  - `id`: 公司ID
- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": null
}
```

- **错误响应**:
  - `401 Unauthorized`: 未登录
  - `403 Forbidden`: 无权限删除此公司
  - `404 Not Found`: 公司不存在或已被删除
  - `500 Internal Server Error`: 服务器内部错误

## 数据模型

### 公司基础信息 (CompanyBase)

| 字段            | 类型   | 必填 | 描述                 |
| --------------- | ------ | ---- | -------------------- |
| name            | string | 是   | 公司名称             |
| extra_value     | object | 否   | 附加JSON格式数据     |
| extra_schema_id | number | 否   | 关联的JSON Schema ID |
| description     | string | 否   | 公司描述             |

### 公司创建请求 (CompanyCreate)

继承自 CompanyBase，无额外字段。

### 公司更新请求 (CompanyUpdate)

| 字段            | 类型   | 必填 | 描述                 |
| --------------- | ------ | ---- | -------------------- |
| name            | string | 否   | 公司名称             |
| extra_value     | object | 否   | 附加JSON格式数据     |
| extra_schema_id | number | 否   | 关联的JSON Schema ID |
| description     | string | 否   | 公司描述             |

### 公司响应模型 (CompanySchema)

| 字段            | 类型   | 描述                   |
| --------------- | ------ | ---------------------- |
| id              | number | 公司唯一标识符         |
| name            | string | 公司名称               |
| extra_value     | object | 附加JSON格式数据       |
| extra_schema_id | number | 关联的JSON Schema ID   |
| description     | string | 公司描述               |
| created_at      | string | 创建时间，ISO 8601格式 |
| updated_at      | string | 更新时间，ISO 8601格式 |

## 注意事项

1. 所有接口需要用户先登录才能访问
2. 用户只能访问其有权限的公司
3. 删除公司会级联删除与该公司相关的所有数据，请谨慎操作