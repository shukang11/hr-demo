import { getDatabaseInstance } from "./db";
import { Company } from "../types";

export async function dbAddCompany(company: Company): Promise<void> {
  const db = await getDatabaseInstance();
  await db.execute(
    `
    INSERT INTO company (
      name, extra_value, extra_schema_id
    ) VALUES ($1, $2, $3)
  `,
    [
      company.name,
      JSON.stringify(company.extra_value || {}),
      company.extra_schema_id,
    ]
  );
}

export async function dbUpdateCompany({
  name,
  extra_value,
  extra_schema_id,
  id,
}: Partial<Company>): Promise<void> {
  if (id === undefined) {
    throw new Error("Company ID is required to update company");
  }
  const db = await getDatabaseInstance();
  await db.execute(
    `
    UPDATE company SET 
      name = $1, 
      extra_value = $2, 
      extra_schema_id = $3 
    WHERE id = $4
  `,
    [name, JSON.stringify(extra_value || {}), extra_schema_id, id]
  );
}

export async function dbGetAllCompanies(): Promise<Company[]> {
  const db = await getDatabaseInstance();
  const companies = await db.select(
    `
    SELECT * FROM company
    `
  );
  // {"id":1,"name":"mihoyou","created_at":"2024-08-18 03:24:04","updated_at":"2024-08-18 03:24:04","extra_value":null,"extra_schema_id":null}
  // @ts-ignore
  return companies.map((company) => ({
    id: company.id,
    name: company.name,
    created_at: company.created_at,
    updated_at: company.updated_at,
    extra_value: company.extra_value ? JSON.parse(company.extra_value) : null,
    extra_schema_id: company.extra_schema_id,
  }));
}
