# 用户认证接口文档

本文档描述了HR系统的用户认证相关接口，包括登录、登出和获取用户信息等功能。

## 基础信息

- 基础路径: `/auth`
- 内容类型: `application/json`

## 接口列表

### 1. 用户登录

**接口描述**: 处理用户的登录请求，验证用户名和密码，生成认证令牌

- **URL**: `/auth/login`
- **方法**: `POST`
- **请求体**:

```json
{
  "username": "用户名", // 用户名，与email至少提供一个
  "email": "user@example.com", // 电子邮箱，与username至少提供一个
  "password_hashed": "密码哈希值" // 使用SHA256哈希后的密码，至少6个字符
}
```

- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "token": "用户认证令牌",
    "user": {
      "id": 1,
      "username": "用户名",
      "email": "user@example.com",
      "gender": 0, // 0-未知, 1-男, 2-女
      "phone": "手机号码" // 可能为null
    }
  }
}
```

- **错误响应**:
  - `400 Bad Request`: 请求数据无效
  - `401 Unauthorized`: 用户名或密码错误
  - `500 Internal Server Error`: 服务器内部错误

### 2. 用户登出

**接口描述**: 处理用户的登出请求，清除认证令牌

- **URL**: `/auth/logout`
- **方法**: `POST`
- **请求体**: 无需请求体
- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": null
}
```

### 3. 获取用户信息

**接口描述**: 获取当前登录用户的详细信息

- **URL**: `/auth/info`
- **方法**: `GET`
- **请求头**:
  - 需要包含有效的认证令牌（通过Cookie或其他方式提供）
- **成功响应** (200 OK):

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 1,
    "username": "用户名",
    "email": "user@example.com",
    "gender": 0, // 0-未知, 1-男, 2-女
    "phone": "手机号码" // 可能为null
  }
}
```

- **错误响应**:
  - `401 Unauthorized`: 未登录或令牌无效

## 数据模型

### 登录请求 (LoginRequest)

| 字段            | 类型   | 必填 | 描述                               |
| --------------- | ------ | ---- | ---------------------------------- |
| username        | string | 否*  | 用户名 (*与email至少一个必填)      |
| email           | string | 否*  | 电子邮箱 (*与username至少一个必填) |
| password_hashed | string | 是   | 密码哈希值，至少6个字符            |

### 登录响应 (LoginResponse)

| 字段  | 类型          | 描述         |
| ----- | ------------- | ------------ |
| token | string        | 用户认证令牌 |
| user  | AccountSchema | 用户信息对象 |

### 用户信息 (AccountSchema)

| 字段     | 类型   | 描述                      |
| -------- | ------ | ------------------------- |
| id       | number | 用户唯一标识符            |
| username | string | 用户名                    |
| email    | string | 电子邮箱                  |
| gender   | number | 性别 (0-未知, 1-男, 2-女) |
| phone    | string | 手机号码，可能为null      |

## 注意事项

1. 所有接口返回的HTTP状态码都会与响应体中的状态码保持一致
2. 登录后会在服务器端记录用户session，后续请求会自动识别用户身份
3. 用户信息接口需要用户先登录才能访问