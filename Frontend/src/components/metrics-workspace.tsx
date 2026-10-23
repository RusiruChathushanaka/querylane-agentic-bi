"use client";
import { useReadResource } from "@/hooks/use-read-resource";
import { ResourceFeedback } from "./resource-feedback";

import { AppSelect, AppSelectItem } from "@/components/ui/app-select";
import Link from "@/components/ui/app-link";
import { Skeleton } from "./ui/skeleton";
import { usePendingRequest } from "@/hooks/use-pending-request";
import { useUnsavedNavigation } from "@/hooks/use-unsaved-navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { Metric, MetricDefinition, MetricRef } from "@/lib/planning-types";
import { DashboardHeader } from "./dashboard-shared";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";

const dimensions: MetricDefinition["dimensions"] = [
  "region",
  "store",
  "category",
  "product",
  "channel",
];
const bindings = [
  "revenue",
  "gross_sales",
  "discounts",
  "orders",
  "units",
  "customers",
  "cost",
  "line_revenue",
  "refunds",
  "returned_cost",
];
const initial: MetricDefinition = {
  name: "",
  description: "",
  aliases: [],
  formula: { operation: "sum", measure: "revenue", left: null, right: null },
  time_basis: "order_date",
  unit: "currency",
  dimensions,
  limitations: "",
  examples: [],
};
const status = (m: Metric) =>
  m.archived
    ? "Archived"
    : m.published_version
      ? "Published shared definition"
      : "Draft";

