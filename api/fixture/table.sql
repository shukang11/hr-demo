-- 创建 company 表
CREATE TABLE IF NOT EXISTS "company" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" TEXT NOT NULL,
    "extra_value" JSON,
    "extra_schema_id" INTEGER,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建 json_schemas 表
CREATE TABLE IF NOT EXISTS "json_schemas" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" TEXT NOT NULL,
    "schema" JSON NOT NULL,
    "company_id" INTEGER,
    "remark" TEXT,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("company_id") REFERENCES "company" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- 创建 department 表
CREATE TABLE IF NOT EXISTS "department" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "parent_id" INTEGER,
    "company_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "leader_id" INTEGER,
    "remark" TEXT,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("company_id") REFERENCES "company" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("parent_id") REFERENCES "department" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- 创建 position 表
CREATE TABLE IF NOT EXISTS "position" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" TEXT NOT NULL,
    "company_id" INTEGER NOT NULL,
    "remark" TEXT,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("company_id") REFERENCES "company" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- 创建 employee 表
CREATE TABLE IF NOT EXISTS "employee" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "company_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT,
    "phone" TEXT,
    "birthdate" DATE,
    "address" TEXT,
    "gender" TEXT NOT NULL,
    "extra_value" JSON,
    "extra_schema_id" INTEGER,
    "marital_status" TEXT,
    "emergency_contact" TEXT,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("company_id") REFERENCES "company" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- 创建 employee_position 表
CREATE TABLE IF NOT EXISTS "employee_position" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "employee_id" INTEGER NOT NULL,
    "company_id" INTEGER NOT NULL,
    "department_id" INTEGER NOT NULL,
    "position_id" INTEGER NOT NULL,
    "start_date" DATETIME,
    "remark" TEXT,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("employee_id") REFERENCES "employee" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("company_id") REFERENCES "company" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("department_id") REFERENCES "department" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("position_id") REFERENCES "position" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- 创建 candidates 表
CREATE TABLE IF NOT EXISTS "candidates" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "company_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "phone" TEXT,
    "email" TEXT,
    "position_id" INTEGER,
    "department_id" INTEGER,
    "interview_date" DATETIME,
    "status" TEXT,
    "interviewer_id" INTEGER,
    "evaluation" TEXT,
    "remark" TEXT,
    "extra_value" JSON,
    "extra_schema_id" INTEGER,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("company_id") REFERENCES "company" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("position_id") REFERENCES "position" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("department_id") REFERENCES "department" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("interviewer_id") REFERENCES "employee" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("extra_schema_id") REFERENCES "json_schemas" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);