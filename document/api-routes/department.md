# 部门管理接口文档

本文档描述了HR系统的部门管理相关接口，包括部门的创建、更新、查询和删除等功能。

## 基础信息

- 基础路径: `/department`
- 内容类型: `application/json`
- 认证要求: 所有接口都需要用户先登录

## 接口列表

### 1. 创建或更新部门

**请求**

```http
POST /api/department/insert
Content-Type: application/json
Authorization: <token>
```

**请求参数**

| 参数名     | 类型    | 必须 | 描述                                 |
| ---------- | ------- | ---- | ------------------------------------ |
| id         | integer | 否   | 部门ID，更新时必须提供，创建时不提供 |
| name       | string  | 是   | 部门名称                             |
| company_id | integer | 是   | 所属公司ID                           |
| parent_id  | integer | 否   | 父部门ID，如为顶级部门则不提供       |
| leader_id  | integer | 否   | 部门负责人ID                         |
| remark     | string  | 否   | 备注信息                             |

**创建部门请求示例**

```json
{
  "name": "技术部",
  "company_id": 1,
  "parent_id": null,
  "leader_id": 5,
  "remark": "负责公司技术相关事务"
}
```

**更新部门请求示例**

```json
{
  "id": 2,
  "name": "研发部",
  "company_id": 1,
  "parent_id": 1,
  "leader_id": 8,
  "remark": "负责产品研发"
}
```

**响应**

| 状态码 | 描述           |
| ------ | -------------- |
| 200    | 请求成功       |
| 400    | 请求参数错误   |
| 403    | 权限不足       |
| 500    | 服务器内部错误 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 2,
    "name": "研发部",
    "company_id": 1,
    "parent_id": 1,
    "leader_id": 8,
    "remark": "负责产品研发",
    "created_at": "2024-04-25T10:30:00",
    "updated_at": "2024-04-30T15:45:22"
  }
}
```

### 2. 获取部门列表

**请求**

```http
GET /api/department/list/{company_id}?page=1&limit=10
Authorization: <token>
```

**请求参数**

| 参数名     | 位置 | 类型    | 必须 | 描述               |
| ---------- | ---- | ------- | ---- | ------------------ |
| company_id | 路径 | integer | 是   | 公司ID             |
| page       | 查询 | integer | 否   | 页码，默认为1      |
| limit      | 查询 | integer | 否   | 每页条数，默认为10 |

**响应**

| 状态码 | 描述           |
| ------ | -------------- |
| 200    | 请求成功       |
| 403    | 权限不足       |
| 500    | 服务器内部错误 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "总部",
        "company_id": 1,
        "parent_id": null,
        "leader_id": 1,
        "remark": "公司总部",
        "created_at": "2024-04-20T09:00:00",
        "updated_at": "2024-04-20T09:00:00"
      },
      {
        "id": 2,
        "name": "研发部",
        "company_id": 1,
        "parent_id": 1,
        "leader_id": 8,
        "remark": "负责产品研发",
        "created_at": "2024-04-25T10:30:00",
        "updated_at": "2024-04-30T15:45:22"
      }
    ],
    "total": 10,
    "page": 1,
    "limit": 10
  }
}
```

### 3. 搜索部门

**请求**

```http
GET /api/department/search/{company_id}?name=研发&page=1&limit=10
Authorization: <token>
```

**请求参数**

| 参数名     | 位置 | 类型    | 必须 | 描述               |
| ---------- | ---- | ------- | ---- | ------------------ |
| company_id | 路径 | integer | 是   | 公司ID             |
| name       | 查询 | string  | 是   | 部门名称关键词     |
| page       | 查询 | integer | 否   | 页码，默认为1      |
| limit      | 查询 | integer | 否   | 每页条数，默认为10 |

**响应**

| 状态码 | 描述           |
| ------ | -------------- |
| 200    | 请求成功       |
| 403    | 权限不足       |
| 500    | 服务器内部错误 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 2,
        "name": "研发部",
        "company_id": 1,
        "parent_id": 1,
        "leader_id": 8,
        "remark": "负责产品研发",
        "created_at": "2024-04-25T10:30:00",
        "updated_at": "2024-04-30T15:45:22"
      },
      {
        "id": 5,
        "name": "产品研发部",
        "company_id": 1,
        "parent_id": 2,
        "leader_id": 12,
        "remark": "负责产品设计和研发",
        "created_at": "2024-04-26T11:20:00",
        "updated_at": "2024-04-26T11:20:00"
      }
    ],
    "total": 2,
    "page": 1,
    "limit": 10
  }
}
```

### 4. 获取部门详情

**请求**

```http
GET /api/department/get/{department_id}
Authorization: <token>
```

**请求参数**

| 参数名        | 位置 | 类型    | 必须 | 描述   |
| ------------- | ---- | ------- | ---- | ------ |
| department_id | 路径 | integer | 是   | 部门ID |

**响应**

| 状态码 | 描述           |
| ------ | -------------- |
| 200    | 请求成功       |
| 403    | 权限不足       |
| 404    | 部门不存在     |
| 500    | 服务器内部错误 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 2,
    "name": "研发部",
    "company_id": 1,
    "parent_id": 1,
    "leader_id": 8,
    "remark": "负责产品研发",
    "created_at": "2024-04-25T10:30:00",
    "updated_at": "2024-04-30T15:45:22"
  }
}
```

### 5. 删除部门

**请求**

```http
POST /api/department/delete/{department_id}
Authorization: <token>
```

**请求参数**

| 参数名        | 位置 | 类型    | 必须 | 描述   |
| ------------- | ---- | ------- | ---- | ------ |
| department_id | 路径 | integer | 是   | 部门ID |

**响应**

| 状态码 | 描述           |
| ------ | -------------- |
| 200    | 请求成功       |
| 403    | 权限不足       |
| 404    | 部门不存在     |
| 500    | 服务器内部错误 |

**响应示例**

```json
{
  "code": 200,
  "message": "部门删除成功",
  "data": null
}
```

## 数据模型

### 部门模型 (Department)

| 字段名     | 类型     | 描述                         |
| ---------- | -------- | ---------------------------- |
| id         | integer  | 部门ID（主键）               |
| name       | string   | 部门名称                     |
| company_id | integer  | 所属公司ID（外键）           |
| parent_id  | integer  | 父部门ID（外键），可为空     |
| leader_id  | integer  | 部门负责人ID（外键），可为空 |
| remark     | string   | 备注信息，可为空             |
| created_at | datetime | 创建时间                     |
| updated_at | datetime | 更新时间                     |

## 注意事项

1. 所有接口需要用户先登录才能访问
2. 用户只能访问其有权限的公司下的部门
3. 删除部门时需要考虑该部门是否有关联的子部门或员工
4. 创建部门时，如果指定了父部门，系统会验证父部门是否存在且属于同一公司