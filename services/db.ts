import Database from "@tauri-apps/plugin-sql";

let default_db: Database | null = null;

export async function getDatabaseInstance(): Promise<Database> {
  if (!default_db) {
    default_db = await Database.load("sqlite:mydatabase.db");
  }
  return default_db;
}

export async function clearAllTables(): Promise<void> {
  const db = await getDatabaseInstance();
  const tables = await db.select<{ name: string }[]>(`SELECT name FROM sqlite_master WHERE type='table'`);
  for (const table of tables) {
    await db.execute(`DELETE FROM ${table.name}`);
  }
}
