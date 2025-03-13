# 部门管理接口

## 创建或更新部门

创建新部门或更新现有部门信息。

- **接口地址**: `/department/insert`
- **请求方式**: `POST`
- **请求参数**:

```typescript
{
    id?: number;           // 部门ID（更新时必填）
    name: string;          // 部门名称
    company_id: number;    // 所属公司ID
    parent_id?: number;    // 父部门ID
    leader_id?: number;    // 部门负责人ID
    remark?: string;       // 备注
}
```

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 部门ID
        name: string;      // 部门名称
        company_id: number;// 所属公司ID
        parent_id?: number;// 父部门ID
        leader_id?: number;// 部门负责人ID
        remark?: string;   // 备注
        created_at: string;// 创建时间
        updated_at: string;// 更新时间
    }
}
```

## 获取部门列表

获取指定公司的部门列表。

- **接口地址**: `/department/list/:company_id`
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
            id: number;        // 部门ID
            name: string;      // 部门名称
            company_id: number;// 所属公司ID
            parent_id?: number;// 父部门ID
            leader_id?: number;// 部门负责人ID
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

## 搜索部门

根据名称搜索部门。

- **接口地址**: `/department/search/:company_id`
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

- **响应结果**: 同获取部门列表

## 获取部门详情

获取指定部门的详细信息。

- **接口地址**: `/department/get/:id`
- **请求方式**: `GET`
- **路径参数**:
  - `id`: 部门ID

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 部门ID
        name: string;      // 部门名称
        company_id: number;// 所属公司ID
        parent_id?: number;// 父部门ID
        leader_id?: number;// 部门负责人ID
        remark?: string;   // 备注
        created_at: string;// 创建时间
        updated_at: string;// 更新时间
    }
}
```

## 删除部门

删除指定的部门。

- **接口地址**: `/department/delete/:id`
- **请求方式**: `POST`
- **路径参数**:
  - `id`: 部门ID

- **响应结果**:

```typescript
{
    code: number;      // 状态码
    message: string;   // 状态信息
}
``` 