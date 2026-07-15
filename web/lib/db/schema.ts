import {
  pgTable,
  text,
  timestamp,
  numeric,
  bigint,
  boolean,
  uuid,
  primaryKey,
  index,
} from "drizzle-orm/pg-core";

export const companies = pgTable("companies", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
});

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name").notNull().default(""),
  passwordHash: text("password_hash").notNull(),
  verified: boolean("verified").notNull().default(false),
  verificationCode: text("verification_code"),
  verificationExpiresAt: timestamp("verification_expires_at", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const sessions = pgTable("sessions", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  expiresAt: timestamp("expires_at", { withTimezone: true }).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const periods = pgTable(
  "periods",
  {
    id: text("id").notNull(),
    companyId: text("company_id")
      .notNull()
      .references(() => companies.id),
    nombre: text("nombre").notNull(),
    banco: text("banco").notNull(),
    cuenta: text("cuenta").notNull(),
    saldoInicial: numeric("saldo_inicial", { precision: 18, scale: 2 }).notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [primaryKey({ columns: [t.companyId, t.id] })],
);

export const transactions = pgTable(
  "transactions",
  {
    id: bigint("id", { mode: "number" }).primaryKey().generatedAlwaysAsIdentity(),
    companyId: text("company_id").notNull(),
    periodId: text("period_id").notNull(),
    fecha: text("fecha").notNull(), // stored as YYYY-MM-DD text, matches source app
    descripcion: text("descripcion").notNull().default(""),
    movimiento: text("movimiento").notNull().default(""),
    tipo: text("tipo").notNull().$type<"cargo" | "abono">(),
    monto: numeric("monto", { precision: 18, scale: 2 }).notNull(),
    concepto: text("concepto").notNull().default(""),
    cuenta: text("cuenta").notNull().default(""),
    cuentaRef: text("cuenta_ref").notNull().default(""),
    origen: text("origen").notNull().default(""),
    nota: text("nota").notNull().default(""),
    estado: text("estado")
      .notNull()
      .default("Pendiente")
      .$type<"Pendiente" | "Conciliado" | "En revisión">(),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    index("idx_tx_period").on(t.companyId, t.periodId, t.fecha),
    index("idx_tx_estado").on(t.companyId, t.periodId, t.estado),
  ],
);

export const userSettings = pgTable("user_settings", {
  userId: uuid("user_id")
    .primaryKey()
    .references(() => users.id, { onDelete: "cascade" }),
  alegraEmail: text("alegra_email").notNull().default(""),
  alegraToken: text("alegra_token").notNull().default(""),
  currentCompanyId: text("current_company_id").references(() => companies.id),
  currentPeriodId: text("current_period_id"),
});
