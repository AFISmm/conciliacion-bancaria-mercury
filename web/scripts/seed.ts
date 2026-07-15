import "dotenv/config";
import { db } from "../lib/db";
import { companies } from "../lib/db/schema";
import { COMPANIES } from "../lib/companies";

async function main() {
  for (const c of COMPANIES) {
    await db.insert(companies).values(c).onConflictDoNothing();
  }
  console.log(`Seeded ${COMPANIES.length} companies.`);
  process.exit(0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
