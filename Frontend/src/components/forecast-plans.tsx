"use client";
import { useReadResource } from "@/hooks/use-read-resource";
import { ResourceFeedback } from "./resource-feedback";

import { AppSelect, AppSelectItem } from "@/components/ui/app-select";
import Link from "@/components/ui/app-link";
import { Skeleton } from "./ui/skeleton";
import { PlanningSkills } from "./planning-skills";
import { usePreferences } from "@/hooks/use-preferences";
import { usePendingRequest } from "@/hooks/use-pending-request";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { toast } from "sonner";
import { api, backendUrl } from "@/lib/api";
import type {
  ForecastDocument,
  ForecastPlan,
  ForecastRevision,
  HierarchyNode,
  JobRun,
  Metric,
} from "@/lib/planning-types";
import { DashboardHeader } from "./dashboard-shared";
import { JobControls, SavedArtifactPreview } from "./dashboard-builder";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

const money = (v: number | string) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(Number(v));
const stateLabel = (doc: ForecastDocument, node: HierarchyNode) =>
  doc.kind === "adjusted_plan"
    ? "User planning assumption"
    : ["store", "product"].includes(node.level)
      ? "Allocated estimate — not independently modeled"
      : node.level === "company"
        ? "Modeled company forecast"
        : "Reconciled forecast";

