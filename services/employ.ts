import { getDatabaseInstance } from "./db";
import { Employee } from "../types";
import useSWR from "swr";

export async function dbAddEmployee(employee: Employee): Promise<void> {
  const db = await getDatabaseInstance();
  let result;

  if (employee.id) {
    // 如果存在 id，则为 update
    result = await db.execute(
      `
      UPDATE employee SET 
        name = $1, 
        email = $2, 
        phone = $3, 
        gender = $4, 
        birthdate = $5, 
        address = $6, 
        extra_value = $7, 
        extra_schema_id = $8,
        hire_date = $9,
        termination_date = $10
      WHERE id = $11
      `,
      [
        employee.username || "",
        employee.email,
        employee.phone || "",
        employee.gender || "Unknown",
        employee.birthday ? employee.birthday.toISOString().split("T")[0] : null,
        employee.address,
        JSON.stringify(employee.extra?.value || {}),
        employee.extra?.id,
        employee.employeeInfo?.hireDate ? employee.employeeInfo.hireDate.toISOString().split("T")[0] : null,
        employee.employeeInfo?.terminationDate ? employee.employeeInfo.terminationDate.toISOString().split("T")[0] : null,
        employee.id,
      ]
    );
  } else {
    // 否则为 insert
    result = await db.execute(
      `
      INSERT INTO employee (
        name, email, phone, gender, birthdate, address, extra_value, extra_schema_id, hire_date, termination_date
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      `,
      [
        employee.username || "",
        employee.email,
        employee.phone || "",
        employee.gender || "Unknown",
        employee.birthday ? employee.birthday.toISOString().split("T")[0] : null,
        employee.address,
        JSON.stringify(employee.extra?.value || {}),
        employee.extra?.id,
        employee.employeeInfo?.hireDate ? employee.employeeInfo.hireDate.toISOString().split("T")[0] : null,
        employee.employeeInfo?.terminationDate ? employee.employeeInfo.terminationDate.toISOString().split("T")[0] : null,
      ]
    );
  }

  console.log(`after operation: `, result);

  if (employee.department) {
    // 更新 employee_position 表
    console.log(`查询现有员工:`, employee.id || result.lastInsertId);
    const existingEmployee: any[] = await db.select(`
      SELECT id FROM employee_position WHERE employee_id = $1
    `, [employee.id || result.lastInsertId]);

    console.log(`现有员工查询结果:`, existingEmployee);
    const hasExsitsEmployeePosition = existingEmployee && existingEmployee.length > 0;
    if (hasExsitsEmployeePosition) {
      console.log(`更新员工职位信息:`, employee.id || result.lastInsertId);
      await db.execute(
        `
        UPDATE employee_position SET
          company_id = $1,
          position_id = $2
        WHERE employee_id = $3 AND department_id = $4
        `,
        [
          employee.company?.id || employee.department.company,
          employee.position?.id,
          employee.id || result.lastInsertId,
          employee.department.id,
        ]
      );
    } else {
      await db.execute(
        `
        INSERT INTO employee_position (
          employee_id, company_id, department_id, position_id
        ) VALUES ($1, $2, $3, $4)
        `,
        [
          employee.id || result.lastInsertId,
          employee.company?.id || employee.department.company,
          employee.department.id,
          employee.position?.id,
        ]
      );
    }
  }
}

export async function dbGetEmployees(): Promise<Employee[]> {
  const db = await getDatabaseInstance();
  const employees = await db.select(`
    SELECT e.*, ep.*, d.name as department_name, c.name as company_name, p.name as position_name,
           e.hire_date, e.termination_date
    FROM employee e
    LEFT JOIN employee_position ep ON e.id = ep.employee_id
    LEFT JOIN department d ON ep.department_id = d.id
    LEFT JOIN company c ON ep.company_id = c.id
    LEFT JOIN position p ON ep.position_id = p.id
  `);
  console.log(`employees`, employees);
  // @ts-ignore
  return employees.map((row: any) => ({
    id: row.id,
    username: row.name,
    email: row.email,
    phone: row.phone,
    gender: row.gender,
    birthdate: row.birthdate ? new Date(row.birthdate) : null,
    address: row.address,
    extra: {
      value: row.extra_value ? JSON.parse(row.extra_value) : {},
      id: row.extra_schema_id,
    },
    department: row.department_id ? {
      id: row.department_id,
      name: row.department_name,
    } : null,
    employeeInfo: {
      hireDate: row.hire_date ? new Date(row.hire_date) : null,
      terminationDate: row.termination_date ? new Date(row.termination_date) : null,
    },
  }));
}

export const employeesFetcher = () => dbGetEmployees();

export const useEmployees = () => {
  return useSWR('/get-employees', employeesFetcher);
}

