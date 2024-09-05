import { getDatabaseInstance } from "./db";
import { Employee } from "../types";
import useSWR from "swr";

export async function dbAddEmployee(employee: Employee): Promise<void> {
  const db = await getDatabaseInstance();
  await db.execute(
    `
    INSERT INTO employee (
      name, email, phone, gender, birthdate, address, extra_value, extra_schema_id
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
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
    ]
  );

  if (employee.department && employee.company && employee) {
    await db.execute(
      `
    INSERT INTO employee_position (
      employee_id, company_id, department_id, position_id
    ) VALUES ($1, $2, $3, $4)
    `,
      [
        employee.id,
        employee.company.id,
        employee.department.id,
        employee.position?.id,
      ]
    );
  }
}

export async function dbUpdateEmployee(employee: Employee): Promise<void> {
  if (employee.id === undefined) {
    throw new Error("Employee ID is required to update employee");
  }
  const db = await getDatabaseInstance();
  await db.execute(
    `
    UPDATE employee SET 
      name = $1, 
      email = $2, 
      phone = $3, 
      gender = $4, 
      birthdate = $5, 
      address = $6, 
      extra_value = $7, 
      extra_schema_id = $8 
    WHERE id = $9
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
      employee.id,
    ]
  );
}

export async function dbGetEmployees(): Promise<Employee[]> {
  const db = await getDatabaseInstance();
  const employees = await db.select(`
    SELECT e.*, ep.*, d.name as department_name, c.name as company_name, p.name as position_name
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
  }));
}

export const employeesFetcher = () => dbGetEmployees();

export const useEmployees = () => {
  return useSWR('/get-employees', employeesFetcher);
}

