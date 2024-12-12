from datetime import date
from extensions.ext_database import db
from .base import BaseModel


class JsonSchemaInDB(BaseModel):
    """JSON Schema 数据库模型
    用于存储和管理 JSON 数据结构的模式定义

    Attributes:
        name (str): Schema 名称，不可为空
        schema (JSON): JSON Schema 定义，不可为空
    """
    __tablename__ = 'json_schemas'

    name = db.Column(db.String(255), nullable=False)
    schema = db.Column(db.JSON, nullable=False)


class CompanyInDB(BaseModel):
    """公司信息数据库模型
    存储公司基本信息及其与其他实体的关系

    Attributes:
        name (str): 公司名称，不可为空
        extra_value (JSON): 额外的 JSON 格式数据
        extra_schema_id (int): 关联的 JSON Schema ID
        extra_schema (JsonSchemaInDB): 关联的 JSON Schema 对象
        departments (list): 公司下属部门列表
        positions (list): 公司职位列表
    """
    __tablename__ = 'company'

    name = db.Column(db.String(255), nullable=False)
    extra_value = db.Column(db.JSON)
    extra_schema_id = db.Column(db.Integer, db.ForeignKey('json_schemas.id'))

    # Relationships
    extra_schema = db.relationship('JsonSchemaInDB', foreign_keys=[extra_schema_id])
    departments = db.relationship('DepartmentInDB', back_populates='company')
    positions = db.relationship('PositionInDB', back_populates='company')


class EmployeeInDB(BaseModel):
    """员工信息数据库模型
    存储员工的详细个人信息及其与公司、部门、职位的关系

    Attributes:
        name (str): 员工姓名，不可为空
        email (str): 电子邮箱
        phone (str): 联系电话
        birthdate (date): 出生日期
        address (str): 居住地址
        hire_date (date): 入职日期
        termination_date (date): 离职日期
        gender (str): 性别，必须为 'Male'、'Female' 或 'Unknown'
        extra_value (JSON): 额外的 JSON 格式数据
        extra_schema_id (int): 关联的 JSON Schema ID
        extra_schema (JsonSchemaInDB): 关联的 JSON Schema 对象
        positions (list): 员工担任的职位列表
        led_departments (list): 员工作为负责人的部门列表
    """
    __tablename__ = 'employee'

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    birthdate = db.Column(db.Date)
    address = db.Column(db.String(255))
    hire_date = db.Column(db.Date)
    termination_date = db.Column(db.Date)
    gender = db.Column(db.String, nullable=False)
    extra_value = db.Column(db.JSON)
    extra_schema_id = db.Column(db.Integer, db.ForeignKey('json_schemas.id'))

    # Relationships
    extra_schema = db.relationship('JsonSchemaInDB', foreign_keys=[extra_schema_id])
    positions = db.relationship('EmployeePositionInDB', back_populates='employee')
    led_departments = db.relationship('DepartmentInDB', back_populates='leader')


class DepartmentInDB(BaseModel):
    """部门信息数据库模型
    存储部门信息及其与公司、员工的关系，支持树形结构

    Attributes:
        parent_id (int): 父部门ID，用于构建部门树形结构
        company_id (int): 所属公司ID，不可为空
        name (str): 部门名称，不可为空
        leader_id (int): 部门负责人ID
        remark (str): 备注信息
        parent (DepartmentInDB): 父部门对象
        children (list): 子部门列表
        company (CompanyInDB): 所属公司对象
        leader (EmployeeInDB): 部门负责人对象
        employee_positions (list): 部门下的员工-职位关联列表
    """
    __tablename__ = 'department'

    parent_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    remark = db.Column(db.String(255))

    # Relationships
    parent = db.relationship('DepartmentInDB', remote_side=[id], backref='children')
    company = db.relationship('CompanyInDB', back_populates='departments')
    leader = db.relationship('EmployeeInDB', back_populates='led_departments')
    employee_positions = db.relationship('EmployeePositionInDB', back_populates='department')


class PositionInDB(BaseModel):
    """职位信息数据库模型
    存储职位信息及其与公司的关系

    Attributes:
        name (str): 职位名称，不可为空
        company_id (int): 所属公司ID，不可为空
        remark (str): 备注信息
        company (CompanyInDB): 所属公司对象
        employee_positions (list): 该职位下的员工-职位关联列表
    """
    __tablename__ = 'position'

    name = db.Column(db.String(64), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    remark = db.Column(db.String(255))

    # Relationships
    company = db.relationship('CompanyInDB', back_populates='positions')
    employee_positions = db.relationship('EmployeePositionInDB', back_populates='position')


class EmployeePositionInDB(BaseModel):
    """员工-职位关联数据库模型
    存储员工与职位的多对多关系，包含额外的关联信息

    Attributes:
        employee_id (int): 员工ID，不可为空
        company_id (int): 公司ID，不可为空
        department_id (int): 部门ID，不可为空
        position_id (int): 职位ID，不可为空
        remark (str): 备注信息
        employee (EmployeeInDB): 关联的员工对象
        company (CompanyInDB): 关联的公司对象
        department (DepartmentInDB): 关联的部门对象
        position (PositionInDB): 关联的职位对象
    """
    __tablename__ = 'employee_position'

    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    remark = db.Column(db.String(255))

    # Relationships
    employee = db.relationship('EmployeeInDB', back_populates='positions')
    company = db.relationship('CompanyInDB')
    department = db.relationship('DepartmentInDB', back_populates='employee_positions')
    position = db.relationship('PositionInDB', back_populates='employee_positions') 