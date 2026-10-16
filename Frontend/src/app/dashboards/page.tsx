import type { Metadata } from "next";
import { DashboardsLibrary } from "@/components/dashboards-library";
import "@/app/dashboards.css";
export const metadata: Metadata = { title: "Dashboards — Querylane" };
export default function Page() {
  return <DashboardsLibrary />;
}
