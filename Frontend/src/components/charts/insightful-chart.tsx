"use client";

import "@/app/charts.css";

import { useEffect, useId, useRef, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  ComposedChart,
  Brush,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ReferenceDot,
  ReferenceLine,
  Scatter,
  ScatterChart,
  XAxis,
  YAxis,
} from "recharts";
import {
  ArrowUpRight,
  Download,
  Expand,
  RotateCcw,
  Sparkles,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { ChartContainer, ChartTooltip } from "@/components/ui/chart";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { api, backendUrl } from "@/lib/api";
import {
  chartNotes,
  changeLabel,
  dateLabel,
  exploreQuestion,
  formatMeasure,
  unitKey,
} from "@/lib/chart-format";
import { downloadBlob, exportChartPng } from "@/lib/chart-export";
import { usePreferences } from "@/hooks/use-preferences";
import type { Artifact, ChartData, ChartMeasure, ChartRow } from "@/lib/types";

const palette = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];
function categoryColor(value: unknown) {
  const hash = Array.from(String(value)).reduce(
    (n, c) => (n * 31 + c.charCodeAt(0)) >>> 0,
    0,
  );
  return palette[hash % palette.length];
}
const label = (field: string) => field.replaceAll("_", " ");
const numeric = /int|float|double|decimal|numeric|number|real/i;

function Values({
  row,
  measures,
  decimals,
}: {
  row: ChartRow;
  measures: ChartMeasure[];
  decimals: number;
}) {
  return (
    <dl className="chart-value-list">
      {measures.map((m) => {
        const detail = row._detail?.[m.field];
        return (
          <div key={m.field}>
            <dt>{m.label}</dt>
            <dd>{formatMeasure(row[m.field], m, decimals)}</dd>
            {detail?.previous_label && (
              <small>
                vs {dateLabel(detail.previous_label)}:{" "}
                {changeLabel(detail, m, decimals)}
              </small>
            )}
            {detail?.variance && (
              <small>
                {label(detail.actual_field ?? "Actual")} vs {m.label}:{" "}
                {changeLabel(detail.variance, m, decimals)}
              </small>
            )}
            {detail?.share != null && (
              <small>{detail.share.toFixed(1)}% of complete result total</small>
            )}
          </div>
        );
      })}
    </dl>
  );
}

