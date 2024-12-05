-- Add up migration script here
    -- 新建一个用于存储 json schema 的表，用于存放描述 JSON 数据结构的 JSON Schema

    CREATE TABLE IF NOT EXISTS json_schemas (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `name` VARCHAR(255) NOT NULL,
        `schema` JSON NOT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 新建公司表
    CREATE TABLE IF NOT EXISTS company (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `name` VARCHAR(255) NOT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `extra_value` JSON NULL,
        extra_schema_id INTEGER NULL
    );

    -- 新建雇员个人数据库表
    CREATE TABLE IF NOT EXISTS employee (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `name` VARCHAR(255) NOT NULL,
        `email` VARCHAR(255) NULL,
        `phone` VARCHAR(20) NULL,
        `birthdate` DATE NULL,
        `address` VARCHAR(255) NULL,
        `gender` TEXT CHECK(`gender` IN ('Male', 'Female', 'Unknown')) NOT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `extra_value` JSON NULL,
        extra_schema_id INTEGER NULL
    );

    -- 新建公司部门数据库表
    CREATE TABLE IF NOT EXISTS department (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `parent_id` INTEGER NULL,
        `company_id` INTEGER NOT NULL,
        `name` VARCHAR(64) NOT NULL,
        `leader_id` INTEGER NULL,
        `remark` VARCHAR(255) NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 新建公司职位数据库表
    CREATE TABLE IF NOT EXISTS position (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `name` VARCHAR(64) NOT NULL,
        `company_id` INTEGER NOT NULL,
        `remark` VARCHAR(255) NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 新建公司员工职位关联表
    CREATE TABLE IF NOT EXISTS employee_position (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `employee_id` INTEGER NOT NULL,
        `company_id` INTEGER NOT NULL,
        `department_id` INTEGER NOT NULL,
        `position_id` INTEGER NOT NULL,
        `remark` VARCHAR(255) NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 创建默认公司，名称为 mihoyou
    INSERT INTO company (`name`) VALUES ('mihoyou');