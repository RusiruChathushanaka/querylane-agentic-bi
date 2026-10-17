import type { ChartData, ChartMeasure } from "@/lib/types";

export function formatMeasure(
  value: unknown,
  measure?: Partial<ChartMeasure>,
  decimals = 2,
  compact = false,
): string {
  if (
    value === null ||
    value === undefined ||
    value === "" ||
    typeof value === "boolean"
  )
    return "—";
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  const percent = measure?.unit === "percent" && measure.percent_scale;
  const scaled = percent && measure.percent_scale === "whole" ? n / 100 : n;
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: measure?.unit === "count" ? 0 : decimals,
    ...(compact
      ? { notation: "compact" as const, maximumFractionDigits: 1 }
      : {}),
    ...(measure?.unit === "currency" && measure.currency
      ? { style: "currency", currency: measure.currency }
      : percent
        ? { style: "percent" }
        : {}),
  }).format(scaled);
}

export function dateLabel(value: unknown, compact = false): string {
  const text = String(value ?? "—");
  if (!/^\d{4}-\d{2}(-\d{2})?$/.test(text)) return text;
  const date = new Date(`${text.length === 7 ? `${text}-01` : text}T00:00:00Z`);
  if (Number.isNaN(date.getTime())) return text;
  return new Intl.DateTimeFormat("en-US", {
    month: compact ? "short" : "long",
    ...(text.length > 7 ? { day: "numeric" as const } : {}),
    year: "numeric",
    timeZone: "UTC",
  }).format(date);
}

export function changeLabel(
  info: {
    delta?: number;
    percent?: number | null;
    percentage_points?: number | null;
  },
  measure: ChartMeasure,
  decimals = 2,
): string {
  if (info.percentage_points != null)
    return `${info.percentage_points >= 0 ? "+" : ""}${new Intl.NumberFormat("en-US", { maximumFractionDigits: decimals }).format(info.percentage_points)} percentage points`;
  const delta = info.delta ?? 0;
  return `${delta >= 0 ? "+" : "−"}${formatMeasure(Math.abs(delta), measure, decimals)} · ${info.percent == null ? "percentage change unavailable (zero baseline)" : `${info.percent >= 0 ? "+" : ""}${info.percent.toFixed(decimals)}%`}`;
}

export function chartNotes(data: ChartData): string {
  const c = data.coverage;
  return [
    ...(data.prediction
      ? [
          `Observed through ${data.prediction.cutoff}; dashed series are conditional predictions. ${data.prediction.interval ? `Nominal ${data.prediction.interval.level * 100}% historical residual band; backtest coverage ${(data.prediction.interval.coverage * 100).toFixed(1)}%; future coverage is not guaranteed.` : "Validated intervals unavailable; uncertainty is not quantified."}`,
        ]
      : []),
    data.scope.start
      ? `${dateLabel(data.scope.start)} – ${dateLabel(data.scope.end)}`
      : `${c.selected_rows.toLocaleString()} saved observations`,
    `${c.plotted_rows.toLocaleString()} plotted`,
    c.sampled
      ? "Extrema-preserving sample; summaries use all selected observations"
      : "",
    c.omitted_categories
      ? `${c.omitted_categories} categories omitted; no Other grouping`
      : "",
    !c.complete ? "Partial source result; population totals unavailable" : "",
    data.visualization.partial_periods?.length
      ? "Incomplete periods excluded from period-change comparisons"
      : "",
  ]
    .filter(Boolean)
    .join(" · ");
}

export function exploreQuestion(
  title: string,
  dimension: string,
  value: unknown,
  measure: string,
  scope: string,
): string {
  return `Explore ${measure} for ${dimension.replaceAll("_", " ")} ${String(value)} in “${title}”. Scope: ${scope}. What contributes to this observation?`;
}

export function unitKey(measure: ChartMeasure): string {
  return `${measure.unit}:${measure.currency ?? ""}:${measure.percent_scale ?? ""}`;
}
