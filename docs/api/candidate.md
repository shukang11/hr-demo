# 候选人管理接口

## 创建或更新候选人

创建新候选人或更新现有候选人信息。

- **接口地址**: `/candidate/insert`
- **请求方式**: `POST`
- **请求参数**:

```typescript
{
    id?: number;           // 候选人ID（更新时必填）
    company_id: number;    // 公司ID
    name: string;          // 候选人姓名
    phone?: string;        // 联系电话
    email?: string;        // 电子邮箱
    position_id: number;   // 应聘职位ID
    department_id: number; // 目标部门ID
    interview_date?: string; // 面试日期（格式：YYYY-MM-DD HH:mm:ss）
    interviewer_id?: number; // 面试官ID
    extra_value?: {        // 额外字段值（JSON）
        gender?: "Male" | "Female" | "Unknown"; // 性别
        birthday?: string; // 出生日期
        education?: string; // 学历
        work_years?: number; // 工作年限
        source?: string;   // 来源
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
        id: number;        // 候选人ID
        company_id: number;// 公司ID
        name: string;      // 候选人姓名
        phone?: string;    // 联系电话
        email?: string;    // 电子邮箱
        position_id: number; // 应聘职位ID
        department_id: number; // 目标部门ID
        interview_date?: string; // 面试日期
        status: string;    // 状态
        interviewer_id?: number; // 面试官ID
        evaluation?: string; // 面试评价
        remark?: string;   // 备注
        extra_value?: any; // 额外字段值
        created_at: string;// 创建时间
        updated_at: string;// 更新时间
    }
}
```

## 更新候选人状态

更新候选人的状态信息。

- **接口地址**: `/candidate/:id/status`
- **请求方式**: `POST`
- **路径参数**:
  - `id`: 候选人ID
- **请求参数**:

```typescript
{
    status: "Pending" | "Scheduled" | "Interviewed" | "Accepted" | "Rejected" | "Withdrawn"; // 状态
    evaluation?: string;   // 面试评价
    remark?: string;      // 备注
}
```

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 候选人ID
        status: string;    // 更新后的状态
        evaluation?: string; // 面试评价
        remark?: string;   // 备注
        updated_at: string;// 更新时间
    }
}
```

## 获取候选人列表

获取指定公司的候选人列表。

- **接口地址**: `/candidate/list/:company_id`
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
            id: number;        // 候选人ID
            company_id: number;// 公司ID
            name: string;      // 候选人姓名
            phone?: string;    // 联系电话
            email?: string;    // 电子邮箱
            position_id: number; // 应聘职位ID
            department_id: number; // 目标部门ID
            interview_date?: string; // 面试日期
            status: string;    // 状态
            interviewer_id?: number; // 面试官ID
            evaluation?: string; // 面试评价
            remark?: string;   // 备注
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

## 获取候选人详情

获取指定候选人的详细信息。

- **接口地址**: `/candidate/get/:id`
- **请求方式**: `GET`
- **路径参数**:
  - `id`: 候选人ID

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        id: number;        // 候选人ID
        company_id: number;// 公司ID
        name: string;      // 候选人姓名
        phone?: string;    // 联系电话
        email?: string;    // 电子邮箱
        position_id: number; // 应聘职位ID
        department_id: number; // 目标部门ID
        interview_date?: string; // 面试日期
        status: string;    // 状态
        interviewer_id?: number; // 面试官ID
        evaluation?: string; // 面试评价
        remark?: string;   // 备注
        extra_value?: any; // 额外字段值
        created_at: string;// 创建时间
        updated_at: string;// 更新时间
    }
}
```

## 删除候选人

删除指定的候选人。

- **接口地址**: `/candidate/delete/:id`
- **请求方式**: `POST`
- **路径参数**:
  - `id`: 候选人ID

- **响应结果**:

```typescript
{
    code: number;      // 状态码
    message: string;   // 状态信息
}
``` 