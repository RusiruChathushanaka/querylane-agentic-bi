import type { Metadata } from "next";
import { DashboardWorkspace } from "@/components/dashboard-workspace";
import "@/app/dashboards.css";
export const metadata: Metadata = { title: "Shared dashboard — Querylane" };
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ mode?: string }>;
}) {
  const { id } = await params;
  const { mode } = await searchParams;
  return (
    <DashboardWorkspace
      key={id}
      id={id}
      initialEdit={mode === "edit"}
    />
  );
}
