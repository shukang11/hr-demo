# 仪表盘接口

## 获取公司完整看板统计数据

获取公司的完整统计数据，包括员工、部门、招聘等各方面的统计信息。

- **接口地址**: `/dashboard/stats/:company_id`
- **请求方式**: `GET`
- **路径参数**:
  - `company_id`: 公司ID
- **查询参数**:

```typescript
{
    start_date?: string;  // 开始日期（格式：YYYY-MM-DD）
    end_date?: string;    // 结束日期（格式：YYYY-MM-DD）
}
```

- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        total_employees: number;  // 员工总数
        department_distribution: Array<{  // 部门分布
            department: string;   // 部门名称
            count: number;       // 员工数量
        }>;
        gender_distribution: {    // 性别分布
            male: number;        // 男性数量
            female: number;      // 女性数量
            unknown: number;     // 未知数量
        };
        age_distribution: Array<{  // 年龄分布
            range: string;       // 年龄段
            count: number;       // 人数
        }>;
        candidate_status_distribution: Array<{  // 候选人状态分布
            status: string;      // 状态
            count: number;       // 数量
        }>;
        monthly_interviews: number;  // 本月面试数量
        conversion_rate: number;     // 面试转化率
        department_recruitment_top5: Array<{  // 部门招聘需求TOP5
            department: string;   // 部门名称
            open_positions: number;  // 开放职位数量
        }>;
        employee_growth_trend: Array<{  // 员工增长趋势
            month: string;       // 月份（YYYY-MM）
            count: number;       // 数量
        }>;
        department_growth_trend: Array<{  // 部门人员变化趋势
            department: string;   // 部门名称
            trend: Array<{
                month: string;    // 月份（YYYY-MM）
                count: number;    // 数量
            }>;
        }>;
        position_distribution: Array<{  // 职位分布
            position: string;    // 职位名称
            count: number;       // 人数
        }>;
        tenure_distribution: Array<{  // 入职时长分布
            range: string;       // 时长范围
            count: number;       // 人数
        }>;
    }
}
```

## 获取公司人员概览统计数据

获取公司的人员概览统计数据。

- **接口地址**: `/dashboard/employee-overview/:company_id`
- **请求方式**: `GET`
- **路径参数**:
  - `company_id`: 公司ID
- **查询参数**: 同获取公司完整看板统计数据
- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        total_employees: number;  // 员工总数
        department_distribution: Array<{  // 部门分布
            department: string;   // 部门名称
            count: number;       // 员工数量
        }>;
        gender_distribution: {    // 性别分布
            male: number;        // 男性数量
            female: number;      // 女性数量
            unknown: number;     // 未知数量
        };
        age_distribution: Array<{  // 年龄分布
            range: string;       // 年龄段
            count: number;       // 人数
        }>;
    }
}
```

## 获取公司招聘概况统计数据

获取公司的招聘相关统计数据。

- **接口地址**: `/dashboard/recruitment-stats/:company_id`
- **请求方式**: `GET`
- **路径参数**:
  - `company_id`: 公司ID
- **查询参数**: 同获取公司完整看板统计数据
- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        candidate_status_distribution: Array<{  // 候选人状态分布
            status: string;      // 状态
            count: number;       // 数量
        }>;
        monthly_interviews: number;  // 本月面试数量
        conversion_rate: number;     // 面试转化率
        department_recruitment_top5: Array<{  // 部门招聘需求TOP5
            department: string;   // 部门名称
            open_positions: number;  // 开放职位数量
        }>;
    }
}
```

## 获取公司组织发展统计数据

获取公司的组织发展相关统计数据。

- **接口地址**: `/dashboard/organization-stats/:company_id`
- **请求方式**: `GET`
- **路径参数**:
  - `company_id`: 公司ID
- **查询参数**: 同获取公司完整看板统计数据
- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: {
        employee_growth_trend: Array<{  // 员工增长趋势
            month: string;       // 月份（YYYY-MM）
            count: number;       // 数量
        }>;
        department_growth_trend: Array<{  // 部门人员变化趋势
            department: string;   // 部门名称
            trend: Array<{
                month: string;    // 月份（YYYY-MM）
                count: number;    // 数量
            }>;
        }>;
        position_distribution: Array<{  // 职位分布
            position: string;    // 职位名称
            count: number;       // 人数
        }>;
        tenure_distribution: Array<{  // 入职时长分布
            range: string;       // 时长范围
            count: number;       // 人数
        }>;
    }
}
```

## 获取生日员工列表

获取指定时间范围内过生日的员工列表。

- **接口地址**: `/dashboard/birthday-employees/:company_id`
- **请求方式**: `GET`
- **路径参数**:
  - `company_id`: 公司ID
- **查询参数**: 同获取公司完整看板统计数据
- **响应结果**:

```typescript
{
    code: number;          // 状态码
    message: string;       // 状态信息
    data: Array<{
        id: number;        // 员工ID
        name: string;      // 员工姓名
        department: string;// 部门名称
        position: string;  // 职位名称
        birthdate: string; // 生日日期
    }>
} 