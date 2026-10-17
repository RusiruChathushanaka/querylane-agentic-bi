import { MetricRevision } from "@/components/metric-revision";
import "@/app/dashboards.css";
import "@/app/planning.css";
export const metadata = { title: "Saved metric version — Querylane" };
export default async function Page({
  params,
}: {
  params: Promise<{ id: string; version: string }>;
}) {
  const p = await params;
  return <MetricRevision id={p.id} version={Number(p.version)} />;
}
