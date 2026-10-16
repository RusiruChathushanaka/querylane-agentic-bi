import type { Metadata } from "next";
import { DashboardWorkspace } from "@/components/dashboard-workspace";
import "@/app/dashboards.css";
export const metadata: Metadata = { title: "Shared dashboard — Querylane" };
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <DashboardWorkspace key={id} id={id} />;
}
