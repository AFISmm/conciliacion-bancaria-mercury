import { verifySession } from "@/lib/auth/dal";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  await verifySession();
  return <>{children}</>;
}
