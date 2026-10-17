import type { Metadata } from "next";
import { ReportsLibrary } from "@/components/reports-library";
import "@/app/dashboards.css";
export const metadata: Metadata = { title: "Reports — Querylane" };
export default function Page() {
  return <ReportsLibrary />;
}