function Plot({
  data,
  view,
  measures,
  colors,
  primary,
  highlight,
  decimals,
  scatterX,
  scatterY,
  onPin,
  onRange,
}: {
  data: ChartData;
  view: string;
  measures: ChartMeasure[];
  colors: Record<string, string>;
  primary: string;
  highlight: boolean;
  decimals: number;
  scatterX: string;
  scatterY: string;
  onPin: (row: ChartRow) => void;
  onRange: (start: string, end: string) => void;
}) {
  const x = data.visualization.x ?? "";
  const temporal = data.visualization.dimension_kind === "temporal";
  const horizontal =
    view === "bar" &&
    !temporal &&
    data.rows.some((r) => String(r[x]).length > 12);
  const groupMeasure = measures[0];
  const ticks = (v: unknown) => formatMeasure(v, groupMeasure, decimals, true);
  const name = (v: unknown) =>
    temporal ? dateLabel(v, true) : String(v ?? "Missing");
  const config = Object.fromEntries(
    measures.map((m) => [m.field, { label: m.label, color: colors[m.field] }]),
  );
  const pointClick = (state: { activeIndex?: string | number | null }) => {
    const index = Number(state.activeIndex);
    if (
      state.activeIndex != null &&
      Number.isInteger(index) &&
      data.rows[index] &&
      !data.rows[index]._gap
    )
      onPin(data.rows[index]);
  };
  const tooltip = (
    <ChartTooltip
      content={({ active, payload }) => {
        const row = payload?.[0]?.payload as ChartRow | undefined;
        if (!active || !row || row._gap) return null;
        return (
          <div
            className="insight-tooltip"
            role="status"
            aria-live="polite"
            aria-atomic="true"
          >
            <strong>
              {name(
                view === "scatter" && data.identity
                  ? row[data.identity]
                  : (row[x] ?? "Observation"),
              )}
            </strong>
            <Values row={row} measures={measures} decimals={decimals} />
          </div>
        );
      }}
      wrapperStyle={{ zIndex: 5, pointerEvents: "none" }}
    />
  );
  const axes = (
    <>
      <CartesianGrid vertical={false} strokeDasharray="3 5" />
      <XAxis
        dataKey={horizontal ? undefined : x}
        type={horizontal ? "number" : "category"}
        tickLine={false}
        axisLine={false}
        minTickGap={30}
        tickMargin={10}
        interval={temporal ? "preserveStartEnd" : undefined}
        tickFormatter={horizontal ? ticks : name}
        domain={
          horizontal
            ? [
                (min: number) => Math.min(0, min),
                (max: number) => Math.max(0, max),
              ]
            : undefined
        }
      />
      <YAxis
        dataKey={horizontal ? x : undefined}
        type={horizontal ? "category" : "number"}
        tickLine={false}
        axisLine={false}
        width={horizontal ? 130 : 80}
        interval={horizontal ? 0 : undefined}
        tickFormatter={
          horizontal
            ? (v) =>
                String(v).length > 20 ? `${String(v).slice(0, 18)}…` : String(v)
            : ticks
        }
        domain={
          horizontal
            ? undefined
            : view === "bar"
              ? [
                  (min: number) => Math.min(0, min),
                  (max: number) => Math.max(0, max),
                ]
              : undefined
        }
      />
      {view === "bar" &&
        (horizontal ? (
          <ReferenceLine x={0} stroke="var(--muted-foreground)" />
        ) : (
          <ReferenceLine y={0} stroke="var(--muted-foreground)" />
        ))}
      {tooltip}
      {temporal && data.rows.length > 12 && (
        <Brush
          ariaLabel="Chart date range"
          dataKey={x}
          height={28}
          stroke="var(--muted-foreground)"
          fill="var(--background)"
          travellerWidth={12}
          tickFormatter={(v) => dateLabel(v, true)}
          onChange={({ startIndex, endIndex }) => {
            if (
              startIndex != null &&
              endIndex != null &&
              (startIndex > 0 || endIndex < data.rows.length - 1)
            )
              onRange(
                String(data.rows[startIndex][x]),
                String(data.rows[endIndex][x]),
              );
          }}
        />
      )}
    </>
  );
  const references =
    highlight && temporal && data.coverage.unique_dimension
      ? data.annotations
          .filter(
            (a) =>
              a.field === primary &&
              a.value != null &&
              !(
                a.kind === "latest" &&
                data.annotations.some((b) => b.kind === "peak" && b.x === a.x)
              ),
          )
          .map((a, i) => (
            <ReferenceDot
              key={`${a.kind}-${i}`}
              x={a.x as string}
              y={a.value as number}
              r={a.kind === "latest" ? 4 : 5}
              fill={colors[primary]}
              stroke="var(--background)"
              strokeWidth={2}
              label={{
                value:
                  a.kind === "latest"
                    ? "Latest"
                    : data.annotations.some(
                          (b) => b.kind === "latest" && b.x === a.x,
                        )
                      ? "Peak · Latest"
                      : "Peak",
                position: "top",
                fill: "var(--foreground)",
                fontSize: 11,
              }}
            />
          ))
      : null;
  const lineProps = (m: ChartMeasure) => ({
    dataKey: m.field,
    name: m.label ?? m.field,
    stroke: colors[m.field],
    strokeWidth: 2.3,
    strokeDasharray:
      m.role === "target" || m.role === "comparison" ? "6 4" : undefined,
    connectNulls: false,
    isAnimationActive: false,
  });
  const plotHeight = horizontal ? Math.max(300, data.rows.length * 38) : 320;
  return (
    <ChartContainer
      config={config}
      className="analytics-chart insight-plot"
      style={{ height: plotHeight }}
      role="group"
      aria-label={`${data.visualization.title}: ${measures.map((m) => m.label).join(", ")}`}
    >
      {view === "bar" ? (
        <ComposedChart
          accessibilityLayer
          data={data.rows}
          layout={horizontal ? "vertical" : "horizontal"}
          margin={{ top: 24, right: 22, bottom: 8, left: 0 }}
          onClick={pointClick}
        >
          {axes}
          {measures.map((m) =>
            m.role === "target" || m.role === "comparison" ? (
              <Line key={m.field} {...lineProps(m)} dot={{ r: 3 }} />
            ) : (
              <Bar
                key={m.field}
                dataKey={m.field}
                name={m.label ?? m.field}
                fill={colors[m.field]}
                maxBarSize={42}
                radius={3}
                isAnimationActive={false}
                activeBar={{ stroke: "var(--foreground)", strokeWidth: 2 }}
              >
                {data.rows.map((row, index) => (
                  <Cell
                    key={index}
                    fill={
                      highlight &&
                      m.field === primary &&
                      row[m.field] !== data.stats.max
                        ? "var(--chart-context)"
                        : colors[m.field]
                    }
                  />
                ))}
              </Bar>
            ),
          )}
        </ComposedChart>
      ) : view === "line" || view === "area" ? (
        view === "line" ? (
          <LineChart
            accessibilityLayer
            data={data.rows}
            margin={{ top: 28, right: 32, bottom: 8, left: 0 }}
            onClick={pointClick}
          >
            {axes}
            {measures.map((m) => (
              <Line
                key={m.field}
                {...lineProps(m)}
                dot={data.rows.length < 15}
                activeDot={{ r: 5 }}
              />
            ))}
            {references}
          </LineChart>
        ) : (
          <AreaChart
            accessibilityLayer
            data={data.rows}
            margin={{ top: 28, right: 32, bottom: 8, left: 0 }}
            onClick={pointClick}
          >
            {axes}
            {measures.map((m) => (
              <Area
                key={m.field}
                {...lineProps(m)}
                fill={colors[m.field]}
                fillOpacity={m.role === "target" ? 0 : 0.1}
              />
            ))}
            {references}
          </AreaChart>
        )
      ) : view === "pie" && data.composition ? (
        <PieChart accessibilityLayer>
          <Pie
            data={data.rows}
            dataKey={primary}
            nameKey={x}
            innerRadius="55%"
            outerRadius="80%"
            isAnimationActive={false}
            onClick={(row) => onPin(row.payload as ChartRow)}
            label={({ percent }) => `${((percent ?? 0) * 100).toFixed(0)}%`}
          >
            {data.rows.map((row, index) => (
              <Cell
                key={index}
                fill={categoryColor(row[x])}
                stroke="var(--background)"
                strokeWidth={2}
              />
            ))}
          </Pie>
          {tooltip}
        </PieChart>
      ) : (
        <ScatterChart
          accessibilityLayer
          margin={{ top: 16, right: 22, bottom: 26, left: 10 }}
        >
          <CartesianGrid strokeDasharray="3 5" />
          <XAxis
            type="number"
            dataKey={scatterX}
            name={label(scatterX)}
            tickFormatter={(v) =>
              formatMeasure(
                v,
                data.visualization.measures.find((m) => m.field === scatterX),
                decimals,
                true,
              )
            }
            label={{ value: label(scatterX), position: "bottom", offset: 8 }}
          />
          <YAxis
            type="number"
            dataKey={scatterY}
            name={label(scatterY)}
            width={85}
            tickFormatter={(v) =>
              formatMeasure(
                v,
                data.visualization.measures.find((m) => m.field === scatterY),
                decimals,
                true,
              )
            }
            label={{
              value: label(scatterY),
              angle: -90,
              position: "insideLeft",
            }}
          />
          {tooltip}
          <Scatter
            data={data.rows.filter(
              (r) => r[scatterX] != null && r[scatterY] != null,
            )}
            fill={colors[primary] ?? palette[0]}
            isAnimationActive={false}
            onClick={(row) => onPin(row.payload as ChartRow)}
          />
        </ScatterChart>
      )}
    </ChartContainer>
  );
}

