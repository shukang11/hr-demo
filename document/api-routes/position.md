# 职位管理接口文档

本文档描述了HR系统的职位管理相关接口，包括职位的创建、更新、查询和删除等功能。

## 基础信息

- 基础路径: `/position`
- 内容类型: `application/json`
- 认证要求: 所有接口都需要用户先登录

## 接口列表

### 1. 创建或更新职位

**接口描述**: 创建新职位或更新现有职位信息

- **URL**: `/position/create`
- **方法**: `POST`
- **请求体**:

```json
{
  "id": 1,             // 可选，如果提供则表示更新现有职位
  "name": "职位名称",    // 必填，职位名称
  "company_id": 1,     // 必填，所属公司ID
  "remark": "职位描述"   // 可选，职位描述文本
}
```

- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 1,
    "name": "职位名称",
    "company_id": 1,
    "remark": "职位描述",
    "created_at": "2025-04-29T10:00:00Z",
    "updated_at": "2025-04-29T10:00:00Z"
  }
}
```

- **错误响应**:
  - `400 Bad Request`: 请求数据无效
  - `403 Forbidden`: 无权限执行此操作
  - `404 Not Found`: 更新时职位不存在或无访问权限
  - `500 Internal Server Error`: 服务器内部错误

### 2. 获取职位列表

**接口描述**: 获取指定公司的所有职位列表，支持分页

- **URL**: `/position/list/{company_id}`
- **方法**: `GET`
- **URL参数**:
  - `company_id`: 公司ID
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
        "name": "职位名称",
        "company_id": 1,
        "remark": "职位描述",
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
  - `403 Forbidden`: 无权限访问此公司
  - `500 Internal Server Error`: 服务器内部错误

### 3. 搜索职位

**接口描述**: 根据名称搜索指定公司中的职位，支持分页

- **URL**: `/position/search/{company_id}`
- **方法**: `GET`
- **URL参数**:
  - `company_id`: 公司ID
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
        "name": "职位名称",
        "company_id": 1,
        "remark": "职位描述",
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
  - `403 Forbidden`: 无权限访问此公司
  - `500 Internal Server Error`: 服务器内部错误

### 4. 获取职位详情

**接口描述**: 获取指定职位的详细信息

- **URL**: `/position/get/{id}`
- **方法**: `GET`
- **URL参数**:
  - `id`: 职位ID
- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 1,
    "name": "职位名称",
    "company_id": 1,
    "remark": "职位描述",
    "created_at": "2025-04-29T10:00:00Z",
    "updated_at": "2025-04-29T10:00:00Z"
  }
}
```

- **错误响应**:
  - `401 Unauthorized`: 未登录
  - `403 Forbidden`: 无权限访问此职位
  - `404 Not Found`: 职位不存在
  - `500 Internal Server Error`: 服务器内部错误

### 5. 删除职位

**接口描述**: 删除指定的职位

- **URL**: `/position/delete/{id}`
- **方法**: `POST`
- **URL参数**:
  - `id`: 职位ID
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
  - `403 Forbidden`: 无权限删除此职位
  - `404 Not Found`: 职位不存在或已被删除
  - `500 Internal Server Error`: 服务器内部错误

## 数据模型

### 职位基础信息 (PositionBase)

| 字段       | 类型   | 必填 | 描述       |
| ---------- | ------ | ---- | ---------- |
| name       | string | 是   | 职位名称   |
| company_id | number | 是   | 所属公司ID |
| remark     | string | 否   | 职位描述   |

### 职位创建请求 (PositionCreate)

继承自 PositionBase，无额外字段。

### 职位更新请求 (PositionUpdate)

| 字段   | 类型   | 必填 | 描述     |
| ------ | ------ | ---- | -------- |
| name   | string | 否   | 职位名称 |
| remark | string | 否   | 职位描述 |

### 职位响应模型 (PositionSchema)

| 字段       | 类型   | 描述                   |
| ---------- | ------ | ---------------------- |
| id         | number | 职位唯一标识符         |
| name       | string | 职位名称               |
| company_id | number | 所属公司ID             |
| remark     | string | 职位描述，可能为null   |
| created_at | string | 创建时间，ISO 8601格式 |
| updated_at | string | 更新时间，ISO 8601格式 |

## 注意事项

1. 所有接口需要用户先登录才能访问
2. 用户只能访问其有权限的公司下的职位
3. 删除职位时需要考虑该职位是否有关联的员工或候选人