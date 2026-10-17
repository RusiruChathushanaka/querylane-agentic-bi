"use client";
import dynamic from "next/dynamic";
import Link from "next/link";
import { workspacePath } from "@/lib/workspace-links";
import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  Download,
  Pencil,
  RefreshCw,
  Search,
  Share2,
} from "lucide-react";
import { toast } from "sonner";
import { api, backendUrl } from "@/lib/api";
import { usePreferences } from "@/hooks/use-preferences";
import type { Artifact } from "@/lib/types";
import type { Report, ReportRevision, ReportRun } from "@/lib/report-types";
import { DashboardHeader } from "@/components/dashboard-shared";
import { ReportRunCard } from "@/components/report-run-card";
import { MarkdownContent } from "@/components/markdown-content";
import { SkillEvidence } from "@/components/skill-evidence";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
const ResultCard = dynamic(() => import("@/components/result-card"), {
  loading: () => <Skeleton className="h-80" />,
});

export function ReportWorkspace({
  id,
  initialVersion,
}: {
  id: string;
  initialVersion?: number;
}) {
  const [report, setReport] = useState<Report | null>(null);
  const [version, setVersion] = useState(initialVersion);
  const [revision, setRevision] = useState<ReportRevision | null>(null);
  const [artifacts, setArtifacts] = useState<Record<string, Artifact>>({});
  const [error, setError] = useState("");
  const [dialog, setDialog] = useState<"rename" | "revise" | null>(null);
  const [tick, setTick] = useState(0);
  const [exporting, setExporting] = useState("");
  const load = useCallback(
    async (signal?: AbortSignal) => {
      try {
        const value = await api<Report>(`/reports/${id}`, { signal });
        if (signal?.aborted) return;
        setReport(value);
        const selected = version ?? value.latest_version;
        if (selected) {
          const saved = await api<ReportRevision>(
            `/reports/${id}/revisions/${selected}`,
            { signal },
          );
          const values = await Promise.all(
            saved.document.artifact_ids.map((a) =>
              api<Artifact>(`/artifacts/${a}?metadata_only=true`, { signal }),
            ),
          );
          if (signal?.aborted) return;
          setRevision(saved);
          setArtifacts(Object.fromEntries(values.map((a) => [a.id, a])));
        }
        setError("");
      } catch (e) {
        if (!signal?.aborted) setError((e as Error).message);
      }
    },
    [id, version],
  );
  useEffect(() => {
    const controller = new AbortController();
    void Promise.resolve().then(() => {
      if (!controller.signal.aborted) return load(controller.signal);
    });
    return () => controller.abort();
  }, [load, tick]);
  async function download(format: string) {
    if (!revision) return;
    setExporting(format);
    toast.loading("Preparing saved download", { id: `download:${id}` });
    try {
      const response = await fetch(
        `${await backendUrl()}/api/v1/reports/${id}/revisions/${revision.version}/downloads/${format}`,
        { cache: "no-store" },
      );
      if (!response.ok)
        throw new Error(
          (await response.json()).error?.message ?? "Download unavailable.",
        );
      const blob = await response.blob();
      const href = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = href;
      link.download = `querylane-${id.slice(0, 12)}-v${revision.version}.${format === "data" ? "zip" : format}`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(href), 60000);
      toast.success("Report downloaded", { id: `download:${id}` });
    } catch (e) {
      toast.error((e as Error).message, { id: `download:${id}` });
    } finally {
      setExporting("");
    }
  }
  const doc = revision?.document;
  return (
    <div className="reports-page">
      <a className="skip-link" href="#report-reader">
        Skip to report
      </a>
      <DashboardHeader />
      <main className="reports-main" id="report-reader" tabIndex={-1}>
        <Button asChild variant="ghost" size="sm">
          <Link href="/reports">
            <ArrowLeft aria-hidden />
            All reports
          </Link>
        </Button>
        {error && (
          <div role="alert" className="report-note">
            <p>{error}</p>
            <Button variant="outline" onClick={() => setTick((v) => v + 1)}>
              Reload latest
            </Button>
          </div>
        )}
        {!report ? (
          !error && <Skeleton className="h-64 mt-8" />
        ) : (
          <>
            <div className="reports-hero mt-6">
              <div>
                <div className="reports-eyebrow">
                  Public intelligence report
                </div>
                <h1>{report.name}</h1>
                <p>
                  {doc?.scope ??
                    (report.latest_version
                      ? "Loading the saved report and evidence…"
                      : "The analyst is preparing saved findings and evidence.")}
                </p>
              </div>
              <div className="report-actions">
                <Button
                  variant="outline"
                  onClick={() => {
                    void navigator.clipboard
                      .writeText(location.href)
                      .then(() => toast.success("Report link copied"))
                      .catch(() =>
                        toast.error("Copy the address from your browser."),
                      );
                  }}
                >
                  <Share2 aria-hidden />
                  Share
                </Button>
                <Button
                  variant="ghost"
                  disabled={!!report.active_run_id || report.deleted}
                  onClick={() => setDialog("rename")}
                >
                  <Pencil aria-hidden />
                  Rename
                </Button>
              </div>
            </div>
            {report.deleted && (
              <div className="report-note">
                This report is in Recently deleted. Its saved versions remain
                inspectable during recovery.
              </div>
            )}
            {report.active_run_id && (
              <ReportRunCard
                key={report.active_run_id}
                runId={report.active_run_id}
                onComplete={() => {
                  setVersion(undefined);
                  setTick((v) => v + 1);
                }}
              />
            )}
            {!doc && !!report.latest_version && !error && (
              <div role="status" aria-live="polite">
                <p className="report-note">Loading saved report version…</p>
                <Skeleton className="h-64 mt-6" />
              </div>
            )}
            {!report.active_run_id && !doc && !report.latest_version && (
              <div className="report-note">
                {report.status === "failed"
                  ? "The report did not finish. Its saved intermediate evidence remains available for operator inspection. Create a narrower report from the workspace."
                  : "No completed version is available."}
                <Button asChild variant="outline">
                  <Link href={workspacePath(report.conversation_id)}>
                    Return to chat
                  </Link>
                </Button>
              </div>
            )}
            {doc && (
              <>
                <div className="report-toolbar">
                  <label className="sr-only" htmlFor="report-version">
                    Saved report version
                  </label>
                  <select
                    id="report-version"
                    value={revision?.version}
                    onChange={(e) => {
                      setRevision(null);
                      setVersion(Number(e.target.value));
                      history.replaceState(
                        null,
                        "",
                        `/reports/${id}?version=${e.target.value}`,
                      );
                    }}
                  >
                    {[...report.versions].reverse().map((v) => (
                      <option value={v} key={v}>
                        Version {v}
                      </option>
                    ))}
                  </select>
                  <Badge variant="outline">{doc.style} report</Badge>
                  <Badge variant="secondary">{doc.data_profile}</Badge>
                  <div className="grow" />
                  {["pdf", "docx", "data"].map((format) => (
                    <Button
                      key={format}
                      size="sm"
                      variant="outline"
                      disabled={!!exporting}
                      onClick={() => void download(format)}
                    >
                      <Download aria-hidden />
                      {exporting === format
                        ? "Downloading…"
                        : format === "docx"
                          ? "Word"
                          : format === "data"
                            ? "All data (ZIP)"
                            : "PDF"}
                    </Button>
                  ))}
                  <Button
                    size="sm"
                    disabled={!!report.active_run_id || report.deleted}
                    onClick={() => setDialog("revise")}
                  >
                    <RefreshCw aria-hidden />
                    Revise report
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  Downloads contain this saved version. PDF/Word include preview
                  tables; data ZIP includes all saved rows, predictions, and
                  provenance. No new queries or model calls.
                </p>
                <div className="report-layout">
                  <nav className="report-outline" aria-label="Report sections">
                    <a href="#executive-summary">Executive summary</a>
                    {doc.sections.map((s) => (
                      <a key={s.id} href={`#section-${s.id}`}>
                        {s.title}
                      </a>
                    ))}
                    <a href="#report-evidence">Evidence & limitations</a>
                  </nav>
                  <article className="report-document">
                    <section id="executive-summary" className="report-section">
                      <h2>Executive summary</h2>
                      <div className="report-summary">
                        <MarkdownContent>{doc.summary}</MarkdownContent>
                      </div>
                    </section>
                    {doc.sections.map((s) => (
                      <section
                        key={s.id}
                        id={`section-${s.id}`}
                        className="report-section"
                      >
                        <h2>{s.title}</h2>
                        {s.kind === "recommendation" && (
                          <Badge variant="outline">
                            Recommendation · analyst interpretation
                          </Badge>
                        )}
                        <MarkdownContent>{s.markdown}</MarkdownContent>
                        {s.artifact_ids.map(
                          (a) =>
                            artifacts[a] && (
                              <ResultCard key={a} artifact={artifacts[a]} />
                            ),
                        )}
                      </section>
                    ))}
                    <section id="report-evidence" className="report-section">
                      <h2>Evidence & limitations</h2>
                      <div className="report-note">
                        <ul>
                          {doc.limitations.map((l, i) => (
                            <li key={i}>{l}</li>
                          ))}
                        </ul>
                      </div>
                      <details>
                        <summary>
                          Definitions, assumptions & numerical evidence
                        </summary>
                        <div className="report-note">
                          <h3>Definitions</h3>
                          <ul>
                            {doc.definitions.map((d, i) => (
                              <li key={i}>{d}</li>
                            ))}
                          </ul>
                          <h3>Assumptions</h3>
                          <ul>
                            {doc.assumptions.map((d, i) => (
                              <li key={i}>{d}</li>
                            ))}
                          </ul>
                          <h3>Verified calculations</h3>
                          <ul>
                            {doc.claims.map((c) => (
                              <li key={c.id}>
                                <strong>
                                  {c.label}: {c.formatted}
                                </strong>{" "}
                                — {c.calculation}
                              </li>
                            ))}
                          </ul>
                          <p>
                            {doc.mode_note} · {doc.model} · Created{" "}
                            {new Date(doc.created_at).toLocaleString()}
                          </p>
                        </div>
                      </details>
                      <SkillEvidence
                        skills={doc.skills_used}
                        warnings={doc.skill_warnings}
                      />
                    </section>
                    <ResearchPanel />
                  </article>
                </div>
              </>
            )}
            {dialog && (
              <ReportEditDialog
                report={report}
                revision={revision}
                mode={dialog}
                onClose={() => setDialog(null)}
                onSaved={() => {
                  setDialog(null);
                  setVersion(undefined);
                  setTick((v) => v + 1);
                }}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

function ReportEditDialog({
  report,
  revision,
  mode,
  onClose,
  onSaved,
}: {
  report: Report;
  revision: ReportRevision | null;
  mode: "rename" | "revise";
  onClose: () => void;
  onSaved: () => void;
}) {
  const { preferences } = usePreferences();
  const [name, setName] = useState(report.name);
  const [question, setQuestion] = useState("");
  const [style, setStyle] = useState(revision?.document.style ?? "business");
  const [revisionMode, setRevisionMode] = useState("presentation");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [expected, setExpected] = useState(report.revision);
  const [key] = useState(() => crypto.randomUUID());
  const dirty =
    name !== report.name ||
    !!question.trim() ||
    style !== revision?.document.style;
  function close() {
    if (!busy && (!dirty || window.confirm("Discard unsaved report changes?")))
      onClose();
  }
  useEffect(() => {
    if (!dirty) return;
    const guard = (e: BeforeUnloadEvent) => e.preventDefault();
    window.addEventListener("beforeunload", guard);
    return () => window.removeEventListener("beforeunload", guard);
  }, [dirty]);
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (mode === "rename")
        await api(`/reports/${report.id}`, {
          method: "PATCH",
          body: JSON.stringify({ name, expected_revision: expected }),
        });
      else
        await api<ReportRun>(`/reports/${report.id}/revisions`, {
          method: "POST",
          body: JSON.stringify({
            question: question.trim(),
            style,
            expected_revision: expected,
            base_version: revision?.version,
            mode: revisionMode,
            idempotency_key: key,
            model:
              preferences.textModel === "default"
                ? undefined
                : preferences.textModel,
          }),
        });
      toast.success(
        mode === "rename" ? "Report renamed" : "New report version requested",
      );
      onSaved();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open) close();
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {mode === "rename"
              ? "Rename public report"
              : "Create a new report version"}
          </DialogTitle>
          <DialogDescription>
            {mode === "rename"
              ? "Changes the shared library label. Saved report documents remain unchanged."
              : "Earlier versions stay available. Presentation changes reuse saved evidence; reanalysis runs new controlled queries."}
          </DialogDescription>
        </DialogHeader>
        <form className="report-dialog-form" onSubmit={save}>
          {mode === "rename" ? (
            <label>
              Name
              <Input
                value={name}
                maxLength={120}
                required
                onChange={(e) => setName(e.target.value)}
              />
            </label>
          ) : (
            <>
              <label>
                Revision type
                <select
                  value={revisionMode}
                  onChange={(e) => setRevisionMode(e.target.value)}
                >
                  <option value="presentation">
                    Rework presentation — saved evidence
                  </option>
                  <option value="reanalyze">
                    Reanalyze — new source queries
                  </option>
                </select>
              </label>
              <label>
                {revisionMode === "presentation"
                  ? "How should the report change?"
                  : "New analysis question"}
                <Textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  maxLength={4000}
                  required
                />
              </label>
              <label>
                Style
                <select
                  value={style}
                  onChange={(e) =>
                    setStyle(e.target.value as "business" | "technical")
                  }
                >
                  <option value="business">Business</option>
                  <option value="technical">Technical</option>
                </select>
              </label>
            </>
          )}
          {error && (
            <div role="alert">
              <p className="report-error">{error}</p>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  void api<Report>(`/reports/${report.id}`)
                    .then((r) => {
                      setExpected(r.revision);
                      setError(
                        "Latest revision loaded. Your draft is preserved; review before saving.",
                      );
                    })
                    .catch((e) => setError(e.message));
                }}
              >
                Reload latest revision
              </Button>
            </div>
          )}
          <div className="report-actions">
            <Button
              type="button"
              variant="outline"
              onClick={close}
              disabled={busy}
            >
              Cancel
            </Button>
            <Button
              disabled={
                busy || (mode === "rename" ? !name.trim() : !question.trim())
              }
              type="submit"
            >
              {busy
                ? "Saving…"
                : mode === "rename"
                  ? "Save name"
                  : "Create version"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

type ResearchResult = {
  text: string;
  grounding: {
    grounding_chunks?: { web?: { uri?: string; title?: string } }[];
    grounding_supports?: unknown[];
    search_entry_point?: { rendered_content?: string };
  };
};
function ResearchPanel() {
  const { preferences } = usePreferences();
  const [enabled, setEnabled] = useState(false);
  const [topic, setTopic] = useState("retail seasonality");
  const [value, setValue] = useState<ResearchResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let cancelled = false;
    void api<{ research_enabled: boolean }>("/reports/config")
      .then((c) => {
        if (!cancelled) setEnabled(c.research_enabled);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);
  if (!enabled) return null;
  async function search() {
    setBusy(true);
    setError("");
    setValue(null);
    try {
      setValue(
        await api<ResearchResult>("/reports/research", {
          method: "POST",
          body: JSON.stringify({
            topic,
            model:
              preferences.textModel === "default"
                ? undefined
                : preferences.textModel,
          }),
        }),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <aside className="report-research">
      <h2>External research</h2>
      <p className="report-note">
        Optional Google Search results are visible only in this browser panel.
        They are not saved to the shared report or its downloads. No database
        rows or private context are sent.
      </p>
      <div className="report-actions">
        <label className="sr-only" htmlFor="research-topic">
          Public research topic
        </label>
        <select
          id="research-topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        >
          {[
            "retail seasonality",
            "retail forecasting methods",
            "retail inventory planning",
            "retail promotion measurement",
          ].map((t) => (
            <option key={t}>{t}</option>
          ))}
        </select>
        <Button variant="outline" disabled={busy} onClick={() => void search()}>
          <Search aria-hidden />
          {busy ? "Researching…" : "Search public topic"}
        </Button>
        {value && (
          <Button variant="ghost" onClick={() => setValue(null)}>
            Clear panel
          </Button>
        )}
      </div>
      {error && <p role="alert">{error}</p>}
      {value && (
        <>
          <div className="report-research-text">{value.text}</div>
          <div className="report-research-links">
            {value.grounding.grounding_chunks?.map(
              (c, i) =>
                c.web?.uri?.startsWith("https://") && (
                  <a
                    href={c.web.uri}
                    target="_blank"
                    rel="noopener noreferrer"
                    key={i}
                  >
                    {c.web.title ?? `Source ${i + 1}`}
                  </a>
                ),
            )}
          </div>
          {value.grounding.search_entry_point?.rendered_content && (
            <iframe
              title="Google Search suggestions"
              sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox"
              srcDoc={value.grounding.search_entry_point.rendered_content}
              referrerPolicy="no-referrer"
            />
          )}
        </>
      )}
    </aside>
  );
}
