# 员工管理接口

## 创建或更新员工

创建新员工或更新现有员工信息。

- **接口地址**: `/employee/insert`
- **请求方式**: `POST`
- **请求参数**:

```typescript
{
    id?: number;           // 员工ID（更新时必填）
    company_id: number;    // 公司ID
    name: string;          // 员工姓名
    email?: string;        // 电子邮箱
    phone?: string;        // 电话号码
    birthdate?: string;    // 出生日期（格式：YYYY-MM-DD HH:mm:ss）
    address?: string;      // 地址
    gender: "Male" | "Female" | "Unknown"; // 性别
    department_id?: number; // 部门ID
    position_id?: number;   // 职位ID
    entry_date?: string;    // 入职日期（格式：YYYY-MM-DD HH:mm:ss）
    candidate_id?: number;  // 候选人ID
    extra_value?: {        // 额外字段值（JSON）
        education?: string; // 学历
        work_years?: number; // 工作年限
        source?: string;    // 来源
        [key: string]: any; // 其他自定义字段
    };
    extra_schema_id?: number; // 额外字段模式ID
}
```

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 员工ID
        company_id: number;// 公司ID
        name: string;      // 员工姓名
        email?: string;    // 电子邮箱
        phone?: string;    // 电话号码
        birthdate?: string;// 出生日期
        address?: string;  // 地址
        gender: string;    // 性别
        department_id?: number; // 部门ID
        position_id?: number;   // 职位ID
        extra_value?: any; // 额外字段值
        created_at: string;// 创建时间
        updated_at: string;// 更新时间
    }
}
```

## 添加员工职位

为员工添加新的职位。

- **接口地址**: `/employee/position/add`
- **请求方式**: `POST`
- **请求参数**:

```typescript
{
    employee_id: number;   // 员工ID
    company_id: number;    // 公司ID
    department_id: number; // 部门ID
    position_id: number;   // 职位ID
    entry_at: string;      // 入职时间（格式：YYYY-MM-DD HH:mm:ss）
    remark?: string;       // 备注
}
```

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 记录ID
        employee_id: number; // 员工ID
        company_id: number;  // 公司ID
        department_id: number; // 部门ID
        position_id: number;   // 职位ID
        entry_at: string;    // 入职时间
        remark?: string;     // 备注
        created_at: string;  // 创建时间
        updated_at: string;  // 更新时间
    }
}
```

## 移除员工职位

移除员工的某个职位。

- **接口地址**: `/employee/position/remove/:id`
- **请求方式**: `POST`
- **路径参数**:
  - `id`: 职位记录ID

- **响应结果**:

```typescript
{
    code: number;      // 状态码
    message: string;   // 状态信息
}
```

## 获取员工列表

获取员工列表。

- **接口地址**: `/employee/list`
- **请求方式**: `GET`
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
            id: number;        // 员工ID
            company_id: number;// 公司ID
            name: string;      // 员工姓名
            email?: string;    // 电子邮箱
            phone?: string;    // 电话号码
            birthdate?: string;// 出生日期
            address?: string;  // 地址
            gender: string;    // 性别
            department_id?: number; // 部门ID
            position_id?: number;   // 职位ID
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

## 按公司获取员工列表

获取指定公司的员工列表。

- **接口地址**: `/employee/list/:company_id`
- **请求方式**: `GET`
- **路径参数**:
  - `company_id`: 公司ID
- **查询参数**: 同获取员工列表
- **响应结果**: 同获取员工列表

## 按部门获取员工列表

获取指定部门的员工列表。

- **接口地址**: `/employee/list/department/:department_id`
- **请求方式**: `GET`
- **路径参数**:
  - `department_id`: 部门ID
- **查询参数**: 同获取员工列表
- **响应结果**: 同获取员工列表

## 搜索员工

根据名称搜索员工。

- **接口地址**: `/employee/search`
- **请求方式**: `GET`
- **查询参数**:

```typescript
{
    name: string;      // 搜索关键词
    page?: number;     // 页码，默认1
    limit?: number;    // 每页数量，默认20
}
```

- **响应结果**: 同获取员工列表

## 获取员工详情

获取指定员工的详细信息。

- **接口地址**: `/employee/get/:id`
- **请求方式**: `GET`
- **路径参数**:
  - `id`: 员工ID

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 员工ID
        company_id: number;// 公司ID
        name: string;      // 员工姓名
        email?: string;    // 电子邮箱
        phone?: string;    // 电话号码
        birthdate?: string;// 出生日期
        address?: string;  // 地址
        gender: string;    // 性别
        department_id?: number; // 部门ID
        position_id?: number;   // 职位ID
        extra_value?: any; // 额外字段值
        created_at: string;// 创建时间
        updated_at: string;// 更新时间
    }
}
```

## 删除员工

删除指定的员工。

- **接口地址**: `/employee/delete/:id`
- **请求方式**: `POST`
- **路径参数**:
  - `id`: 员工ID

- **响应结果**:

```typescript
{
    code: number;      // 状态码
    message: string;   // 状态信息
}
```

## 获取员工职位列表

获取员工的所有职位记录。

- **接口地址**: `/employee/position/list/:employee_id`
- **请求方式**: `GET`
- **路径参数**:
  - `employee_id`: 员工ID

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: Array<{
        id: number;        // 记录ID
        employee_id: number; // 员工ID
        company_id: number;  // 公司ID
        department_id: number; // 部门ID
        position_id: number;   // 职位ID
        entry_at: string;    // 入职时间
        remark?: string;     // 备注
        created_at: string;  // 创建时间
        updated_at: string;  // 更新时间
    }>
}
```

## 获取员工当前职位

获取员工的当前职位信息。

- **接口地址**: `/employee/position/:id`
- **请求方式**: `GET`
- **路径参数**:
  - `id`: 员工ID

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 记录ID
        employee_id: number; // 员工ID
        company_id: number;  // 公司ID
        department_id: number; // 部门ID
        position_id: number;   // 职位ID
        entry_at: string;    // 入职时间
        remark?: string;     // 备注
        created_at: string;  // 创建时间
        updated_at: string;  // 更新时间
    }
}
```

## 获取员工职位历史

获取员工的所有职位历史记录。

- **接口地址**: `/employee/position/history/:id`
- **请求方式**: `GET`
- **路径参数**:
  - `id`: 员工ID

- **响应结果**: 同获取员工职位列表 