# 职位管理接口

## 创建或更新职位

创建新职位或更新现有职位信息。

- **接口地址**: `/position/insert`
- **请求方式**: `POST`
- **请求参数**:

```typescript
{
    id?: number;           // 职位ID（更新时必填）
    name: string;          // 职位名称
    company_id: number;    // 所属公司ID
    remark?: string;       // 备注
}
```

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 职位ID
        name: string;      // 职位名称
        company_id: number;// 所属公司ID
        remark?: string;   // 备注
        created_at: string;// 创建时间
        updated_at: string;// 更新时间
    }
}
```

## 获取职位列表

获取指定公司的职位列表。

- **接口地址**: `/position/list/:company_id`
- **请求方式**: `GET`
- **路径参数**:
  - `company_id`: 公司ID
- **查询参数**:

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
            id: number;        // 职位ID
            name: string;      // 职位名称
            company_id: number;// 所属公司ID
            remark?: string;   // 备注
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

## 搜索职位

根据名称搜索职位。

- **接口地址**: `/position/search/:company_id`
- **请求方式**: `GET`
- **路径参数**:
  - `company_id`: 公司ID
- **查询参数**:

```typescript
{
    name: string;      // 搜索关键词
    page?: number;     // 页码，默认1
    limit?: number;    // 每页数量，默认20
}
```

- **响应结果**: 同获取职位列表

## 获取职位详情

获取指定职位的详细信息。

- **接口地址**: `/position/get/:id`
- **请求方式**: `GET`
- **路径参数**:
  - `id`: 职位ID

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 职位ID
        name: string;      // 职位名称
        company_id: number;// 所属公司ID
        remark?: string;   // 备注
        created_at: string;// 创建时间
        updated_at: string;// 更新时间
    }
}
```

## 删除职位

删除指定的职位。

- **接口地址**: `/position/delete/:id`
- **请求方式**: `POST`
- **路径参数**:
  - `id`: 职位ID

- **响应结果**:

```typescript
{
    code: number;      // 状态码
    message: string;   // 状态信息
}
``` 