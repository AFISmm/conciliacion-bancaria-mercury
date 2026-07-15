import { getCurrentUser } from "@/lib/auth/dal";
import { getUserSettings } from "@/lib/queries/settings";
import { listPeriods } from "@/lib/queries/periods";
import { listTransactions } from "@/lib/queries/transactions";
import { COMPANIES } from "@/lib/companies";
import { Dashboard } from "@/components/Dashboard";

export default async function DashboardPage() {
  const user = await getCurrentUser();
  const settings = await getUserSettings(user!.id);

  const currentCompanyId = settings.currentCompanyId;
  const periods = currentCompanyId ? await listPeriods(currentCompanyId) : [];

  const currentPeriodId = periods.find((p) => p.id === settings.currentPeriodId)?.id ?? periods[0]?.id ?? null;
  const currentPeriod = periods.find((p) => p.id === currentPeriodId) ?? null;

  const transactions =
    currentCompanyId && currentPeriod ? await listTransactions(currentCompanyId, currentPeriod.id) : [];

  return (
    <Dashboard
      userName={user!.name || user!.email}
      companies={[...COMPANIES]}
      currentCompanyId={currentCompanyId}
      periods={periods}
      currentPeriod={currentPeriod}
      transactions={transactions}
      alegraEmail={settings.alegraEmail}
      alegraToken={settings.alegraToken}
    />
  );
}
