"use client";

import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  Scatter,
  ScatterChart,
  XAxis,
  YAxis,
} from "recharts";
import {
  Braces,
  CheckCheck,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Copy,
  Database,
  GitMerge,
  Info,
  Table2,
} from "lucide-react";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api } from "@/lib/api";
import type { Artifact } from "@/lib/types";
import { usePreferences } from "@/hooks/use-preferences";
import { AnimatedNumber } from "@/components/motion/animated-number";
import { motion } from "motion/react";
import { useAppMotion } from "@/hooks/use-app-motion";

const colors = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];
const MotionCardContent = motion.create(CardContent);
const numericType = /int|float|double|decimal|numeric|number|real/i;
const human = (value: string) => value.replaceAll("_", " ");
function display(value: unknown, format = "number", decimals = 2) {
  if (value === null || value === undefined) return "—";
  const number = Number(value);
  if (!Number.isFinite(number) || value === "" || typeof value === "boolean")
    return String(value);
  return (
    new Intl.NumberFormat("en-US", {
      maximumFractionDigits: decimals,
      minimumFractionDigits: 0,
      ...(format === "currency" ? { style: "currency", currency: "USD" } : {}),
    }).format(number) + (format === "percent" ? "%" : "")
  );
}

export default function ResultCard({ artifact }: { artifact: Artifact }) {
  const { preferences } = usePreferences();
  const { reduced } = useAppMotion();
  const decimals = Number(preferences.decimals);
  const [view, setView] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [tableRows, setTableRows] = useState(artifact.rows.slice(0, 250));
  const [tableError, setTableError] = useState("");
  const [loading, setLoading] = useState(false);
  const numeric = artifact.columns
    .filter((column) => numericType.test(column.type))
    .map((column) => column.name);
  const x =
    artifact.visualization.x ??
    artifact.columns.find((column) => !numeric.includes(column.name))?.name ??
    artifact.columns[0]?.name;
  const ys = artifact.visualization.y.length
    ? artifact.visualization.y.filter((column) => numeric.includes(column))
    : numeric.slice(0, 2);
  const chartable = Boolean(x && ys.length && artifact.rows.length);
  const pieable =
    chartable &&
    ys.length === 1 &&
    artifact.rows.every(
      (row) => row[ys[0]] !== null && Number(row[ys[0]]) >= 0,
    );
  const options = [
    "table",
    ...(numeric.length && artifact.row_count === 1 ? ["kpi"] : []),
    ...(chartable && artifact.row_count > 1 ? ["bar", "line", "area"] : []),
    ...(pieable && artifact.row_count > 1 ? ["pie"] : []),
    ...(numeric.length >= 2 && artifact.row_count > 1 ? ["scatter"] : []),
  ];
  const preferred =
    view ??
    (preferences.visualization === "auto"
      ? artifact.visualization.type
      : preferences.visualization);
  const selected = options.includes(preferred)
    ? preferred
    : options.includes(artifact.visualization.type)
      ? artifact.visualization.type
      : "table";
  const data = artifact.rows
    .slice(0, 60)
    .map((row) =>
      Object.fromEntries(
        Object.entries(row).map(([key, value]) => [
          key,
          numeric.includes(key) && value !== null ? Number(value) : value,
        ]),
      ),
    );
  const config = Object.fromEntries(
    ys.map((column, index) => [
      column,
      { label: human(column), color: colors[index % colors.length] },
    ]),
  ) satisfies ChartConfig;
  const ticks = (value: number) =>
    new Intl.NumberFormat("en", {
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(value);

  useEffect(() => {
    if (selected !== "table" || !artifact.page_count) return;
    let cancelled = false;
    api<{ rows: Record<string, unknown>[] }>(
      `/artifacts/${artifact.id}/pages/${page}`,
    )
      .then((result) => {
        if (!cancelled) {
          setTableRows(result.rows);
          setTableError("");
          setLoading(false);
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setTableError(error.message);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [selected, artifact.id, artifact.page_count, page]);

  function changeView(value: string) {
    setView(value);
    toast.success("Visualization updated", {
      id: "visualization-choice",
      description: `${value === "kpi" ? "KPI cards" : `${value[0].toUpperCase()}${value.slice(1)} view`} · underlying data and evidence are unchanged.`,
      duration: 2600,
    });
    if (value === "table" && artifact.page_count) setLoading(true);
  }

  const axes = (
    <>
      <CartesianGrid vertical={false} strokeDasharray="3 5" />
      <XAxis
        dataKey={x}
        tickLine={false}
        axisLine={false}
        tickMargin={12}
        minTickGap={18}
      />
      <YAxis
        tickLine={false}
        axisLine={false}
        tickFormatter={ticks}
        width={56}
      />
      <ChartTooltip
        content={
          <ChartTooltipContent
            valueFormatter={(value) =>
              display(value, artifact.visualization.format, decimals)
            }
          />
        }
      />
      <Legend />
    </>
  );
  return (
    <Card className="result-card">
      <CardHeader>
        <div className="result-heading">
          <div>
            <CardDescription>QUERY RESULT</CardDescription>
            <CardTitle>{artifact.title}</CardTitle>
          </div>
          <Select value={selected} onValueChange={changeView}>
            <SelectTrigger aria-label={`Visualization for ${artifact.title}`}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {options.map((option) => (
                  <SelectItem key={option} value={option}>
                    {option === "kpi"
                      ? "KPI cards"
                      : human(option).replace(/^./, (c) => c.toUpperCase())}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
        <div className="result-meta">
          {artifact.provenance.map((source) => (
            <Badge key={source.source} variant="secondary">
              <Database data-icon="inline-start" />
              {source.source === "bigquery" ? "BigQuery" : "PostgreSQL"}
            </Badge>
          ))}
          <span>
            <Clock3 aria-hidden />
            {artifact.provenance
              .reduce((total, source) => total + source.elapsed_ms, 0)
              .toLocaleString()}{" "}
            ms
          </span>
          <span>{artifact.row_count.toLocaleString()} rows</span>
          {artifact.complete ? (
            <span className="verified">
              <CheckCheck aria-hidden />
              Complete inputs
            </span>
          ) : (
            <Badge variant="destructive">Partial result</Badge>
          )}
        </div>
      </CardHeader>
      <MotionCardContent
        key={selected}
        initial={reduced ? false : { opacity: 0.55 }}
        animate={{ opacity: 1 }}
        transition={{ duration: reduced ? 0 : 0.18 }}
      >
        {!artifact.complete && (
          <Alert variant="destructive">
            <Info />
            <AlertTitle>Partial result</AlertTitle>
            <AlertDescription>
              The source row limit was reached. Narrow the question before using
              this result as a total.
            </AlertDescription>
          </Alert>
        )}
        {selected === "kpi" && (
          <div className="result-kpis">
            {numeric.map((column) => (
              <div key={column}>
                <span>{human(column)}</span>
                <strong>
                  {artifact.rows[0]?.[column] != null &&
                  Number.isFinite(Number(artifact.rows[0][column])) ? (
                    <AnimatedNumber
                      value={Number(artifact.rows[0][column])}
                      format={(value) =>
                        display(
                          value,
                          ys.includes(column)
                            ? artifact.visualization.format
                            : "number",
                          decimals,
                        )
                      }
                    />
                  ) : (
                    "—"
                  )}
                </strong>
              </div>
            ))}
          </div>
        )}
        {selected === "table" && (
          <>
            <div
              className="result-table"
              aria-busy={loading}
              tabIndex={0}
              role="region"
              aria-label={`${artifact.title} data table`}
            >
              <Table>
                <TableCaption>
                  {artifact.title}. Page {page + 1} of{" "}
                  {Math.max(1, artifact.page_count)}.
                </TableCaption>
                <TableHeader>
                  <TableRow>
                    {artifact.columns.map((column) => (
                      <TableHead key={column.name} scope="col">
                        {human(column.name)}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tableRows.map((row, index) => (
                    <TableRow key={index}>
                      {artifact.columns.map((column) => (
                        <TableCell key={column.name}>
                          {numeric.includes(column.name)
                            ? display(
                                row[column.name],
                                ys.includes(column.name)
                                  ? artifact.visualization.format
                                  : "number",
                                decimals,
                              )
                            : String(row[column.name] ?? "—")}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            {tableError && <p role="alert">{tableError}</p>}
            <div className="table-pagination">
              <span>{tableRows.length} rows on this page</span>
              <Button
                variant="outline"
                size="sm"
                disabled={!page || loading}
                onClick={() => {
                  setPage(page - 1);
                  setLoading(true);
                }}
              >
                <ChevronLeft data-icon="inline-start" />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page + 1 >= artifact.page_count || loading}
                onClick={() => {
                  setPage(page + 1);
                  setLoading(true);
                }}
              >
                Next
                <ChevronRight data-icon="inline-end" />
              </Button>
            </div>
          </>
        )}
        {selected !== "table" && selected !== "kpi" && (
          <figure>
            <ChartContainer config={config} className="analytics-chart">
              {selected === "bar" ? (
                <BarChart
                  accessibilityLayer
                  data={data}
                  margin={{ top: 12, right: 8, bottom: 4, left: 0 }}
                >
                  {axes}
                  {ys.map((column, index) => (
                    <Bar
                      key={column}
                      dataKey={column}
                      name={human(column)}
                      fill={colors[index]}
                      radius={[5, 5, 0, 0]}
                      maxBarSize={60}
                      isAnimationActive={false}
                    />
                  ))}
                </BarChart>
              ) : selected === "line" ? (
                <LineChart accessibilityLayer data={data}>
                  {axes}
                  {ys.map((column, index) => (
                    <Line
                      key={column}
                      dataKey={column}
                      name={human(column)}
                      stroke={colors[index]}
                      strokeWidth={2.5}
                      dot={data.length < 20}
                      isAnimationActive={false}
                    />
                  ))}
                </LineChart>
              ) : selected === "area" ? (
                <AreaChart accessibilityLayer data={data}>
                  {axes}
                  {ys.map((column, index) => (
                    <Area
                      key={column}
                      dataKey={column}
                      name={human(column)}
                      stroke={colors[index]}
                      fill={colors[index]}
                      fillOpacity={0.12}
                      strokeWidth={2.5}
                      isAnimationActive={false}
                    />
                  ))}
                </AreaChart>
              ) : selected === "pie" ? (
                <PieChart accessibilityLayer>
                  <Pie
                    data={data.filter((row) => Number(row[ys[0]]) >= 0)}
                    dataKey={ys[0]}
                    nameKey={x}
                    innerRadius="55%"
                    outerRadius="85%"
                    isAnimationActive={false}
                  >
                    {data.map((_, index) => (
                      <Cell key={index} fill={colors[index % colors.length]} />
                    ))}
                  </Pie>
                  <ChartTooltip
                    content={
                      <ChartTooltipContent
                        valueFormatter={(value) =>
                          display(
                            value,
                            artifact.visualization.format,
                            decimals,
                          )
                        }
                      />
                    }
                  />
                  <Legend />
                </PieChart>
              ) : (
                <ScatterChart accessibilityLayer>
                  <CartesianGrid strokeDasharray="3 5" />
                  <XAxis
                    type="number"
                    dataKey={numeric[0]}
                    name={human(numeric[0])}
                    tickFormatter={ticks}
                  />
                  <YAxis
                    type="number"
                    dataKey={numeric[1]}
                    name={human(numeric[1])}
                    tickFormatter={ticks}
                  />
                  <ChartTooltip
                    content={
                      <ChartTooltipContent
                        valueFormatter={(value) =>
                          display(value, "number", decimals)
                        }
                      />
                    }
                  />
                  <Scatter
                    data={data}
                    fill={colors[0]}
                    isAnimationActive={false}
                  />
                </ScatterChart>
              )}
            </ChartContainer>
            <figcaption className="chart-caption">
              {artifact.visualization.title}.{" "}
              {artifact.row_count > 60
                ? `Showing the first 60 of ${artifact.row_count.toLocaleString()} result rows. `
                : ""}
              Switch to table for the underlying data.
            </figcaption>
          </figure>
        )}
        {!artifact.row_count && (
          <p className="empty-result">
            No matching rows. Try a broader date range.
          </p>
        )}
        {artifact.join_diagnostics && (
          <div className="join-note">
            <GitMerge aria-hidden />
            <div>
              <strong>
                Inferred relationship ·{" "}
                {String(artifact.join_diagnostics.cardinality)}
              </strong>
              <p>{String(artifact.join_diagnostics.relationship)}</p>
              <span>
                {String(artifact.join_diagnostics.unmatched_left)} unmatched
                warehouse rows ·{" "}
                {String(artifact.join_diagnostics.unmatched_right)} unmatched
                operations rows ·{" "}
                {Math.round(
                  Number(artifact.join_diagnostics.left_key_coverage) * 100,
                )}
                % key coverage
              </span>
            </div>
          </div>
        )}
      </MotionCardContent>
      <CardFooter className="evidence-footer">
        <details>
          <summary>
            <Braces aria-hidden />
            SQL & evidence
            <span>
              {artifact.provenance.length}{" "}
              {artifact.provenance.length === 1 ? "source" : "sources"}
            </span>
          </summary>
          <div className="evidence-content">
            {artifact.provenance.map((source) => (
              <div key={source.source}>
                <div className="sql-label">
                  <strong>
                    {source.source === "bigquery" ? "BigQuery" : "PostgreSQL"}
                  </strong>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={async () => {
                      try {
                        await navigator.clipboard.writeText(source.sql);
                        toast.success("SQL copied", {
                          id: `copy-sql:${artifact.id}`,
                        });
                      } catch {
                        toast.error(
                          "Clipboard is unavailable in this browser.",
                        );
                      }
                    }}
                  >
                    <Copy data-icon="inline-start" />
                    Copy SQL
                  </Button>
                </div>
                <pre>
                  <code>{source.sql}</code>
                </pre>
                <p>
                  {source.row_count.toLocaleString()} rows · {source.elapsed_ms}{" "}
                  ms · {new Date(source.executed_at).toLocaleString()}
                  {source.bytes_processed != null
                    ? ` · ${(source.bytes_processed / 1024 ** 2).toFixed(2)} MiB scanned`
                    : ""}
                </p>
                {source.job_id && (
                  <p className="job-id">Job: {source.job_id}</p>
                )}
              </div>
            ))}
            <div className="assumptions">
              <strong>
                <Info aria-hidden />
                Assumptions & context
              </strong>
              <ul>
                {artifact.assumptions.map((assumption, index) => (
                  <li key={index}>{assumption}</li>
                ))}
              </ul>
              {artifact.retrieval && (
                <p>Schema retrieval: {artifact.retrieval}</p>
              )}
              {artifact.ai && (
                <p>
                  AI model:{" "}
                  {artifact.ai.backend === "gemini"
                    ? artifact.ai.text_model
                    : "Local sample mode (no model calls)"}
                </p>
              )}
            </div>
          </div>
        </details>
        <span className="data-table-hint">
          <Table2 aria-hidden />
          Read-only analysis
        </span>
      </CardFooter>
    </Card>
  );
}
