CREATE TABLE "companies" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "periods" (
	"id" text NOT NULL,
	"company_id" text NOT NULL,
	"nombre" text NOT NULL,
	"banco" text NOT NULL,
	"cuenta" text NOT NULL,
	"saldo_inicial" numeric(18, 2) NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "periods_company_id_id_pk" PRIMARY KEY("company_id","id")
);
--> statement-breakpoint
CREATE TABLE "sessions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"expires_at" timestamp with time zone NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "transactions" (
	"id" bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "transactions_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1),
	"company_id" text NOT NULL,
	"period_id" text NOT NULL,
	"fecha" text NOT NULL,
	"descripcion" text DEFAULT '' NOT NULL,
	"movimiento" text DEFAULT '' NOT NULL,
	"tipo" text NOT NULL,
	"monto" numeric(18, 2) NOT NULL,
	"concepto" text DEFAULT '' NOT NULL,
	"cuenta" text DEFAULT '' NOT NULL,
	"cuenta_ref" text DEFAULT '' NOT NULL,
	"origen" text DEFAULT '' NOT NULL,
	"nota" text DEFAULT '' NOT NULL,
	"estado" text DEFAULT 'Pendiente' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "user_settings" (
	"user_id" uuid PRIMARY KEY NOT NULL,
	"alegra_email" text DEFAULT '' NOT NULL,
	"alegra_token" text DEFAULT '' NOT NULL,
	"current_company_id" text,
	"current_period_id" text
);
--> statement-breakpoint
CREATE TABLE "users" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"email" text NOT NULL,
	"name" text DEFAULT '' NOT NULL,
	"password_hash" text NOT NULL,
	"verified" boolean DEFAULT false NOT NULL,
	"verification_code" text,
	"verification_expires_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "users_email_unique" UNIQUE("email")
);
--> statement-breakpoint
ALTER TABLE "periods" ADD CONSTRAINT "periods_company_id_companies_id_fk" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "sessions" ADD CONSTRAINT "sessions_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_settings" ADD CONSTRAINT "user_settings_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_settings" ADD CONSTRAINT "user_settings_current_company_id_companies_id_fk" FOREIGN KEY ("current_company_id") REFERENCES "public"."companies"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "idx_tx_period" ON "transactions" USING btree ("company_id","period_id","fecha");--> statement-breakpoint
CREATE INDEX "idx_tx_estado" ON "transactions" USING btree ("company_id","period_id","estado");