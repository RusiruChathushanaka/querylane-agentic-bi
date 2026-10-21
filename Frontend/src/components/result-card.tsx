"use client";

import { PredictionEvidence } from "@/components/prediction-evidence";
import { MetricEvidence } from "@/components/metric-evidence";
import { useEffect, useState } from "react";
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
import type { Artifact } from "@/lib/types";
import { usePreferences } from "@/hooks/use-preferences";
import { AnimatedNumber } from "@/components/motion/animated-number";
import { motion } from "motion/react";
import { useAppMotion } from "@/hooks/use-app-motion";
import { SavedCsvDownload } from "@/components/charts/saved-csv-download";
import InsightfulChart from "@/components/charts/insightful-chart";
import { PinToDashboard } from "@/components/pin-to-dashboard";
import { initialChartView } from "@/lib/chart-view-state";
import { savedResult } from "@/lib/saved-result-loader";
import type { ChartCapture, ChartViewState } from "@/lib/dashboard-types";
import { formatMeasure } from "@/lib/chart-format";

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

export default function ResultCard({
  artifact,
  onExplore,
  initialState,
  onCapture,
  allowPin = true,
  showPredictionEvidence = true,
}: {
  initialState?: ChartViewState;
  onCapture?: (capture: ChartCapture) => void;
  allowPin?: boolean;
  showPredictionEvidence?: boolean;
  artifact: Artifact;
  onExplore?: (question: string) => void;
}) {
  const { preferences } = usePreferences();
  const { reduced } = useAppMotion();
  const decimals = initialState?.decimals ?? Number(preferences.decimals);
  const [captured, setCaptured] = useState<ChartCapture | null>(null);
  const [view, setView] = useState<string | null>(initialState?.view ?? null);
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
  const chartable = Boolean(x && ys.length && artifact.row_count);
  const pieable =
    chartable &&
    artifact.complete &&
    artifact.row_count <= 6 &&
    artifact.visualization.measures?.some(
      (m) => m.field === ys[0] && m.additive,
    ) &&
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

  useEffect(() => {
    if (!["table", "kpi"].includes(selected) || !artifact.page_count) return;
    let cancelled = false;
    const controller = new AbortController();
    savedResult<{ rows: Record<string, unknown>[] }>(
      `/artifacts/${artifact.id}/pages/${page}`,
      controller.signal,
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
      controller.abort();
    };
  }, [selected, artifact.id, artifact.page_count, page]);

  const tableState = JSON.stringify({
    ...(initialState ?? initialChartView(artifact, preferences, selected)),
    view: selected,
    start: null,
    end: null,
  });
  useEffect(() => {
    if (selected === "table")
      onCapture?.({ state: JSON.parse(tableState), ready: true });
  }, [selected, tableState, onCapture]);

  function valueDisplay(value: unknown, column: string) {
    const measure = artifact.visualization.measures?.find(
      (m) => m.field === column,
    );
    return measure
      ? formatMeasure(value, measure, decimals)
      : display(
          value,
          artifact.visualization.y.length === 1 && ys.includes(column)
            ? artifact.visualization.format
            : "number",
          decimals,
        );
  }

  function changeView(value: string) {
    setView(value);
    toast.success("Visualization updated", {
      id: "visualization-choice",
      description: `${value === "kpi" ? "KPI cards" : `${value[0].toUpperCase()}${value.slice(1)} view`} · underlying data and evidence are unchanged.`,
      duration: 2600,
    });
    if (value === "table" && artifact.page_count) setLoading(true);
  }

  return (
    <Card className="result-card">
      <CardHeader>
        <div className="result-heading">
          <div>
            <CardDescription>QUERY RESULT</CardDescription>
            <CardTitle>{artifact.title}</CardTitle>
          </div>
          {allowPin && (
            <PinToDashboard
              artifact={artifact}
              capture={
                selected === "table"
                  ? { state: JSON.parse(tableState), ready: true }
                  : captured?.state.view === selected
                    ? captured
                    : {
                        state:
                          initialState ??
                          initialChartView(artifact, preferences, selected),
                        ready: false,
                      }
              }
            />
          )}
          {selected === "table" && <SavedCsvDownload artifact={artifact} />}
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
        {showPredictionEvidence && artifact.prediction && <PredictionEvidence prediction={artifact.prediction} artifactId={artifact.id} reportId={artifact.report_id} reportVersion={artifact.report_version} />}
        <MetricEvidence metrics={artifact.metric_snapshots ?? []} />
        {artifact.metric_resolution === "ad_hoc" && <p className="text-xs text-muted-foreground">Ad hoc analysis — no published metric definition was captured.</p>}
        {artifact.forecast_plan_id && <a className="underline" href={`/forecast-plans/${artifact.forecast_plan_id}?version=${artifact.forecast_plan_version}`}>Forecast plan version {artifact.forecast_plan_version}</a>}
        <div className="result-meta">
          {artifact.provenance.map((source, index) => (
            <Badge key={`${source.source}-${index}`} variant="secondary">
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
            {numeric
              .filter((column) =>
                (
                  initialState?.visible_measures ??
                  (captured?.state.view === "kpi"
                    ? captured.state.visible_measures
                    : ys)
                ).includes(column),
              )
              .map((column) => (
                <div key={column}>
                  <span>{human(column)}</span>
                  <strong>
                    {tableRows[0]?.[column] != null &&
                    Number.isFinite(Number(tableRows[0][column])) ? (
                      <AnimatedNumber
                        value={Number(tableRows[0][column])}
                        format={(value) => valueDisplay(value, column)}
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
            >
              <Table aria-label={`${artifact.title} data table`}>
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
                            ? valueDisplay(row[column.name], column.name)
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
        {selected !== "table" && (
          <InsightfulChart
            artifact={artifact}
            view={selected}
            onExplore={onExplore}
            initialState={initialState}
            onCapture={onCapture ?? setCaptured}
          />
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
            {artifact.provenance.map((source, index) => (
              <div key={`${source.source}-${index}`}>
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
