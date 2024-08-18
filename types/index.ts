export class ExtraSchema {
  value: Record<string, any>;

  schema?: object;

  constructor({ value, schema }: ExtraSchema) {
    this.value = value;
    this.schema = schema;
  }
}

/**
 * @enum {string}
 * @typedef {object} Gender
 * @property {string} Female - 表示女性
 * @property {string} Male - 表示男性
 * @property {string} Unknown - 表示未知
 */
export enum Gender {
  Female = "female",
  Male = "male",
  Unknown = "unknown",
}

export class Account {
  id?: string;
  username?: string;
  email: string;
  phone?: string;
  employeeInfo?: EmployeeInfo;
  interviews?: Interview[];
  department?: Department;
  extra: Record<string, any>;

  constructor({
    id,
    username,
    email,
    phone,
    employeeInfo,
    interviews,
    department,
    extra,
  }: Account) {
    this.id = id;
    this.username = username;
    this.email = email;
    this.phone = phone;
    this.employeeInfo = employeeInfo;
    this.interviews = interviews;
    this.department = department;
    this.extra = extra;
  }
}

// 表示员工的入职和离职信息
export class EmployeeInfo {
  accountId: string;
  hireDate: Date;
  terminationDate?: Date;

  constructor({ accountId, hireDate, terminationDate }: EmployeeInfo) {
    this.accountId = accountId;
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
  parentId?: string;
  remark?: string;
  children?: Department[];

  constructor({ name, id, parentId, remark, children }: Department) {
    this.name = name;
    this.id = id;
    this.parentId = parentId;
    this.remark = remark;
    this.children = children;
  }
}
