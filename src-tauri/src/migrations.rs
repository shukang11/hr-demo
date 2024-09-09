use tauri_plugin_sql::{Migration, MigrationKind};

pub fn get_version_1() -> Migration {
    let raw_sql = r#"

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
        `hire_date` DATE NULL,
        `termination_date` DATE NULL,
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

   "#;

    Migration {
        version: 1,
        description: "create_initial_tables",
        sql: raw_sql,
        kind: MigrationKind::Up,
    }
}

pub fn get_version_2() -> Migration {
    let raw_sql = r#"
    -- 创建默认公司，名称为 mihoyou
    INSERT INTO company (`name`) VALUES ('mihoyou');

    -- 创建部门
    INSERT INTO department (`company_id`, `name`, `remark`) VALUES (1, '工程部', '主要部门');
    INSERT INTO department (`company_id`, `name`, `remark`) VALUES (1, '市场部', '推广和广告');
    INSERT INTO department (`company_id`, `name`, `remark`) VALUES (1, '销售部', '处理客户互动');

    -- 创建职位
    INSERT INTO position (`company_id`, `name`, `remark`) VALUES (1, '软件工程师', '开发软件');
    INSERT INTO position (`company_id`, `name`, `remark`) VALUES (1, '产品经理', '管理产品');
    INSERT INTO position (`company_id`, `name`, `remark`) VALUES (1, '市场专员', '推广产品');
    INSERT INTO position (`company_id`, `name`, `remark`) VALUES (1, '销售代表', '销售产品');
    INSERT INTO position (`company_id`, `name`, `remark`) VALUES (1, 'UI设计师', '设计界面');
    INSERT INTO position (`company_id`, `name`, `remark`) VALUES (1, 'UX设计师', '设计用户体验');
    INSERT INTO position (`company_id`, `name`, `remark`) VALUES (1, '数据分析师', '分析数据');
    INSERT INTO position (`company_id`, `name`, `remark`) VALUES (1, '客服专员', '客户服务');
    -- 创建员工
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('张三', 'zhangsan@example.com', '12345678901', 'Male', '1990-01-01', '北京市', '2024-07-01', '2024-08-15');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('李四', 'lisi@example.com', '12345678902', 'Female', '1991-02-02', '上海市', '2024-07-02', '2024-08-16');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('王五', 'wangwu@example.com', '12345678903', 'Male', '1992-03-03', '广州市', '2024-07-03', '2024-08-17');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('赵六', 'zhaoliu@example.com', '12345678904', 'Female', '1993-04-04', '深圳市', '2024-07-04', '2024-08-18');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('孙七', 'sunqi@example.com', '12345678905', 'Male', '1994-05-05', '杭州市', '2024-07-05', '2024-08-19');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('周八', 'zhouba@example.com', '12345678906', 'Female', '1995-06-06', '成都市', '2024-07-06', '2024-08-20');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('吴九', 'wujiu@example.com', '12345678907', 'Male', '1996-07-07', '重庆市', '2024-07-07', '2024-08-21');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('郑十', 'zhengshi@example.com', '12345678908', 'Female', '1997-08-08', '南京市', '2024-07-08', '2024-08-22');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('王十一', 'wangshiyi@example.com', '12345678909', 'Male', '1998-09-09', '武汉市', '2024-07-09', '2024-08-23');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('李十二', 'lishier@example.com', '12345678910', 'Female', '1999-10-10', '西安市', '2024-07-10', '2024-08-24');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('张十三', 'zhangshisan@example.com', '12345678911', 'Male', '2000-11-11', '天津市', '2024-07-11', '2024-08-25');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('王十四', 'wangshisi@example.com', '12345678912', 'Female', '2001-12-12', '沈阳市', '2024-07-12', '2024-08-26');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('李十五', 'lishiwu@example.com', '12345678913', 'Male', '2002-01-13', '大连市', '2024-07-13', '2024-08-27');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('张十六', 'zhangshiliu@example.com', '12345678914', 'Female', '2003-02-14', '青岛市', '2024-07-14', '2024-08-28');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('王十七', 'wangshiqi@example.com', '12345678915', 'Male', '2004-03-15', '济南市', '2024-07-15', '2024-08-29');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('李十八', 'lishiba@example.com', '12345678916', 'Female', '2005-04-16', '郑州市', '2024-07-16', '2024-08-30');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('张十九', 'zhangshijiu@example.com', '12345678917', 'Male', '2006-05-17', '长沙市', '2024-07-17', '2024-08-31');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('王二十', 'wangershi@example.com', '12345678918', 'Female', '2007-06-18', '合肥市', '2024-07-18', '2024-09-01');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('李二十一', 'liershi@example.com', '12345678919', 'Male', '2008-07-19', '南昌市', '2024-07-19', '2024-09-02');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('张二十二', 'zhangershi@example.com', '12345678920', 'Female', '2009-08-20', '福州市', '2024-07-20', '2024-09-03');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('王二十三', 'wangersan@example.com', '12345678921', 'Male', '2010-09-21', '石家庄市', '2024-07-21', '2024-09-04');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('李二十四', 'liersi@example.com', '12345678922', 'Female', '2011-10-22', '太原市', '2024-07-22', '2024-09-05');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('张二十五', 'zhangershi@example.com', '12345678923', 'Male', '2012-11-23', '呼和浩特市', '2024-07-23', '2024-09-06');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('王二十六', 'wangershi@example.com', '12345678924', 'Female', '2013-12-24', '兰州市', '2024-07-24', '2024-09-07');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('李二十七', 'lierqi@example.com', '12345678925', 'Male', '2014-01-25', '西宁市', '2024-07-25', '2024-09-08');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('张二十八', 'zhangershi@example.com', '12345678926', 'Female', '2015-02-26', '银川市', '2024-07-26', '2024-09-09');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('王二十九', 'wangershi@example.com', '12345678927', 'Male', '2016-03-27', '乌鲁木齐市', '2024-07-27', '2024-09-10');
    INSERT INTO employee (`name`, `email`, `phone`, `gender`, `birthdate`, `address`, `hire_date`, `termination_date`) VALUES ('李三十', 'liershi@example.com', '12345678928', 'Female', '2017-04-28', '拉萨市', '2024-07-28', '2024-09-11');

    -- 创建员工职位
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (1, 1, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (2, 2, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (3, 3, 1, 3);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (4, 4, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (5, 5, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (6, 6, 1, 3);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (7, 7, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (8, 8, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (9, 9, 1, 3);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (10, 1, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (11, 2, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (12, 3, 1, 3);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (13, 4, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (14, 5, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (15, 6, 1, 3);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (16, 7, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (17, 8, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (18, 9, 1, 3);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (19, 1, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (20, 2, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (21, 3, 1, 3);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (22, 4, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (23, 5, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (24, 6, 1, 3);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (25, 7, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (26, 8, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (27, 9, 1, 3);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (28, 1, 1, 1);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (29, 2, 1, 2);
    INSERT INTO employee_position (`employee_id`, `position_id`, `company_id`, `department_id`) VALUES (30, 3, 1, 3);
    
    "#;
    Migration {
        version: 2,
        description: "fill examples data",
        sql: raw_sql,
        kind: MigrationKind::Up,
    }
}

pub fn get_migrations() -> Vec<Migration> {
    vec![get_version_1(), get_version_2()]
}
