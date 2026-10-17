import type { Metadata } from "next";
import { ReportWorkspace } from "@/components/report-workspace";
import "@/app/dashboards.css";
export const metadata: Metadata = { title: "Analysis report — Querylane" };
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ version?: string }>;
}) {
  const { id } = await params;
  const { version } = await searchParams;
  const selected =
    version && /^\d+$/.test(version) ? Number(version) : undefined;
  return <ReportWorkspace key={id} id={id} initialVersion={selected} />;
}
