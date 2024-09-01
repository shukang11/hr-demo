import { getDatabaseInstance } from "./db";
import { Department } from "../types";
import useSWR from "swr";

export async function dbAddDepartment({
  id,
  name,
  parentId,
  company,
  leader,
  remark,
}: Partial<Department>): Promise<void> {
  if (id) {
    throw new Error(
      "Department ID should not be provided when adding department"
    );
  } else if (company === undefined) {
    throw new Error("Company information is required to add department");
  }
  if (leader && leader?.id === undefined) {
    throw new Error("Department leader ID is required to add department");
  }
  const db = await getDatabaseInstance();
  await db.execute(
    `
    INSERT INTO department (
      name, parent_id, company_id, leader_id, remark
    ) VALUES ($1, $2, $3, $4, $5)
  `,
    [name, parentId, company?.id, leader?.id, remark]
  );
}

export async function dbUpdateDepartment({
  id,
  name,
  parentId,
  company,
  leader,
  remark,
}: Partial<Department>): Promise<void> {
  if (id === undefined) {
    throw new Error("Department ID is required to update department");
  }
  if (leader && leader?.id === undefined) {
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
    [name, parentId, company?.id, leader?.id, remark, id]
  );
}

export async function dbGetDepartments(): Promise<Department[]> {
  const db = await getDatabaseInstance();
  const departements = await db.select(`
    SELECT * FROM department
  `);
  // @ts-ignore
  return departements.map((row) => ({
    id: row.id,
    name: row.name,
    parentId: row.parent_id,
    company: row.company_id,
    leader: row.leader_id,
    remark: row.remark
  }));
}

export const departmentsFetcher = () => dbGetDepartments()

export const useDepartments = () => {
  return useSWR('/get-departments', departmentsFetcher); // 更新路径
}