export default function InsightfulChart({
  artifact,
  view,
  onExplore,
}: {
  artifact: Artifact;
  view: string;
  onExplore?: (question: string) => void;
}) {
  const { preferences } = usePreferences();
  const id = useId();
  const [range, setRange] = useState({ start: "", end: "" });
  const [primary, setPrimary] = useState("");
  const [order, setOrder] = useState("value_desc");
  const [top, setTop] = useState("10");
  const [hidden, setHidden] = useState<Record<string, boolean>>({});
  const [pin, setPin] = useState<ChartRow | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportDialog, setExportDialog] = useState<"png" | "csv" | null>(null);
  const [scatterAxes, setScatterAxes] = useState({ x: "", y: "" });
  const [loaded, setLoaded] = useState<{
    key: string;
    data?: ChartData;
    error?: string;
  } | null>(null);
  const [retry, setRetry] = useState(0);
  const brushTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const params = new URLSearchParams({
    view,
    order,
    top,
    ...(range.start ? { start: range.start } : {}),
    ...(range.end ? { end: range.end } : {}),
    ...(primary ? { primary } : {}),
  });
  const key = `${artifact.id}?${params}&retry=${retry}`;
  useEffect(() => {
    const controller = new AbortController();
    const query = key.split("?")[1];
    api<ChartData>(`/artifacts/${artifact.id}/chart-data?${query}`, {
      signal: controller.signal,
    })
      .then((data) => setLoaded({ key, data }))
      .catch((error) => {
        if (!controller.signal.aborted)
          setLoaded({ key, error: error.message });
      });
    return () => controller.abort();
  }, [artifact.id, key]);
  useEffect(
    () => () => {
      if (brushTimer.current) clearTimeout(brushTimer.current);
    },
    [],
  );
  const data = loaded?.key === key ? loaded.data : undefined;
  const error = loaded?.key === key ? loaded.error : undefined;
  const measures = data?.visualization.measures ?? [];
  const current = data?.primary ?? "";
  const shown = measures.filter(
    (m) =>
      !(
        hidden[m.field] ??
        (!preferences.chartComparisons &&
          ["target", "comparison"].includes(m.role))
      ),
  );
  const colors = Object.fromEntries(
    measures.map((m, i) => [
      m.field,
      m.role === "target" || m.role === "comparison"
        ? "var(--chart-comparison)"
        : palette[i % palette.length],
    ]),
  );
  const activeMeasure = measures.find((m) => m.field === current);
  const temporal = data?.visualization.dimension_kind === "temporal";
  const decimals = Number(preferences.decimals);
  const notes = data ? chartNotes(data) : "";
  const groups = Object.values(
    shown.reduce<Record<string, ChartMeasure[]>>((groups, m) => {
      (groups[unitKey(m)] ??= []).push(m);
      return groups;
    }, {}),
  );
  const numericFields = artifact.columns
    .filter((c) => numeric.test(c.type))
    .slice(0, 4)
    .map((c) => c.name);
  const scatterX = scatterAxes.x || numericFields[0];
  const scatterY = scatterAxes.y || numericFields[1];
  const effectiveView = view === "pie" && !data?.composition ? "bar" : view;
  const pinned = pin && data?.rows.find((r) => r._key === pin._key && !r._gap);
  const reset = () => {
    setRange({ start: "", end: "" });
    setPrimary("");
    setOrder("value_desc");
    setTop("10");
    setHidden({});
    setPin(null);
    setScatterAxes({ x: "", y: "" });
  };
  const subtitle = activeMeasure
    ? `${activeMeasure.label} · ${activeMeasure.unit === "currency" ? activeMeasure.currency : activeMeasure.unit}${temporal ? ` · ${data?.visualization.granularity ?? "observed"} observations` : ""}`
    : "Saved query result";

  async function download() {
    if (!data || !exportDialog) return;
    setExporting(true);
    try {
      if (exportDialog === "csv") {
        const response = await fetch(
          `${await backendUrl()}/api/v1/artifacts/${artifact.id}/export.csv`,
          { cache: "no-store" },
        );
        if (!response.ok)
          throw new Error("The saved result could not be exported. Try again.");
        downloadBlob(
          await response.blob(),
          `querylane-${artifact.id}-${artifact.complete ? "complete" : "partial"}.csv`,
        );
      } else {
        const root = document.getElementById(
          `${id}-${expanded ? "expanded" : "inline"}`,
        );
        if (!root) throw new Error("The chart is unavailable.");
        await exportChartPng(
          root,
          artifact.title,
          subtitle,
          notes,
          effectiveView === "pie"
            ? data.rows.map((row) => ({
                label: String(row[data.visualization.x ?? ""]),
                color: categoryColor(row[data.visualization.x ?? ""]),
              }))
            : shown.map((m) => ({
                label: `${m.label} (${m.unit === "currency" ? m.currency : m.unit})`,
                color: colors[m.field],
                dashed: ["target", "comparison"].includes(m.role),
              })),
        );
      }
      toast.success(`${exportDialog.toUpperCase()} download ready`, {
        description:
          exportDialog === "csv"
            ? `${artifact.row_count.toLocaleString()} saved rows · ${artifact.complete ? "complete result" : "partial source result"}`
            : "Current view, units, and scope notes included.",
      });
      setExportDialog(null);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Export failed.");
    } finally {
      setExporting(false);
    }
  }

  function content(isExpanded: boolean) {
    return (
      <div
        className="chart-explorer"
        id={`${id}-${isExpanded ? "expanded" : "inline"}`}
        aria-busy={!data && !error}
      >
        <p className="chart-subtitle">{subtitle}</p>
        {!data && !error && (
          <div className="chart-loading">
            Preparing the complete saved result…
          </div>
        )}
        {error && (
          <div role="alert" className="chart-error">
            <p>{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setRetry(retry + 1)}
            >
              Retry chart
            </Button>
            <p>The underlying table and evidence remain available.</p>
          </div>
        )}
        {data && (
          <>
            <div
              className="chart-toolbar"
              role="group"
              aria-label="Chart exploration controls"
            >
              {measures.length > 1 && (
                <label>
                  Primary measure
                  <select
                    value={current}
                    onChange={(e) => {
                      setPrimary(e.target.value);
                      setHidden({ ...hidden, [e.target.value]: false });
                      setPin(null);
                    }}
                  >
                    {measures.map((m) => (
                      <option key={m.field} value={m.field}>
                        {m.label}
                      </option>
                    ))}
                  </select>
                </label>
              )}
              {temporal ? (
                <>
                  <label>
                    Start date
                    <input
                      type="date"
                      value={range.start}
                      onChange={(e) => {
                        setRange({ ...range, start: e.target.value });
                        setPin(null);
                      }}
                    />
                  </label>
                  <label>
                    End date
                    <input
                      type="date"
                      value={range.end}
                      onChange={(e) => {
                        setRange({ ...range, end: e.target.value });
                        setPin(null);
                      }}
                    />
                  </label>
                </>
              ) : (
                effectiveView !== "scatter" && (
                  <>
                    <label>
                      Order
                      <select
                        value={order}
                        onChange={(e) => setOrder(e.target.value)}
                      >
                        <option value="value_desc">Highest first</option>
                        <option value="value_asc">Lowest first</option>
                        <option value="label">Name A–Z</option>
                        <option value="original">Query order</option>
                      </select>
                    </label>
                    <label>
                      Categories
                      <select
                        value={top}
                        onChange={(e) => setTop(e.target.value)}
                      >
                        {[5, 10, 20].map((n) => (
                          <option key={n} value={n}>
                            Top {n}
                          </option>
                        ))}
                      </select>
                    </label>
                  </>
                )
              )}
              {effectiveView === "scatter" && (
                <>
                  {["x", "y"].map((axis) => (
                    <label key={axis}>
                      {axis.toUpperCase()} measure
                      <select
                        value={axis === "x" ? scatterX : scatterY}
                        onChange={(e) =>
                          setScatterAxes({
                            x: scatterX,
                            y: scatterY,
                            [axis]: e.target.value,
                          })
                        }
                      >
                        {numericFields.map((f) => (
                          <option key={f} value={f}>
                            {label(f)}
                          </option>
                        ))}
                      </select>
                    </label>
                  ))}
                </>
              )}
              <div className="chart-actions">
                <Button variant="ghost" size="sm" onClick={reset}>
                  <RotateCcw />
                  Reset
                </Button>
                {!isExpanded && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpanded(true)}
                  >
                    <Expand />
                    Expand
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!data.rows.length || exporting || view === "kpi"}
                  onClick={() => setExportDialog("png")}
                >
                  <Download />
                  PNG
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={exporting}
                  onClick={() => setExportDialog("csv")}
                >
                  CSV
                </Button>
              </div>
            </div>
            {!data.coverage.complete && (
              <p className="chart-warning">
                Partial source result. Highlights describe observed rows;
                population totals and shares are unavailable.
              </p>
            )}
            {preferences.chartHighlights && activeMeasure && (
              <ul
                className="chart-insights"
                aria-label="Factual chart insights"
              >
                {data.insights
                  .filter(
                    (i) => preferences.chartComparisons || i.kind !== "target",
                  )
                  .map((insight, i) => (
                    <li key={i}>
                      <Sparkles aria-hidden />
                      <span>
                        <strong>
                          {insight.kind === "change"
                            ? "Period change"
                            : insight.kind === "share"
                              ? "Share of total"
                              : insight.kind === "target"
                                ? "Variance to target"
                                : insight.kind === "leader"
                                  ? "Leading category"
                                  : "Highest observed"}
                        </strong>
                        <b>
                          {insight.kind === "share"
                            ? `${insight.value.toFixed(1)}%`
                            : insight.kind === "change" ||
                                insight.kind === "target"
                              ? changeLabel(insight, activeMeasure, decimals)
                              : formatMeasure(
                                  insight.value,
                                  activeMeasure,
                                  decimals,
                                )}
                        </b>
                        <small>
                          {temporal ? dateLabel(insight.label) : insight.label}
                          {insight.previous_label
                            ? ` vs ${dateLabel(insight.previous_label)}`
                            : ""}
                        </small>
                      </span>
                    </li>
                  ))}
              </ul>
            )}
            {view === "pie" && !data.composition && (
              <p className="chart-warning">
                A donut requires 2–6 distinct categories with complete,
                additive, nonnegative values. Showing bars instead.
              </p>
            )}
            {view !== "kpi" &&
              effectiveView !== "scatter" &&
              measures.length > 1 && (
                <div
                  className="chart-legend"
                  role="group"
                  aria-label="Visible chart series"
                >
                  {measures.map((m) => {
                    const visible = shown.some((s) => s.field === m.field);
                    return (
                      <button
                        type="button"
                        key={m.field}
                        aria-pressed={visible}
                        disabled={visible && shown.length === 1}
                        onClick={() => {
                          setHidden({ ...hidden, [m.field]: visible });
                          if (visible && m.field === current)
                            setPrimary(
                              shown.find((other) => other.field !== m.field)
                                ?.field ?? current,
                            );
                          setPin(null);
                        }}
                      >
                        <span
                          style={{ background: colors[m.field] }}
                          className={
                            m.role === "target" || m.role === "comparison"
                              ? "is-comparator"
                              : ""
                          }
                        />
                        {m.label}
                        {!visible && <small>hidden</small>}
                      </button>
                    );
                  })}
                </div>
              )}
            {view === "kpi" ? null : data.warning ? (
              <p role="status" className="chart-warning">
                {data.warning}
              </p>
            ) : !data.rows.length ? (
              <p className="empty-result">
                No observations in this range. Reset or broaden the dates.
              </p>
            ) : (
              <div className="chart-export-surface">
                {(effectiveView === "scatter" || effectiveView === "pie"
                  ? [shown]
                  : groups
                )
                  .filter((g) => g.length)
                  .map((group, index) => (
                    <figure key={group.map((m) => m.field).join("-")}>
                      <figcaption className="chart-unit-label">
                        {group.map((m) => m.label).join(" · ")} ·{" "}
                        {group[0].unit === "currency"
                          ? group[0].currency
                          : group[0].unit}
                      </figcaption>
                      <Plot
                        data={data}
                        view={effectiveView}
                        measures={
                          effectiveView === "scatter"
                            ? [scatterX, scatterY]
                                .filter(
                                  (field, index, fields) =>
                                    fields.indexOf(field) === index,
                                )
                                .map(
                                  (field) =>
                                    measures.find((m) => m.field === field) ?? {
                                      field,
                                      label: label(field),
                                      unit: "number",
                                      currency: null,
                                      percent_scale: null,
                                      additive: false,
                                      role: "measure",
                                      compares_to: null,
                                      direction: "neutral",
                                    },
                                )
                            : group
                        }
                        colors={colors}
                        primary={current}
                        highlight={
                          preferences.chartHighlights &&
                          group.some((m) => m.field === current)
                        }
                        decimals={decimals}
                        scatterX={scatterX}
                        scatterY={scatterY}
                        onPin={setPin}
                        onRange={(start, end) => {
                          if (brushTimer.current)
                            clearTimeout(brushTimer.current);
                          brushTimer.current = setTimeout(() => {
                            setRange({
                              start:
                                start.slice(0, 10).length === 7
                                  ? `${start}-01`
                                  : start.slice(0, 10),
                              end:
                                end.length === 7
                                  ? `${end}-01`
                                  : end.slice(0, 10),
                            });
                            setPin(null);
                          }, 400);
                        }}
                      />
                      <span className="sr-only">
                        Plot {index + 1}. Use left and right arrow keys to
                        inspect values. Use the inspect observation control
                        below to pin details.
                      </span>
                    </figure>
                  ))}
              </div>
            )}
            {view !== "kpi" && data.rows.length > 0 && (
              <label className="chart-inspect">
                Inspect observation
                <select
                  value={pinned?._key ?? ""}
                  onChange={(e) =>
                    setPin(
                      data.rows.find(
                        (r) => String(r._key) === e.target.value,
                      ) ?? null,
                    )
                  }
                >
                  <option value="">Select a point or use this list…</option>
                  {data.rows
                    .filter((r) => !r._gap)
                    .map((r, i) => (
                      <option key={i} value={r._key}>
                        {data.visualization.x
                          ? temporal
                            ? dateLabel(r[data.visualization.x])
                            : String(r[data.visualization.x] ?? "Missing")
                          : `Observation ${i + 1}`}
                      </option>
                    ))}
                </select>
              </label>
            )}
            {effectiveView === "pie" && data.composition && (
              <div
                className="chart-legend"
                role="group"
                aria-label="Composition categories"
              >
                {data.rows.map((row, i) => (
                  <button key={i} type="button" onClick={() => setPin(row)}>
                    <span
                      style={{
                        background: categoryColor(
                          row[data.visualization.x ?? ""],
                        ),
                      }}
                    />
                    {String(row[data.visualization.x ?? ""])}
                  </button>
                ))}
              </div>
            )}
            {pinned && (
              <div
                className="chart-pinned"
                role="group"
                aria-label="Selected observation"
              >
                <div>
                  <strong>
                    {effectiveView === "scatter" && data.identity
                      ? String(pinned[data.identity])
                      : temporal
                        ? dateLabel(pinned[data.visualization.x ?? ""])
                        : String(
                            pinned[data.visualization.x ?? ""] ??
                              (data.identity
                                ? pinned[data.identity]
                                : "Observation"),
                          )}
                  </strong>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label="Close selected observation"
                    onClick={() => setPin(null)}
                  >
                    <X />
                  </Button>
                </div>
                <Values
                  row={pinned}
                  measures={
                    effectiveView === "scatter"
                      ? measures.filter(
                          (m) => m.field === scatterX || m.field === scatterY,
                        )
                      : shown
                  }
                  decimals={decimals}
                />
                {onExplore && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      onExplore(
                        exploreQuestion(
                          artifact.title,
                          data.dimension_label,
                          pinned[data.visualization.x ?? ""] ?? pinned._key,
                          activeMeasure?.label ?? current,
                          notes,
                        ),
                      );
                      setExpanded(false);
                    }}
                  >
                    <ArrowUpRight />
                    Explore this
                  </Button>
                )}
              </div>
            )}
            <p className="chart-caption" id={`${id}-scope-${isExpanded}`}>
              {notes}. Switch to Table for the saved data and SQL evidence.
            </p>
          </>
        )}
      </div>
    );
  }

  return (
    <>
      {content(false)}
      <Dialog open={expanded} onOpenChange={setExpanded}>
        <DialogContent className="chart-expanded">
          <DialogHeader>
            <DialogTitle>{artifact.title}</DialogTitle>
            <DialogDescription>
              Explore the saved result. Controls change this view without
              running another query.
            </DialogDescription>
          </DialogHeader>
          {content(true)}
        </DialogContent>
      </Dialog>
      <Dialog
        open={Boolean(exportDialog)}
        onOpenChange={(open) => {
          if (!exporting && !open) setExportDialog(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Download {exportDialog?.toUpperCase() ?? "result"}
            </DialogTitle>
            <DialogDescription>
              {exportDialog === "csv"
                ? `${artifact.row_count.toLocaleString()} saved rows with original columns. ${artifact.complete ? "Complete source inputs." : "Partial source inputs: this is not a complete population."} Visual Top N and sampling do not limit this download.`
                : `Current visible chart and series, with units and scope notes. ${notes}`}
            </DialogDescription>
          </DialogHeader>
          <Button onClick={() => void download()} disabled={exporting}>
            {exporting
              ? "Preparing download…"
              : `Download ${exportDialog?.toUpperCase() ?? "result"}`}
          </Button>
        </DialogContent>
      </Dialog>
    </>
  );
}
