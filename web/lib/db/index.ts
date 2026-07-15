import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const connectionString = process.env.POSTGRES_URL ?? process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error("Missing POSTGRES_URL / DATABASE_URL environment variable");
}

// Module-scope singleton: reused across warm invocations of the same
// serverless function instance, which is the standard pattern on Vercel.
const client = postgres(connectionString, { prepare: false });

export const db = drizzle(client, { schema });
