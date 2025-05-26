# 候选人管理接口文档

本文档描述了HR系统的候选人管理相关接口，包括候选人的创建、更新、状态管理、查询和删除等功能。

## 基础信息

- 基础路径: `/candidate`
- 内容类型: `application/json`
- 认证要求: 所有接口都需要用户先登录

## 接口列表

### 1. 创建或更新候选人

**接口描述**: 创建新候选人或更新现有候选人信息

- **URL**: `/candidate/insert`
- **方法**: `POST`
- **请求体**:

```json
{
  "id": 1,                  // 可选，如果提供则表示更新现有候选人
  "company_id": 1,          // 必填，所属公司ID
  "name": "张三",            // 必填，候选人姓名
  "phone": "13800138000",   // 可选，联系电话
  "email": "zhangsan@example.com", // 可选，电子邮箱
  "position_id": 2,         // 必填，应聘职位ID
  "department_id": 3,       // 必填，目标部门ID
  "interview_date": "2025-05-15T14:30:00Z", // 可选，面试日期
  "interviewer_id": 5,      // 可选，面试官ID
  "remark": "通过内部推荐",   // 可选，备注信息
  "extra_value": {},        // 可选，附加JSON格式数据
  "extra_schema_id": 1      // 可选，关联的JSON Schema ID
}
```

- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 1,
    "company_id": 1,
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "position_id": 2,
    "department_id": 3,
    "interview_date": "2025-05-15T14:30:00Z",
    "status": "Pending",
    "interviewer_id": 5,
    "evaluation": null,
    "remark": "通过内部推荐",
    "extra_value": {},
    "extra_schema_id": 1,
    "created_at": "2025-04-29T10:00:00Z",
    "updated_at": "2025-04-29T10:00:00Z"
  }
}
```

- **错误响应**:
  - `400 Bad Request`: 请求数据无效
  - `403 Forbidden`: 无权限执行此操作
  - `404 Not Found`: 更新时候选人不存在或无访问权限
  - `500 Internal Server Error`: 服务器内部错误

### 2. 更新候选人状态

**接口描述**: 更新候选人的状态、评价和备注信息

- **URL**: `/candidate/{id}/status`
- **方法**: `POST`
- **URL参数**:
  - `id`: 候选人ID
- **请求体**:

```json
{
  "status": "Interviewed",       // 必填，候选人状态（Pending, Scheduled, Interviewed, Accepted, Rejected, Withdrawn）
  "evaluation": "面试表现良好",    // 可选，面试评价
  "remark": "建议进入下一轮面试"    // 可选，备注信息
}
```

- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 1,
    "company_id": 1,
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "position_id": 2,
    "department_id": 3,
    "interview_date": "2025-05-15T14:30:00Z",
    "status": "Interviewed",
    "interviewer_id": 5,
    "evaluation": "面试表现良好",
    "remark": "建议进入下一轮面试",
    "extra_value": {},
    "extra_schema_id": 1,
    "created_at": "2025-04-29T10:00:00Z",
    "updated_at": "2025-04-29T11:30:00Z"
  }
}
```

- **错误响应**:
  - `400 Bad Request`: 请求数据无效
  - `403 Forbidden`: 无权限更新此候选人状态
  - `404 Not Found`: 候选人不存在
  - `500 Internal Server Error`: 服务器内部错误

### 3. 获取候选人列表

**接口描述**: 获取指定公司的候选人列表，支持分页、状态筛选和搜索

- **URL**: `/candidate/list/{company_id}`
- **方法**: `GET`
- **URL参数**:
  - `company_id`: 公司ID
- **查询参数**:
  - `page`: 当前页码，默认为1
  - `limit`: 每页显示数量，默认为10
  - `status`: 可选的状态筛选 (Pending, Scheduled, Interviewed, Accepted, Rejected, Withdrawn)
  - `search`: 可选的搜索关键词（按姓名搜索）
- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "items": [
      {
        "id": 1,
        "company_id": 1,
        "name": "张三",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "position_id": 2,
        "department_id": 3,
        "interview_date": "2025-05-15T14:30:00Z",
        "status": "Interviewed",
        "interviewer_id": 5,
        "evaluation": "面试表现良好",
        "remark": "建议进入下一轮面试",
        "extra_value": {},
        "extra_schema_id": 1,
        "created_at": "2025-04-29T10:00:00Z",
        "updated_at": "2025-04-29T11:30:00Z"
      }
    ],
    "total": 25,
    "page": 1,
    "limit": 10
  }
}
```

- **错误响应**:
  - `400 Bad Request`: 无效的状态值
  - `401 Unauthorized`: 未登录
  - `403 Forbidden`: 无权限访问此公司
  - `500 Internal Server Error`: 服务器内部错误

### 4. 获取候选人详情

**接口描述**: 获取指定候选人的详细信息

- **URL**: `/candidate/get/{id}`
- **方法**: `GET`
- **URL参数**:
  - `id`: 候选人ID
- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 1,
    "company_id": 1,
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "position_id": 2,
    "department_id": 3,
    "interview_date": "2025-05-15T14:30:00Z",
    "status": "Interviewed",
    "interviewer_id": 5,
    "evaluation": "面试表现良好",
    "remark": "建议进入下一轮面试",
    "extra_value": {},
    "extra_schema_id": 1,
    "created_at": "2025-04-29T10:00:00Z",
    "updated_at": "2025-04-29T11:30:00Z"
  }
}
```

