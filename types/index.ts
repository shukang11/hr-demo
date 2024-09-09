/**
 * @enum {string}
 * @typedef {object} Gender
 * @property {string} Female - 表示女性
 * @property {string} Male - 表示男性
 * @property {string} Unknown - 表示未知
 */
export enum Gender {
  Female = "Female",
  Male = "Male",
  Unknown = "Unknown",
}

export class Company {
  id?: number;
  name: string;
  extra_value: any;
  extra_schema_id?: number;

  constructor({ id, name, extra_value, extra_schema_id }: Company) {
    this.id = id;
    this.name = name;
    this.extra_value = extra_value;
    this.extra_schema_id = extra_schema_id;
  }
}

export class SchemaValue {
  id?: number;
  schema?: object;
  value: object;

  constructor({ id, schema, value }: SchemaValue) {
    this.id = id;
    this.schema = schema;
    this.value = value;
  }
}

export class Position {
  id?: number;
  name: string;
  company: Company;
  remark?: string;

  constructor({ id, name, company, remark }: Position) {
    this.id = id;
    this.name = name;
    this.company = company;
    this.remark = remark;
  }
}

export class Employee {
  id?: number;
  username: string;
  email?: string;
  phone: string;
  gender?: Gender;
  birthday?: Date;
  address?: string;
  employeeInfo?: EmployeeHireInfo;
  interviews?: Interview[];
  department?: Department;
  company?: Company;
  position?: Position;
  extra?: SchemaValue;

  constructor({
    id,
    username,
    email,
    phone,
    gender,
    birthday,
    address,
    employeeInfo,
    interviews,
    department,
    company,
    position,
    extra,
  }: Employee) {
    this.id = id;
    this.username = username;
    this.email = email;
    this.phone = phone;
    this.gender = gender || Gender.Unknown;
    this.birthday = birthday;
    this.address = address;
    this.employeeInfo = employeeInfo;
    this.interviews = interviews;
    this.department = department;
    this.company = company;
    this.position = position;
    this.extra = extra;
  }

  isActive(date: Date): boolean {
    if (!this.employeeInfo) return false;
    if (!this.employeeInfo.hireDate) return false;
    const { terminationDate, hireDate } = this.employeeInfo;
    if (hireDate > date) return false;
    return !terminationDate || terminationDate > date;
  }

}

// 表示员工的入职和离职信息
export class EmployeeHireInfo {
  employeeId?: string;
  hireDate: Date;
  terminationDate?: Date;

  constructor({ employeeId, hireDate, terminationDate }: EmployeeHireInfo) {
    this.employeeId = employeeId;
    this.hireDate = hireDate;
    this.terminationDate = terminationDate;
  }
}

// 面试信息
export class Interview {
  id?: string;
  user_id: string;
  interviewDate: Date;
  remark?: string;

  constructor({ id, user_id, interviewDate, remark }: Interview) {
    this.id = id;
    this.user_id = user_id;
    this.interviewDate = interviewDate;
    this.remark = remark;
  }
}

// 部门
export class Department {
  id?: string;
  name: string;
  company?: Company;
  parentId?: string;
  remark?: string;
  children?: Department[];
  leader?: Employee;
  members?: Employee[];

  constructor({
    id,
    name,
    leader,
    parentId,
    remark,
    children,
    members,
  }: Department) {
    this.name = name;
    this.id = id;
    this.leader = leader;
    this.parentId = parentId;
    this.remark = remark;
    this.children = children;
    this.members = members;
  }
}