export function ForecastPlans({
  id,
  initialVersion,
}: {
  id?: string;
  initialVersion?: number;
}) {
  const router = useRouter();
  const pending = usePendingRequest();
  const [skillIds, setSkillIds] = useState<string[]>([]);
  const { preferences } = usePreferences();
  const textModel =
    preferences.textModel === "default" ? null : preferences.textModel;
  const [plans, setPlans] = useState<ForecastPlan[]>([]);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [root, setRoot] = useState<ForecastPlan | null>(null);
  const [revision, setRevision] = useState<ForecastRevision | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<number | null>(
    initialVersion ?? null,
  );
  const [selectedNode, setSelectedNode] = useState("company");
  const [chart, setChart] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [deleted, setDeleted] = useState(false);
  const [status, setStatus] = useState("all");
  const [objective, setObjective] = useState("");
  const [metricId, setMetricId] = useState("");
  const [horizon, setHorizon] = useState(3);
  const [hierarchy, setHierarchy] = useState("both");
  const [focus, setFocus] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const [adjustValue, setAdjustValue] = useState("");
  const [operation, setOperation] = useState("percent");
  const [reportStyle, setReportStyle] = useState("business");
  const [reason, setReason] = useState("");
  const [compareVersion, setCompareVersion] = useState("");
  const [comparison, setComparison] = useState<ForecastDocument | null>(null);
  const previousStatus = useRef<string | null>(null);
  const reportChats = useRef<Record<string, string>>({});
  const resource = useReadResource(`forecast-plans:${id ?? "library"}:${deleted}`, async (signal) => {
    if (id) return { root: await api<ForecastPlan>(`/forecast-plans/${id}`, { signal }), plans: null };
    return { root: null, plans: (await api<{ plans: ForecastPlan[] }>(`/forecast-plans?deleted=${deleted}`, { signal })).plans };
  }, (v) => {
    if (v.root) {
      setRoot(v.root);
      const current = v.root.run?.status ?? v.root.status;
      if (previousStatus.current && previousStatus.current !== "complete" && current === "complete") toast.success("Forecast plan ready");
      previousStatus.current = current;
    } else if (v.plans) setPlans(v.plans);
  }, 7000);
  const load = async () => (await resource.refresh())?.root;
  const loading = !resource.loaded && resource.pending;
  const metricResource = useReadResource(`plan-metrics:${!!id}`, async (signal) => id ? { metrics: [] as Metric[] } : api<{ metrics: Metric[] }>("/metrics", { signal }), (v) => setMetrics(v.metrics.filter((m) => !m.archived && m.published_version && m.published_definition?.formula.measure === "revenue" && m.published_definition.time_basis === "order_date")));
  const revisionNumber = selectedVersion ?? root?.latest_version;
  const revisionResource = useReadResource(`plan-revision:${id}:${revisionNumber}`, async (signal) => id && revisionNumber ? api<ForecastRevision>(`/forecast-plans/${id}/revisions/${revisionNumber}`, { signal }) : null, (v) => {
    if (v) { setRevision(v); setChart(v.document.company_artifact_id ?? null); setSelectedNode("company"); }
  });
  async function create() {
    const metric = metrics.find((m) => m.id === metricId);
    if (!metric) return;
    setBusy(true);
    setError("");
    try {
      const run = await api<JobRun>("/forecast-plans", {
        method: "POST",
        body: JSON.stringify({
          objective,
          model: textModel,
          skill_ids: skillIds,
          metric: { id: metric.id, version: metric.published_version },
          horizon,
          hierarchy,
          focus,
          start: start || null,
          end: end || null,
          request_id: pending.id("create-plan", {
            objective,
            model: textModel,
            skillIds,
            metricId,
            horizon,
            hierarchy,
            focus,
            start,
            end,
          }),
        }),
      });
      pending.complete("create-plan", {
        objective,
        model: textModel,
        skillIds,
        metricId,
        horizon,
        hierarchy,
        focus,
        start,
        end,
      });
      router.push(`/forecast-plans/${run.root_id}`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function metadata(plan: ForecastPlan, action: string, name?: string) {
    if (
      action === "delete" &&
      !window.confirm(
        "Remove this public plan from the library? It remains recoverable for 30 days; pinned charts remain available.",
      )
    )
      return;
    setBusy(true);
    setError("");
    try {
      const result = await api<ForecastPlan>(
        `/forecast-plans/${plan.id}${action === "restore" ? "/restore" : ""}`,
        {
          method:
            action === "restore"
              ? "POST"
              : action === "delete"
                ? "DELETE"
                : "PATCH",
          body: JSON.stringify({
            expected_revision: plan.revision,
            request_id: crypto.randomUUID(),
            name,
          }),
        },
      );
      await load();
      toast.success(
        action === "delete"
          ? "Plan deleted"
          : action === "restore"
            ? "Plan restored"
            : "Plan renamed",
        action === "delete"
          ? {
              action: {
                label: "Undo",
                onClick: () => {
                  void metadata(result, "restore");
                },
              },
            }
          : undefined,
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function adjustment() {
    if (!root || !revision) return;
    setBusy(true);
    setError("");
    try {
      const result = await api<{ version: number }>(
        `/forecast-plans/${root.id}/adjustments`,
        {
          method: "POST",
          body: JSON.stringify({
            expected_revision: root.revision,
            base_version: revision.version,
            node_id: selectedNode,
            operation,
            value: Number(adjustValue),
            reason,
            request_id: pending.id("adjust", {
              root: root.id,
              revision: root.revision,
              base: revision.version,
              selectedNode,
              operation,
              adjustValue,
              reason,
            }),
          }),
        },
      );
      pending.complete("adjust", {
        root: root.id,
        revision: root.revision,
        base: revision.version,
        selectedNode,
        operation,
        adjustValue,
        reason,
      });
      await load();
      setSelectedVersion(result.version);
      toast.success("Planning adjustment saved as a new version");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function showChart() {
    if (!id || !revision) return;
    setBusy(true);
    setError("");
    try {
      const artifact = await api<{ id: string }>(
        `/forecast-plans/${id}/revisions/${revision.version}/artifacts/${encodeURIComponent(selectedNode)}`,
        { method: "POST" },
      );
      setChart(artifact.id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function download(format: string) {
    if (!id || !revision) return;
    setBusy(true);
    setError("");
    try {
      const response = await fetch(
        `${await backendUrl()}/api/v1/forecast-plans/${id}/revisions/${revision.version}/downloads/${format}`,
        { signal: AbortSignal.timeout(90000) },
      );
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body?.error?.message ?? "Download failed");
      }
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = `querylane-plan-v${revision.version}.${format === "data" ? "zip" : format}`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      toast.success("Saved plan downloaded");
    } catch (e) {
      setError((e as Error).message);
      toast.error("Plan download failed", {
        description: (e as Error).message,
      });
    } finally {
      setBusy(false);
    }
  }
  async function narrative() {
    if (!id || !revision) return;
    setBusy(true);
    setError("");
    try {
      await api(
        `/forecast-plans/${id}/revisions/${revision.version}/artifacts/company`,
        { method: "POST" },
      );
      const scope = { id, version: revision.version, reportStyle };
      const stored = reportChats.current[`${id}:${revision.version}`];
      const chat = stored
        ? { id: stored }
        : await api<{ id: string }>("/conversations", {
            method: "POST",
            body: JSON.stringify({
              title: `Forecast plan: ${root?.name ?? "Saved evidence"}`.slice(
                0,
                100,
              ),
              source: "all",
            }),
          });
      reportChats.current[`${id}:${revision.version}`] = chat.id;
      const report = await api<{ report_id: string }>(
        `/conversations/${chat.id}/reports`,
        {
          method: "POST",
          body: JSON.stringify({
            question: `Explain the saved company forecast and hierarchy methodology for ${root?.name}, version ${revision.version}. Distinguish predictions, allocations and user planning adjustments. Use only the saved evidence.`,
            style: reportStyle,
            model: textModel,
            forecast_plan_id: id,
            forecast_plan_version: revision.version,
            idempotency_key: pending.id("plan-narrative", scope),
          }),
        },
      );
      pending.complete("plan-narrative", scope);
      router.push(`/reports/${report.report_id}`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function recompute() {
    if (
      !root ||
      !revision ||
      !window.confirm(
        "Recompute using new source reads and the current forecasting policy? This consumes another advanced-analysis allowance.",
      )
    )
      return;
    const d = revision.document;
    setBusy(true);
    setError("");
    try {
      await api(`/forecast-plans/${root.id}/revisions`, {
        method: "POST",
        body: JSON.stringify({
          objective: root.name,
          model: textModel,
          metric: {
            id: d.metric_snapshot.id,
            version: d.metric_snapshot.version,
          },
          horizon: d.horizon,
          expected_revision: root.revision,
          request_id: crypto.randomUUID(),
        }),
      });
      await load();
      toast.success("New forecast computation queued");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const doc = revision?.document;
  const node = doc?.history.nodes[selectedNode];
  function pickNode(key: string) {
    setSelectedNode(key);
    setChart(null);
  }
  function tree(level: "region" | "category") {
    if (!doc) return null;
    const parents = Object.values(doc.history.nodes).filter(
      (n) => n.level === level,
    );
    return (
      <div className="bi-tree">
        <ul>
          <li>
            <button
              aria-pressed={selectedNode === "company"}
              onClick={() => pickNode("company")}
            >
              Company
            </button>
          </li>
          {parents.map((parent) => (
            <li key={parent.id}>
              <details open>
                <summary>{parent.name}</summary>
                <button
                  aria-pressed={selectedNode === parent.id}
                  onClick={() => pickNode(parent.id)}
                >
                  View {parent.name} total
                </button>
                <ul>
                  {Object.values(doc.history.nodes)
                    .filter((n) => n.parent === parent.id)
                    .map((child) => (
                      <li key={child.id}>
                        <button
                          aria-pressed={selectedNode === child.id}
                          onClick={() => pickNode(child.id)}
                        >
                          {child.name}
                        </button>
                      </li>
                    ))}
                </ul>
              </details>
            </li>
          ))}
        </ul>
      </div>
    );
  }
  const shown = plans.filter(
    (p) =>
      p.name.toLowerCase().includes(query.toLowerCase()) &&
      (status === "all" || (p.run?.status ?? p.status) === status),
  );
  return (
    <>
      <a className="skip-link" href="#plans-main">
        Skip to forecast plans
      </a>
      <DashboardHeader />
      <main className="bi-main" id="plans-main" tabIndex={-1}>
        <ResourceFeedback resource={resource} label="Loading forecast plans" />
        <ResourceFeedback resource={metricResource} label="Loading published revenue definitions" />
        {id && <ResourceFeedback resource={revisionResource} label="Loading saved plan version" />}
        <header className="bi-hero">
          <div>
            <span className="bi-kicker">
              Coherent predictions. Explicit planning assumptions.
            </span>
            <h1>{root?.name ?? "Forecast plans."}</h1>
            <p>
              Connect company revenue to regions, stores, categories and
              products. Explore validated methods and clearly labeled
              allocations, then save your own planning assumptions.
            </p>
            <Badge variant="secondary">Public synthetic retail planning</Badge>
          </div>
          {id && (
            <Button asChild variant="outline">
              <Link href="/forecast-plans">All forecast plans</Link>
            </Button>
          )}
        </header>
        {error && (
          <div className="bi-error" role="alert">
            {error}
            <div>
              <Button
                variant="outline"
                onClick={() => void load().catch((e) => setError(e.message))}
              >
                Reload latest
              </Button>
            </div>
          </div>
        )}
        {!id && (
          <>
            <form
              className="bi-editor"
              onSubmit={(e) => {
                e.preventDefault();
                void create();
              }}
            >
              <h2>Create a forecast plan</h2>
              <div className="bi-fields">
                <label className="bi-field bi-wide">
                  <span>Business objective</span>
                  <textarea
                    required
                    minLength={3}
                    value={objective}
                    onChange={(e) => setObjective(e.target.value)}
                    placeholder="Plan next quarter’s revenue across our regions and product categories."
                  />
                </label>
                <label className="bi-field">
                  <span>Published revenue definition</span>
                  <AppSelect
                    required
                    value={metricId}
                    onValueChange={(selectedValue) =>
                      setMetricId(selectedValue)
                    }
                  >
                    <AppSelectItem value="">Choose a metric</AppSelectItem>
                    {metrics.map((m) => (
                      <AppSelectItem key={m.id} value={String(m.id)}>
                        {m.name} · v{m.published_version}
                      </AppSelectItem>
                    ))}
                  </AppSelect>
                </label>
                <label className="bi-field">
                  <span>Future months</span>
                  <AppSelect
                    value={horizon}
                    onValueChange={(selectedValue) =>
                      setHorizon(Number(selectedValue))
                    }
                  >
                    {[1, 2, 3, 4, 5, 6].map((v) => (
                      <AppSelectItem key={v} value={String(v)}>
                        {v} month{v > 1 ? "s" : ""}
                      </AppSelectItem>
                    ))}
                  </AppSelect>
                </label>
                <label className="bi-field">
                  <span>Planning view</span>
                  <AppSelect
                    value={hierarchy}
                    onValueChange={(selectedValue) =>
                      setHierarchy(selectedValue)
                    }
                  >
                    <AppSelectItem value="both">
                      Geography + products
                    </AppSelectItem>
                    <AppSelectItem value="geography">
                      Focus on geography
                    </AppSelectItem>
                    <AppSelectItem value="products">
                      Focus on products
                    </AppSelectItem>
                  </AppSelect>
                </label>
                <label className="bi-field">
                  <span>Priority region or category (optional)</span>
                  <input
                    value={focus}
                    maxLength={100}
                    onChange={(e) => setFocus(e.target.value)}
                  />
                </label>
                <label className="bi-field">
                  <span>History start (optional, month start)</span>
                  <input
                    type="date"
                    value={start}
                    onChange={(e) => setStart(e.target.value)}
                  />
                </label>
                <label className="bi-field">
                  <span>History end (optional, month end)</span>
                  <input
                    type="date"
                    value={end}
                    onChange={(e) => setEnd(e.target.value)}
                  />
                </label>
              </div>
              <p className="bi-note">
                Defaults to all complete source history. Forecasts begin after
                the saved cutoff. Both hierarchies share the company total; your
                selected view controls initial exploration. Uses the shared
                advanced-analysis allowance.
              </p>
              {metricResource.loaded && !metrics.length && (
                <p className="bi-note">
                  Publish an order-date merchandise revenue metric in the{" "}
                  <Link href="/metrics" className="underline">
                    Metrics catalog
                  </Link>{" "}
                  first.
                </p>
              )}
              <PlanningSkills
                source="all"
                selected={skillIds}
                onChange={setSkillIds}
              />
              <Button disabled={busy || !metricId} type="submit">
                Create forecast plan
              </Button>
            </form>
            <div className="bi-toolbar">
              <label className="bi-field">
                <span>Search plans</span>
                <input
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </label>
              <label className="bi-field">
                <span>Library</span>
                <AppSelect
                  value={deleted ? "deleted" : "active"}
                  onValueChange={(selectedValue) =>
                    setDeleted(selectedValue === "deleted")
                  }
                >
                  <AppSelectItem value="active">Active plans</AppSelectItem>
                  <AppSelectItem value="deleted">
                    Recently deleted
                  </AppSelectItem>
                </AppSelect>
              </label>
              <label className="bi-field">
                <span>Status</span>
                <AppSelect
                  value={status}
                  onValueChange={(selectedValue) => setStatus(selectedValue)}
                >
                  {[
                    "all",
                    "complete",
                    "queued",
                    "running",
                    "failed",
                    "cancelled",
                    "waiting_input",
                  ].map((v) => (
                    <AppSelectItem value={String(v)} key={v}>
                      {v}
                    </AppSelectItem>
                  ))}
                </AppSelect>
              </label>
            </div>
            {loading ? (
              <Skeleton aria-hidden="true" className="h-40 w-full" />
            ) : !resource.loaded ? null : !shown.length ? (
              <div className="bi-empty">
                No matching plans. Start with a business objective and a
                published revenue definition.
              </div>
            ) : (
              <div className="bi-grid">
                {shown.map((p) => (
                  <article className="bi-card" key={p.id}>
                    <Badge variant="outline">{p.run?.status ?? p.status}</Badge>
                    <h2>
                      <Link href={`/forecast-plans/${p.id}`}>{p.name}</Link>
                    </h2>
                    <p>{p.versions.length} saved versions · public</p>
                    <div className="bi-card-actions">
                      <Button asChild size="sm" variant="outline">
                        <Link href={`/forecast-plans/${p.id}`}>Open plan</Link>
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        disabled={busy}
                        onClick={() =>
                          void metadata(p, p.deleted ? "restore" : "delete")
                        }
                      >
                        {p.deleted ? "Restore" : "Delete"}
                      </Button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </>
        )}
        {root?.run && (
          <JobControls
            run={root.run}
            onChange={() => void load().catch((e) => setError(e.message))}
          />
        )}
        {root && (
          <div className="bi-toolbar">
            <label className="bi-field">
              <span>Immutable version</span>
              <AppSelect
                value={selectedVersion ?? root.latest_version ?? ""}
                onValueChange={(selectedValue) =>
                  setSelectedVersion(Number(selectedValue))
                }
              >
                {root.versions.map((v) => (
                  <AppSelectItem key={v} value={String(v)}>
                    Version {v}
                  </AppSelectItem>
                ))}
              </AppSelect>
            </label>
            <Button
              disabled={
                busy ||
                (!!root.run &&
                  !["complete", "failed", "cancelled"].includes(
                    root.run.status,
                  ))
              }
              variant="outline"
              onClick={() => {
                const name = window.prompt("New public plan name", root.name);
                if (name?.trim()) void metadata(root, "rename", name);
              }}
            >
              Rename
            </Button>
            <Button
              disabled={busy}
              variant="outline"
              onClick={() =>
                void metadata(root, root.deleted ? "restore" : "delete")
              }
            >
              {root.deleted ? "Restore" : "Delete"}
            </Button>
            <Button
              disabled={
                busy ||
                (!!root.run &&
                  !["complete", "failed", "cancelled"].includes(
                    root.run.status,
                  )) ||
                !doc ||
                root.deleted
              }
              variant="outline"
              onClick={() => void recompute()}
            >
              Recompute with source data
            </Button>
            {doc &&
              ["pdf", "data", "json"].map((format) => (
                <Button
                  key={format}
                  disabled={busy}
                  variant="outline"
                  onClick={() => void download(format)}
                >
                  {format === "data"
                    ? "Download CSV ZIP"
                    : `Download ${format.toUpperCase()}`}
                </Button>
              ))}
          </div>
        )}
        {doc && node && (
          <>
            <div className="bi-card">
              <h2>
                {doc.kind === "adjusted_plan"
                  ? "Planning assumptions"
                  : "Statistical forecast"}{" "}
                · version {doc.version}
              </h2>
              <p>
                Observed through {doc.cutoff}. {doc.horizon} future months.
                Recipe: {doc.selection.selected.replaceAll("_", " ")}.
              </p>
              <p className="bi-note">
                Metric: {doc.metric_snapshot.definition.name} · v
                {doc.metric_snapshot.version}.{" "}
                {doc.metric_snapshot.definition.description}
              </p>
              {doc.limitations.map((v, i) => (
                <p key={i} className="bi-note">
                  {v}
                </p>
              ))}
            </div>
            <Tabs
              key={`${doc.id}:${doc.version}`}
              defaultValue={
                doc.preferred_view === "products" ? "products" : "geography"
              }
              className="mt-5"
              onValueChange={() => {
                setSelectedNode("company");
                setChart(doc.company_artifact_id ?? null);
              }}
            >
              <TabsList aria-label="Forecast hierarchy">
                <TabsTrigger value="geography">Geography</TabsTrigger>
                <TabsTrigger value="products">Products</TabsTrigger>
              </TabsList>
              {(["geography", "products"] as const).map((tab) => (
                <TabsContent key={tab} value={tab}>
                  <div className="bi-layout">
                    <nav aria-label={`${tab} hierarchy`}>
                      {tree(tab === "geography" ? "region" : "category")}
                    </nav>
                    <section>
                      <h2 className="text-xl font-semibold">{node.name}</h2>
                      <p className="bi-note">{stateLabel(doc, node)}</p>
                      <Button
                        disabled={busy}
                        variant="outline"
                        onClick={() => void showChart()}
                      >
                        Show saved chart & pin controls
                      </Button>
                      {chart && (
                        <div className="mt-4">
                          <SavedArtifactPreview id={chart} allowPin />
                        </div>
                      )}
                      <div
                        className="bi-table-wrap"
                        role="region"
                        tabIndex={0}
                        aria-label={`${node.name} monthly data`}
                      >
                        <table className="bi-table">
                          <caption>
                            {node.name}: saved monthly revenue, USD. Future
                            values are{" "}
                            {doc.kind === "adjusted_plan"
                              ? "planning assumptions"
                              : "predictions / allocated estimates"}
                            .
                          </caption>
                          <thead>
                            <tr>
                              <th scope="col">Month</th>
                              <th scope="col">Observed revenue</th>
                              <th scope="col">Future value</th>
                              {doc.statistical_predictions && (
                                <th scope="col">
                                  Original statistical baseline
                                </th>
                              )}
                            </tr>
                          </thead>
                          <tbody>
                            {doc.history.months.map((month, i) => (
                              <tr key={month}>
                                <th scope="row">{month}</th>
                                <td>{money(node.history[i])}</td>
                                <td>—</td>
                                {doc.statistical_predictions && <td>—</td>}
                              </tr>
                            ))}
                            {doc.future_months.map((month, i) => (
                              <tr key={month}>
                                <th scope="row">{month}</th>
                                <td>—</td>
                                <td>{money(doc.predictions[node.id][i])}</td>
                                {doc.statistical_predictions && (
                                  <td>
                                    {money(
                                      doc.statistical_predictions[node.id][i],
                                    )}
                                  </td>
                                )}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </section>
                  </div>
                </TabsContent>
              ))}
            </Tabs>
            <section className="bi-editor">
              <h2>Save a planning adjustment</h2>
              <p className="bi-note">
                Change {node.name}. “Set” applies the entered USD amount to each
                future month. Percent applies to each month’s saved value. This
                creates a new version and proportionally reallocates the other
                hierarchy to the new company total; it is not a learned
                scenario.
              </p>
              <div className="bi-fields">
                <label className="bi-field">
                  <span>Adjustment</span>
                  <AppSelect
                    value={operation}
                    onValueChange={(selectedValue) =>
                      setOperation(selectedValue)
                    }
                  >
                    <AppSelectItem value="percent">
                      Percentage change
                    </AppSelectItem>
                    <AppSelectItem value="set">
                      Set USD per future month
                    </AppSelectItem>
                  </AppSelect>
                </label>
                <label className="bi-field">
                  <span>
                    {operation === "percent"
                      ? "Percentage, minimum −100"
                      : "USD per month, minimum 0"}
                  </span>
                  <input
                    type="number"
                    min={operation === "percent" ? -100 : 0}
                    step="0.01"
                    value={adjustValue}
                    onChange={(e) => setAdjustValue(e.target.value)}
                  />
                </label>
                <label className="bi-field bi-wide">
                  <span>Business assumption / reason</span>
                  <textarea
                    value={reason}
                    maxLength={1000}
                    onChange={(e) => setReason(e.target.value)}
                  />
                </label>
              </div>
              <Button
                disabled={
                  busy ||
                  !adjustValue.trim() ||
                  reason.trim().length < 3 ||
                  root?.deleted
                }
                onClick={() => void adjustment()}
              >
                Save adjustment as new version
              </Button>
              {doc.adjustments.map((a, i) => (
                <p key={i} className="bi-note">
                  {a.node_id}: {a.operation} {a.value}. {a.reason}
                </p>
              ))}
            </section>
            <section className="bi-editor">
              <h2>Create an Advanced Analysis report</h2>
              <p className="bi-note">
                Write a narrative from this saved version, with no new source
                queries or forecast inference. Report writing uses the shared
                advanced-analysis allowance.
              </p>
              <div className="bi-toolbar">
                <label className="bi-field">
                  <span>Report style</span>
                  <AppSelect
                    value={reportStyle}
                    onValueChange={(selectedValue) =>
                      setReportStyle(selectedValue)
                    }
                  >
                    <AppSelectItem value="business">Business</AppSelectItem>
                    <AppSelectItem value="technical">Technical</AppSelectItem>
                  </AppSelect>
                </label>
                <Button
                  disabled={busy || root?.deleted}
                  onClick={() => void narrative()}
                >
                  Create report from saved plan
                </Button>
              </div>
            </section>
            <section className="bi-editor">
              <h2>Compare saved versions</h2>
              <label className="bi-field">
                <span>Comparison version</span>
                <AppSelect
                  value={compareVersion}
                  onValueChange={(selectedValue) => {
                    setCompareVersion(selectedValue);
                    if (selectedValue)
                      void api<ForecastRevision>(
                        `/forecast-plans/${id}/revisions/${selectedValue}`,
                      )
                        .then((v) => setComparison(v.document))
                        .catch((e) => setError(e.message));
                    else setComparison(null);
                  }}
                >
                  <AppSelectItem value="">Choose version</AppSelectItem>
                  {root?.versions
                    .filter((v) => v !== doc.version)
                    .map((v) => (
                      <AppSelectItem key={v} value={String(v)}>
                        Version {v}
                      </AppSelectItem>
                    ))}
                </AppSelect>
              </label>
              {comparison && (
                <div
                  className="bi-table-wrap"
                  role="region"
                  tabIndex={0}
                  aria-label="Company version comparison"
                >
                  <table className="bi-table">
                    <caption>
                      Company values; comparisons join exact future months.
                    </caption>
                    <thead>
                      <tr>
                        <th scope="col">Month</th>
                        <th scope="col">Current version</th>
                        <th scope="col">Compared version</th>
                      </tr>
                    </thead>
                    <tbody>
                      {doc.future_months.map((month, i) => {
                        const other = comparison.future_months.indexOf(month);
                        return (
                          <tr key={month}>
                            <th scope="row">{month}</th>
                            <td>{money(doc.predictions.company[i])}</td>
                            <td>
                              {other < 0
                                ? "Not available"
                                : money(comparison.predictions.company[other])}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
            <details className="bi-editor">
              <summary>
                Forecast methods, chronological validation and evidence
              </summary>
              <p className="bi-note">
                Equal weighting across company, region, store, category and
                product errors. All scales and allocation weights use training
                data only. An adaptive recipe needs ≥5% improvement, two fold
                wins and no level degradation above 10%.
              </p>
              <pre
                className="bi-code"
                tabIndex={0}
                role="region"
                aria-label="Forecast methods and reproducibility details"
              >
                {JSON.stringify(
                  {
                    selection: doc.selection,
                    methods: doc.methods,
                    input_hash: doc.history.input_hash,
                    metric: doc.metric_snapshot,
                  },
                  null,
                  2,
                )}
              </pre>
            </details>
          </>
        )}
      </main>
    </>
  );
}
