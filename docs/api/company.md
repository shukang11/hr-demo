# 公司管理接口

## 状态码说明

- 200: 成功
- 400: 请求参数错误
- 500: 服务器内部错误

## 错误响应

当发生错误时，响应格式如下：

```typescript
{
    code: number;      // 状态码
    message: string;   // 错误信息
    data?: any;        // 可能的额外错误信息
}
```

常见错误：
- 创建公司时重复的公司名称
- 更新或删除时公司ID不存在
- 服务器内部错误

## 创建或更新公司

创建新公司或更新现有公司信息。

- **接口地址**: `/company/insert`
- **请求方式**: `POST`
- **请求参数**:

```typescript
{
    id?: number;           // 公司ID（更新时必填）
    name: string;          // 公司名称（必填，且在同一系统中唯一）
    extra_value?: {        // 额外字段值（JSON）
        description?: string;  // 公司描述
        address?: string;      // 公司地址
        website?: string;      // 公司网站
        phone?: string;        // 联系电话
        email?: string;        // 联系邮箱
        [key: string]: any;    // 其他自定义字段
    };
    extra_schema_id?: number;  // 额外字段模式ID
}
```

- **响应结果**:

```typescript
{
    code: number;          // 状态码（200表示成功）
    message: string;       // 状态信息
    data: {
        id: number;        // 公司ID
        name: string;      // 公司名称
        extra_value?: any; // 额外字段值
        created_at: string;// 创建时间（格式：YYYY-MM-DD HH:mm:ss）
        updated_at: string;// 更新时间（格式：YYYY-MM-DD HH:mm:ss）
    }
}
```

- **错误情况**:
  - 400: 公司名称已存在
  - 400: 请求参数格式错误
  - 500: 服务器内部错误

## 获取公司列表

分页获取公司列表。

- **接口地址**: `/company/list`
- **请求方式**: `GET`
- **请求参数**:

```typescript
{
    page?: number;     // 页码，默认1
    limit?: number;    // 每页数量，默认20
}
```

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        items: Array<{
            id: number;        // 公司ID
            name: string;      // 公司名称
            extra_value?: any; // 额外字段值
            created_at: string;// 创建时间
            updated_at: string;// 更新时间
        }>;
        total: number;     // 总记录数
        page: number;      // 当前页码
        limit: number;     // 每页数量
        total_pages: number; // 总页数
    }
}
```

## 搜索公司

根据名称搜索公司。

- **接口地址**: `/company/search`
- **请求方式**: `GET`
- **请求参数**:

```typescript
{
    name: string;      // 搜索关键词
    page?: number;     // 页码，默认1
    limit?: number;    // 每页数量，默认20
}
```

- **响应结果**: 同获取公司列表

## 获取公司详情

获取指定公司的详细信息。

- **接口地址**: `/company/:id`
- **请求方式**: `GET`
- **路径参数**:
  - `id`: 公司ID

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 公司ID
        name: string;      // 公司名称
        extra_value?: any; // 额外字段值
        created_at: string;// 创建时间
        updated_at: string;// 更新时间
    }
}
```

## 删除公司

删除指定的公司。

- **接口地址**: `/company/:id`
- **请求方式**: `DELETE`
- **路径参数**:
  - `id`: 公司ID

- **响应结果**:

```typescript
{
    code: number;      // 状态码
    message: string;   // 状态信息
}
``` 