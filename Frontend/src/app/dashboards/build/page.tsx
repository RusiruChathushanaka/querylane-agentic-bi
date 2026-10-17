import { DashboardBuilder } from "@/components/dashboard-builder";
import "@/app/dashboards.css";
import "@/app/planning.css";
export const metadata = { title: "AI Dashboard Builder — Querylane" };
export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ dashboard?: string; build?: string }>;
}) {
  const p = await searchParams;
  return <DashboardBuilder dashboardId={p.dashboard} buildId={p.build} />;
}
