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
    SELECT * FROM employee
  `);
  // @ts-ignore
  return employees.map((row: any) => ({
    id: row.id,
    username: row.name,
    email: row.email,
    phone: row.phone,
    gender: row.gender,
    birthday: row.birthdate ? new Date(row.birthdate) : null,
    address: row.address,
    extra: {
      value: row.extra_value ? JSON.parse(row.extra_value) : {},
      id: row.extra_schema_id,
    },
  }));
}

export const employeesFetcher = () => dbGetEmployees();

export const useEmployees = () => {
  return useSWR('/get-employees', employeesFetcher);
}

