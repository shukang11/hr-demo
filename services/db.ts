import Database from "@tauri-apps/plugin-sql";

let default_db: Database | null = null;

export async function getDatabaseInstance(): Promise<Database> {
  if (!default_db) {
    default_db = await Database.load("sqlite:mydatabase.db");
  }
  return default_db;
}


