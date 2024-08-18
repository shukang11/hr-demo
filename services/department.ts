import { getDatabaseInstance } from "./db";
import { Department } from "../types";

export async function dbAddDepartment(department: Department): Promise<void> {
  if (department.leader?.id === undefined) {
    throw new Error("Department leader ID is required to add department");
  }
  const db = await getDatabaseInstance();
  await db.execute(
    `
    INSERT INTO department (
      name, parent_id, company_id, leader_id, remark
    ) VALUES ($1, $2, $3, $4, $5)
  `,
    [
      department.name,
      department.parentId,
      department.company?.id,
      department.leader?.id,
      department.remark,
    ]
  );
}

export async function dbUpdateDepartment(department: Department): Promise<void> {
  if (department.id === undefined) {
    throw new Error("Department ID is required to update department");
  }
  if (department.leader?.id === undefined) {
    throw new Error("Department leader ID is required to update department");
  }
  const db = await getDatabaseInstance();
  await db.execute(
    `
    UPDATE department SET 
      name = $1, 
      parent_id = $2, 
      company_id = $3, 
      leader_id = $4, 
      remark = $5 
    WHERE id = $6
  `,
    [
      department.name,
      department.parentId,
      department.company?.id,
      department.leader?.id,
      department.remark,
      department.id,
    ]
  );
}
