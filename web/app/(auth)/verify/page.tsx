import { VerifyForm } from "@/components/auth/VerifyForm";

export default async function VerifyPage({
  searchParams,
}: {
  searchParams: Promise<{ email?: string; devCode?: string }>;
}) {
  const params = await searchParams;
  return <VerifyForm email={params.email ?? ""} initialDevCode={params.devCode} />;
}