export function MetricsWorkspace({ id }: { id?: string }) {
  const pending = usePendingRequest();
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [selected, setSelected] = useState<Metric | null>(null);
  const [draft, setDraft] = useState<MetricDefinition | null>(null);
  const [editorKey, setEditorKey] = useState(0);
  const [dirty, setDirty] = useState(false);
  useUnsavedNavigation(dirty);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("active");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const [validation, setValidation] = useState("");
  const [historical, setHistorical] = useState("");
  const [start, setStart] = useState("2023-01-01");
  const [end, setEnd] = useState("2026-09-30");
  const [preview, setPreview] = useState("");
  const resource = useReadResource(`metrics:${id ?? "library"}`, (signal) => api<{ metrics: Metric[] }>("/metrics", { signal }), (v) => {
    setMetrics(v.metrics);
    if (id && !dirty && !draft) {
      const metric = v.metrics.find((m) => m.id === id);
      if (metric) { setSelected(metric); setDraft(structuredClone(metric.draft)); }
    }
  });
  const load = async () => (await resource.refresh())?.metrics ?? metrics;
  const loading = !resource.loaded && resource.pending;
  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => {
      if (dirty) e.preventDefault();
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);
  const canDiscard = () =>
    !dirty || window.confirm("Discard unsaved metric edits?");
  function edit(m: Metric | null, duplicate = false) {
    if (!canDiscard()) return;
    setEditorKey((v) => v + 1);
    setSelected(duplicate ? null : m);
    setDraft(
      m
        ? {
            ...structuredClone(m.draft),
            name: duplicate ? `${m.name} copy` : m.draft.name,
          }
        : structuredClone(initial),
    );
    setDirty(false);
    setError("");
    setValidation("");
    setHistorical("");
  }
  function update(patch: Partial<MetricDefinition>) {
    setDraft((d) => (d ? { ...d, ...patch } : d));
    setDirty(true);
    setValidation("");
  }
  async function save() {
    if (!draft) return;
    setBusy(true);
    setError("");
    try {
      const m = await api<Metric>(
        selected ? `/metrics/${selected.id}` : "/metrics",
        {
          method: selected ? "PATCH" : "POST",
          body: JSON.stringify({
            definition: draft,
            expected_revision: selected?.revision,
            request_id: pending.id("save-metric", {
              id: selected?.id,
              revision: selected?.revision,
              draft,
            }),
          }),
        },
      );
      pending.complete("save-metric", {
        id: selected?.id,
        revision: selected?.revision,
        draft,
      });
      setSelected(m);
      setDraft(structuredClone(m.draft));
      setDirty(false);
      await load();
      toast.success("Metric draft saved");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function action(m: Metric, name: string) {
    if (name === "publish" && dirty) {
      setError("Save the current draft before publishing.");
      return;
    }
    if (
      name === "publish" &&
      !window.confirm(
        "Publish this shared definition? New analyses may use it. Existing answers retain their saved versions.",
      )
    )
      return;
    setBusy(true);
    setError("");
    try {
      const result = await api<Metric>(`/metrics/${m.id}/${name}`, {
        method: "POST",
        body: JSON.stringify({
          expected_revision: m.revision,
          request_id: pending.id("metric-action", {
            id: m.id,
            revision: m.revision,
            name,
          }),
        }),
      });
      pending.complete("metric-action", {
        id: m.id,
        revision: m.revision,
        name,
      });
      if (selected?.id === m.id) setSelected(result);
      await load();
      toast.success(
        name === "publish"
          ? `Published version ${result.published_version}`
          : name === "archive"
            ? "Metric archived"
            : "Metric restored",
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function chooseMeasure(measure: string) {
    if (!draft) return;
    update({
      formula: {
        operation:
          measure === "orders"
            ? "count"
            : measure === "customers"
              ? "distinct_count"
              : "sum",
        measure,
        left: null,
        right: null,
      },
      unit: ["orders", "units", "customers"].includes(measure)
        ? "count"
        : "currency",
      time_basis: ["refunds", "returned_cost"].includes(measure)
        ? "refund_date"
        : "order_date",
      dimensions: ["orders", "customers"].includes(measure)
        ? ["region", "store", "channel"]
        : dimensions,
    });
  }
  async function validate() {
    if (!draft || !selected) return;
    setBusy(true);
    setError("");
    try {
      setValidation(
        JSON.stringify(
          await api(`/metrics/${selected.id}/validate`, {
            method: "POST",
            body: JSON.stringify({
              definition: draft,
              expected_revision: selected.revision,
              request_id: crypto.randomUUID(),
            }),
          }),
          null,
          2,
        ),
      );
      toast.success("Structural validation passed", {
        description:
          "This does not certify business meaning or numerical accuracy.",
      });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function test() {
    if (!selected?.published_version) return;
    setBusy(true);
    setError("");
    try {
      setPreview(
        JSON.stringify(
          await api(`/metrics/${selected.id}/test`, {
            method: "POST",
            body: JSON.stringify({
              start,
              end,
              version: selected.published_version,
              grain: "month",
              request_id: pending.id("test-metric", {
                id: selected.id,
                version: selected.published_version,
                start,
                end,
              }),
            }),
          }),
          null,
          2,
        ),
      );
      pending.complete("test-metric", {
        id: selected.id,
        version: selected.published_version,
        start,
        end,
      });
      toast.success("Saved metric preview ready");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const shown = metrics.filter(
    (m) =>
      (filter === "archived" ? m.archived : !m.archived) &&
      `${m.name} ${m.draft.description} ${m.draft.aliases.join(" ")} BigQuery`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  const refSelect = (side: "left" | "right") => (
    <label className="bi-field">
      <span>
        {side === "left"
          ? "Left metric / numerator"
          : "Right metric / denominator"}
      </span>
      <AppSelect
        value={draft?.formula[side]?.id ?? ""}
        onValueChange={(selectedValue) => {
          const m = metrics.find((v) => v.id === selectedValue);
          if (draft)
            update({
              formula: {
                ...draft.formula,
                [side]: m
                  ? ({
                      id: m.id,
                      version: m.published_version,
                    } satisfies MetricRef)
                  : null,
              },
            });
        }}
      >
        <AppSelectItem value="">Choose a published metric</AppSelectItem>
        {metrics
          .filter(
            (m) => m.published_version && !m.archived && m.id !== selected?.id,
          )
          .map((m) => (
            <AppSelectItem key={m.id} value={String(m.id)}>
              {m.name} · v{m.published_version}
            </AppSelectItem>
          ))}
      </AppSelect>
    </label>
  );
  return (
    <>
      <a className="skip-link" href="#metrics-main">
        Skip to metrics
      </a>
      <DashboardHeader />
      <main className="bi-main" id="metrics-main" tabIndex={-1}>
        <ResourceFeedback resource={resource} label="Loading business metrics" />
        <header className="bi-hero">
          <div>
            <span className="bi-kicker">
              One business meaning. Traceable calculations.
            </span>
            <h1>Business metrics.</h1>
            <p>
              Define revenue, margin and the measures behind your decisions.
              Every answer keeps the exact published versions it used.
            </p>
            <Badge variant="secondary">
              Public — everyone can edit and publish
            </Badge>
          </div>
          <Button onClick={() => edit(null)}>Create metric</Button>
        </header>
        {error && (
          <div className="bi-error" role="alert">
            {error}
            <div className="bi-toolbar">
              <Button
                variant="outline"
                onClick={() =>
                  void load()
                    .then((values) => {
                      if (
                        selected &&
                        window.confirm(
                          "Reload the saved draft and discard your unsaved edits?",
                        )
                      ) {
                        const m = values.find((v) => v.id === selected.id);
                        if (m) edit(m);
                      }
                    })
                    .catch((e) => setError(e.message))
                }
              >
                Reload latest
              </Button>
            </div>
          </div>
        )}
        {draft && (
          <section className="bi-editor" aria-labelledby="metric-editor-title">
            <h2 id="metric-editor-title">
              {selected ? "Edit shared metric draft" : "New metric"}
            </h2>
            <p className="bi-note">
              Publication changes future calculations. It never rewrites
              historical evidence. Validation checks structure, not
              organizational approval.
            </p>
            <div className="bi-fields">
              <label className="bi-field">
                <span>Name</span>
                <input
                  required
                  maxLength={100}
                  value={draft.name}
                  onChange={(e) => update({ name: e.target.value })}
                />
              </label>
              <label className="bi-field">
                <span>Aliases, comma separated</span>
                <input
                  key={`aliases-${editorKey}`}
                  defaultValue={draft.aliases.join(", ")}
                  onChange={() => setDirty(true)}
                  onBlur={(e) =>
                    update({
                      aliases: e.target.value
                        .split(",")
                        .map((v) => v.trim())
                        .filter(Boolean),
                    })
                  }
                />
              </label>
              <label className="bi-field bi-wide">
                <span>Business meaning</span>
                <textarea
                  required
                  maxLength={1500}
                  value={draft.description}
                  onChange={(e) => update({ description: e.target.value })}
                />
              </label>
              <label className="bi-field">
                <span>Calculation</span>
                <AppSelect
                  value={
                    draft.formula.operation === "ratio" ||
                    draft.formula.operation === "subtract"
                      ? draft.formula.operation
                      : "measure"
                  }
                  onValueChange={(selectedValue) =>
                    selectedValue === "measure"
                      ? chooseMeasure("revenue")
                      : update({
                          formula: {
                            operation: selectedValue as "ratio" | "subtract",
                            measure: null,
                            left: null,
                            right: null,
                          },
                        })
                  }
                >
                  <AppSelectItem value="measure">
                    Approved source measure
                  </AppSelectItem>
                  <AppSelectItem value="subtract">Difference</AppSelectItem>
                  <AppSelectItem value="ratio">Ratio</AppSelectItem>
                </AppSelect>
              </label>
              {draft.formula.measure ? (
                <label className="bi-field">
                  <span>Measure</span>
                  <AppSelect
                    value={draft.formula.measure}
                    onValueChange={(selectedValue) =>
                      chooseMeasure(selectedValue)
                    }
                  >
                    {bindings.map((v) => (
                      <AppSelectItem value={String(v)} key={v}>
                        {v}
                      </AppSelectItem>
                    ))}
                  </AppSelect>
                </label>
              ) : (
                <>
                  <div />
                  {refSelect("left")}
                  {refSelect("right")}
                </>
              )}
              <label className="bi-field">
                <span>Time basis</span>
                <AppSelect
                  value={draft.time_basis}
                  onValueChange={(selectedValue) =>
                    update({
                      time_basis:
                        selectedValue as MetricDefinition["time_basis"],
                    })
                  }
                >
                  <AppSelectItem value="order_date">Order date</AppSelectItem>
                  <AppSelectItem value="refund_date">
                    Refund-date reporting calendar
                  </AppSelectItem>
                </AppSelect>
              </label>
              <label className="bi-field">
                <span>Units</span>
                <AppSelect
                  value={draft.unit}
                  onValueChange={(selectedValue) =>
                    update({ unit: selectedValue as MetricDefinition["unit"] })
                  }
                >
                  {["currency", "count", "percent", "number"].map((v) => (
                    <AppSelectItem value={String(v)} key={v}>
                      {v}
                    </AppSelectItem>
                  ))}
                </AppSelect>
              </label>
              <fieldset className="bi-wide">
                <legend>Supported breakdowns</legend>
                <div className="bi-toolbar">
                  {dimensions.map((v) => (
                    <label key={v}>
                      <input
                        type="checkbox"
                        checked={draft.dimensions.includes(v)}
                        onChange={(e) =>
                          update({
                            dimensions: e.target.checked
                              ? [...draft.dimensions, v]
                              : draft.dimensions.filter((d) => d !== v),
                          })
                        }
                      />{" "}
                      {v}
                    </label>
                  ))}
                </div>
              </fieldset>
              <label className="bi-field bi-wide">
                <span>Limitations</span>
                <textarea
                  maxLength={2000}
                  value={draft.limitations}
                  onChange={(e) => update({ limitations: e.target.value })}
                />
              </label>
              <label className="bi-field bi-wide">
                <span>Example questions, one per line</span>
                <textarea
                  key={`examples-${editorKey}`}
                  defaultValue={draft.examples.join("\n")}
                  onChange={() => setDirty(true)}
                  onBlur={(e) =>
                    update({
                      examples: e.target.value.split("\n").filter(Boolean),
                    })
                  }
                />
              </label>
            </div>
            <p className="bi-note">
              Calculation preview:{" "}
              {draft.formula.measure
                ? `${draft.formula.operation.replaceAll("_", " ")}(${draft.formula.measure})`
                : `${metrics.find((m) => m.id === draft.formula.left?.id)?.name ?? "Left metric"} ${draft.formula.operation === "ratio" ? "÷" : "−"} ${metrics.find((m) => m.id === draft.formula.right?.id)?.name ?? "Right metric"}`}
              . {draft.unit === "currency" ? "USD" : draft.unit};{" "}
              {draft.time_basis.replaceAll("_", " ")}. Ratios use aggregated
              components.
            </p>
            <div className="bi-toolbar">
              <Button disabled={busy} onClick={() => void save()}>
                Save draft
              </Button>
              <Button
                variant="outline"
                disabled={busy || !selected}
                onClick={() => void validate()}
              >
                Validate & inspect SQL
              </Button>
              <Button
                disabled={busy || !selected || dirty || selected.archived}
                onClick={() => selected && void action(selected, "publish")}
              >
                Publish shared definition
              </Button>
              <Button
                variant="ghost"
                onClick={() => {
                  if (canDiscard()) {
                    setDraft(null);
                    setSelected(null);
                    setDirty(false);
                  }
                }}
              >
                Close editor
              </Button>
            </div>
            {validation && (
              <details open>
                <summary>Structural validation and compiled query</summary>
                <pre
                  className="bi-code"
                  tabIndex={0}
                  role="region"
                  aria-label="Compiled metric structural validation"
                >
                  {validation}
                </pre>
              </details>
            )}
            {selected?.published_version ? (
              <>
                <h3>
                  Numerical test of published v{selected.published_version}
                </h3>
                <div className="bi-toolbar">
                  <label className="bi-field">
                    <span>Start date</span>
                    <input
                      type="date"
                      value={start}
                      onChange={(e) => setStart(e.target.value)}
                    />
                  </label>
                  <label className="bi-field">
                    <span>End date</span>
                    <input
                      type="date"
                      value={end}
                      onChange={(e) => setEnd(e.target.value)}
                    />
                  </label>
                  <Button
                    disabled={busy}
                    variant="outline"
                    onClick={() => void test()}
                  >
                    Test metric
                  </Button>
                  {error && (
                    <Button
                      disabled={busy}
                      variant="outline"
                      onClick={() => {
                        if (
                          !window.confirm(
                            "Start a separate source read? A previous uncertain preview may still be running. This consumes another analysis allowance.",
                          )
                        )
                          return;
                        pending.complete("test-metric", {
                          id: selected.id,
                          version: selected.published_version,
                          start,
                          end,
                        });
                        void test();
                      }}
                    >
                      Start a new preview
                    </Button>
                  )}
                </div>
                <p className="bi-note">
                  Runs a bounded read-only source query and consumes analysis
                  allowance.
                </p>
                {preview && (
                  <pre
                    className="bi-code"
                    tabIndex={0}
                    role="region"
                    aria-label="Saved numerical metric preview"
                  >
                    {preview}
                  </pre>
                )}
                <label className="bi-field">
                  <span>Inspect immutable version</span>
                  <AppSelect
                    key={selected.id}
                    defaultValue=""
                    onValueChange={(selectedValue) => {
                      if (selectedValue)
                        void api(
                          `/metrics/${selected.id}/revisions/${selectedValue}`,
                        )
                          .then((v) =>
                            setHistorical(JSON.stringify(v, null, 2)),
                          )
                          .catch((e) => setError(e.message));
                    }}
                  >
                    <AppSelectItem value="">Choose version</AppSelectItem>
                    {Array.from(
                      { length: selected.published_version },
                      (_, i) => (
                        <AppSelectItem key={i} value={String(i + 1)}>
                          Version {i + 1}
                        </AppSelectItem>
                      ),
                    )}
                  </AppSelect>
                </label>
                {historical && (
                  <pre
                    className="bi-code"
                    tabIndex={0}
                    role="region"
                    aria-label="Historical published metric definition"
                  >
                    {historical}
                  </pre>
                )}
              </>
            ) : null}
          </section>
        )}
        <div className="bi-toolbar">
          <label className="bi-field">
            <span>Search metrics</span>
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Name, meaning, alias or source"
            />
          </label>
          <label className="bi-field">
            <span>State</span>
            <AppSelect
              value={filter}
              onValueChange={(selectedValue) => setFilter(selectedValue)}
            >
              <AppSelectItem value="active">Active metrics</AppSelectItem>
              <AppSelectItem value="archived">Archived</AppSelectItem>
            </AppSelect>
          </label>
          <Button
            variant="outline"
            onClick={() => void load().catch((e) => setError(e.message))}
          >
            Refresh
          </Button>
        </div>
        {loading ? (
          <Skeleton aria-hidden="true" className="h-40 w-full" />
        ) : !resource.loaded ? null : !shown.length ? (
          <div className="bi-empty">
            No matching definitions. Create a metric, or ask an operator to add
            the packaged retail examples.
          </div>
        ) : (
          <div className="bi-grid">
            {shown.map((m) => (
              <article className="bi-card" key={m.id}>
                <Badge variant="outline">{status(m)}</Badge>
                <h2>
                  <Link href={`/metrics/${m.id}`}>{m.name}</Link>
                </h2>
                <p>{m.draft.description}</p>
                <p className="bi-note">
                  BigQuery · {m.draft.unit} ·{" "}
                  {m.draft.time_basis.replaceAll("_", " ")} · Published v
                  {m.published_version || "—"}
                </p>
                <p className="bi-note">
                  Updated {new Date(m.updated_at).toLocaleString()}
                </p>
                <div className="bi-card-actions">
                  <Button size="sm" variant="outline" onClick={() => edit(m)}>
                    Edit {m.name}
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => edit(m, true)}
                  >
                    Duplicate
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={busy}
                    onClick={() =>
                      void action(m, m.archived ? "restore" : "archive")
                    }
                  >
                    {m.archived ? "Restore" : "Archive"}
                  </Button>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
