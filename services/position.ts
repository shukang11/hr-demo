import { getDatabaseInstance } from "./db";
import { Position } from "../types";
import useSWR from "swr";

export async function dbAddPosition(position: Position): Promise<void> {
  const db = await getDatabaseInstance();

  await db.execute(
    `
    INSERT INTO position (
      name, company_id, remark
    ) VALUES ($1, $2, $3)
  `,
    [position.name, position.company.id, position.remark]
  );
}

export async function dbUpdatePosition({
  id,
  name,
  company,
  remark,
}: Partial<Position>): Promise<void> {
  if (id === undefined) {
    throw new Error("Position ID is required to update position");
  }
  const db = await getDatabaseInstance();
  await db.execute(
    `
    UPDATE position SET 
      name = $1, 
      company_id = $2, 
      remark = $3 
    WHERE id = $4
  `,
    [name, company?.id, remark, id]
  );
}

export async function dbGetAllPositions(): Promise<Position[]> {
  const db = await getDatabaseInstance();
  const positions = await db.select(
    `
    SELECT p.*, c.name AS company_name, c.extra_value AS company_extra_value, c.extra_schema_id AS company_extra_schema_id
    FROM position p
    JOIN company c ON p.company_id = c.id
    `
  );
  // @ts-ignore
  return positions.map((position: any) => ({
    id: position.id,
    name: position.name,
    company: {
      id: position.company_id,
      name: position.company_name,
      extra_value: position.company_extra_value,
      extra_schema_id: position.company_extra_schema_id,
    },
    remark: position.remark,
    created_at: position.created_at,
    updated_at: position.updated_at,
  }));
}

export const positionsFetcher = () => dbGetAllPositions();

export const usePositions = () => {
  return useSWR("/get-positions", positionsFetcher);
};
