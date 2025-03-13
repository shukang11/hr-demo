-- Initial tables

-- Create json_schemas table
CREATE TABLE IF NOT EXISTS json_schemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                 -- schema名称
    schema TEXT NOT NULL,               -- JSON Schema
    company_id INTEGER,                 -- 公司ID
    remark TEXT,                        -- 备注
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Create company table
CREATE TABLE IF NOT EXISTS company (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                 -- 公司名称
    extra_value TEXT,                   -- 额外JSON数据
    extra_schema_id INTEGER,            -- 额外数据schema ID
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP   -- 更新时间
);

-- Create department table
CREATE TABLE IF NOT EXISTS department (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER,                  -- 父部门ID
    company_id INTEGER NOT NULL,        -- 公司ID
    name TEXT NOT NULL,                 -- 部门名称
    leader_id INTEGER,                  -- 部门负责人ID
    remark TEXT,                        -- 备注
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES department(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Create position table
CREATE TABLE IF NOT EXISTS position (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                 -- 职位名称
    company_id INTEGER NOT NULL,        -- 公司ID
    remark TEXT,                        -- 备注
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create employee table
CREATE TABLE IF NOT EXISTS employee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,        -- 公司ID
    name TEXT NOT NULL,                 -- 姓名
    email TEXT,                         -- 邮箱
    phone TEXT,                         -- 电话
    birthdate DATE,                     -- 出生日期
    address TEXT,                       -- 地址
    gender TEXT NOT NULL,               -- 性别
    extra_value TEXT,                   -- 额外JSON数据
    extra_schema_id INTEGER,            -- 额外数据schema ID
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create employee_position table
CREATE TABLE IF NOT EXISTS employee_position (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,       -- 员工ID
    company_id INTEGER NOT NULL,        -- 公司ID
    department_id INTEGER NOT NULL,     -- 部门ID
    position_id INTEGER NOT NULL,       -- 职位ID
    entry_at DATETIME,                 -- 入职时间
    remark TEXT,                        -- 备注
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (employee_id) REFERENCES employee(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (department_id) REFERENCES department(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (position_id) REFERENCES position(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Candidates table (second migration)
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,        -- 公司ID
    name TEXT NOT NULL,                 -- 候选人姓名
    phone TEXT,                         -- 联系电话
    email TEXT,                         -- 电子邮箱
    position_id INTEGER,                -- 应聘职位ID
    department_id INTEGER,              -- 目标部门ID
    interview_date DATETIME,            -- 面试日期
    status TEXT,                        -- 状态
    interviewer_id INTEGER,             -- 面试官ID
    evaluation TEXT,                    -- 面试评价
    remark TEXT,                        -- 备注
    extra_value TEXT,                   -- 额外JSON数据
    extra_schema_id INTEGER,            -- 额外数据schema ID
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (position_id) REFERENCES position(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (department_id) REFERENCES department(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (interviewer_id) REFERENCES employee(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (extra_schema_id) REFERENCES json_schemas(id) ON DELETE SET NULL ON UPDATE CASCADE
);