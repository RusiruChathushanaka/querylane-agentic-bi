import { MetricsWorkspace } from "@/components/metrics-workspace";
import "@/app/dashboards.css";
import "@/app/planning.css";
export const metadata = { title: "Metric definition — Querylane" };
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  return <MetricsWorkspace id={(await params).id} />;
}