- **错误响应**:
  - `401 Unauthorized`: 未登录
  - `403 Forbidden`: 无权限访问此候选人
  - `404 Not Found`: 候选人不存在
  - `500 Internal Server Error`: 服务器内部错误

### 5. 删除候选人

**接口描述**: 删除指定的候选人

- **URL**: `/candidate/delete/{id}`
- **方法**: `POST`
- **URL参数**:
  - `id`: 候选人ID
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
  - `403 Forbidden`: 无权限删除此候选人
  - `404 Not Found`: 候选人不存在或已被删除
  - `500 Internal Server Error`: 服务器内部错误

## 数据模型

### 候选人状态枚举 (CandidateStatus)

| 值          | 描述       |
| ----------- | ---------- |
| Pending     | 待处理     |
| Scheduled   | 已安排面试 |
| Interviewed | 已面试     |
| Accepted    | 已通过     |
| Rejected    | 已拒绝     |
| Withdrawn   | 已撤回     |

### 候选人基础信息 (CandidateBase)

| 字段            | 类型   | 必填 | 描述                   |
| --------------- | ------ | ---- | ---------------------- |
| company_id      | number | 是   | 所属公司ID             |
| name            | string | 是   | 候选人姓名             |
| phone           | string | 否   | 联系电话               |
| email           | string | 否   | 电子邮箱               |
| position_id     | number | 是   | 应聘职位ID             |
| department_id   | number | 是   | 目标部门ID             |
| interview_date  | string | 否   | 面试日期，ISO 8601格式 |
| interviewer_id  | number | 否   | 面试官ID               |
| remark          | string | 否   | 备注信息               |
| extra_value     | object | 否   | 附加JSON格式数据       |
| extra_schema_id | number | 否   | 关联的JSON Schema ID   |

### 候选人创建请求 (CandidateCreate)

继承自 CandidateBase，并添加：

| 字段   | 类型   | 必填 | 描述                         |
| ------ | ------ | ---- | ---------------------------- |
| status | string | 否   | 候选人状态，默认为 "Pending" |

### 候选人更新请求 (CandidateUpdate)

所有字段均为可选：

| 字段            | 类型   | 必填 | 描述                 |
| --------------- | ------ | ---- | -------------------- |
| name            | string | 否   | 候选人姓名           |
| phone           | string | 否   | 联系电话             |
| email           | string | 否   | 电子邮箱             |
| position_id     | number | 否   | 应聘职位ID           |
| department_id   | number | 否   | 目标部门ID           |
| interview_date  | string | 否   | 面试日期             |
| interviewer_id  | number | 否   | 面试官ID             |
| remark          | string | 否   | 备注信息             |
| extra_value     | object | 否   | 附加JSON格式数据     |
| extra_schema_id | number | 否   | 关联的JSON Schema ID |

### 候选人状态更新请求 (CandidateStatusUpdate)

| 字段       | 类型   | 必填 | 描述       |
| ---------- | ------ | ---- | ---------- |
| status     | string | 是   | 候选人状态 |
| evaluation | string | 否   | 面试评价   |
| remark     | string | 否   | 备注信息   |

### 候选人响应模型 (CandidateSchema)

继承自 CandidateBase，并添加：

| 字段       | 类型   | 描述                   |
| ---------- | ------ | ---------------------- |
| id         | number | 候选人唯一标识符       |
| status     | string | 候选人状态             |
| evaluation | string | 面试评价，可能为null   |
| created_at | string | 创建时间，ISO 8601格式 |
| updated_at | string | 更新时间，ISO 8601格式 |

## 注意事项

1. 所有接口需要用户先登录才能访问
2. 用户只能访问其有权限的公司下的候选人数据
3. 状态更新操作应遵循合理的流程（例如，已拒绝的候选人不应再更改为待处理）
4. 面试日期格式应符合ISO 8601标准 (例如：2025-05-15T14:30:00Z)