-- 删除默认公司数据
DELETE FROM company WHERE name = 'mihoyou';

-- 删除各个表
DROP TABLE IF EXISTS employee_position;
DROP TABLE IF EXISTS position;
DROP TABLE IF EXISTS department;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS company;
DROP TABLE IF EXISTS json_schemas;
