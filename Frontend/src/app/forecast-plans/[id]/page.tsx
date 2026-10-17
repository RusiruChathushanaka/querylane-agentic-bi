import { ForecastPlans } from "@/components/forecast-plans";
import "@/app/dashboards.css";
import "@/app/planning.css";
export const metadata = { title: "Coherent Forecast Plan — Querylane" };
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ version?: string }>;
}) {
  const [{ id }, { version }] = await Promise.all([params, searchParams]);
  return (
    <ForecastPlans
      id={id}
      initialVersion={version ? Number(version) : undefined}
    />
  );
}
