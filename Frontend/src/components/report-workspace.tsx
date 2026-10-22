"use client";
import { useReadResource } from "@/hooks/use-read-resource";
import { ResourceFeedback } from "./resource-feedback";

import { AppSelect, AppSelectItem } from "@/components/ui/app-select";
import dynamic from "next/dynamic";
import Link from "next/link";
import { workspacePath } from "@/lib/workspace-links";
import { useEffect, useRef, useState } from "react";
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
import {
  PredictionEvidence,
  forecastMethodLabel,
} from "@/components/prediction-evidence";
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
  const [activeSection, setActiveSection] = useState("executive-summary");
  const pendingSectionFocus = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (!revision) return;
    const sections = Array.from(
      document.querySelectorAll<HTMLElement>(".report-section"),
    );
    const update = () => {
      const current = sections
        .filter((section) => section.getBoundingClientRect().top <= 160)
        .at(-1);
      setActiveSection(current?.id ?? "executive-summary");
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, [revision]);
  const resource = useReadResource(`report:${id}:${tick}`, (signal) => api<Report>(`/reports/${id}`, { signal }), (v) => { setReport(v); setError(""); });
  const selectedRevision = version ?? report?.latest_version;
  const revisionResource = useReadResource(`report-version:${id}:${selectedRevision}:${tick}`, (signal) => selectedRevision ? api<ReportRevision>(`/reports/${id}/revisions/${selectedRevision}`, { signal }) : Promise.resolve(null), (v) => { if (v) setRevision(v); });
  const evidenceResource = useReadResource(`report-evidence:${id}:${revision?.version}:${tick}`, async (signal) => {
    if (!revision) return [] as Artifact[];
    // Settle each saved card independently; a missing card cannot hide report text or other cards.
    const values: Artifact[] = [];
    const results = await Promise.allSettled(revision.document.artifact_ids.map(async (a) => {
      const value = await api<Artifact>(`/artifacts/${a}?metadata_only=true`, { signal });
      if (!signal.aborted) { values.push(value); setArtifacts((previous) => ({ ...previous, [value.id]: value })); }
    }));
    const failed = results.find((v) => v.status === "rejected");
    if (failed?.status === "rejected") throw failed.reason;
    return values;
  }, () => {});
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
      link.download = `querylane-${
        revision.document.title
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-|-$/g, "")
          .slice(0, 70) || id.slice(0, 12)
      }-v${revision.version}.${format === "data" ? "zip" : format}`;
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
        <ResourceFeedback resource={resource} label="Loading saved report" />
        <ResourceFeedback resource={revisionResource} label="Loading saved report version" />
        <ResourceFeedback resource={evidenceResource} label="Loading saved report charts" />
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
          resource.pending && !error && <Skeleton aria-hidden="true" className="h-64 mt-8" />
        ) : (
          <>
            <div className="reports-hero mt-6">
              <div>
                <div className="reports-eyebrow">
                  Public intelligence report
                </div>
                <h1>{doc?.title ?? report.name}</h1>
                <p>
                  {doc?.scope ??
                    (report.latest_version
                      ? "Loading the saved report and evidence…"
                      : "The analyst is preparing saved findings and evidence.")}
                </p>
                {doc && (
                  <details className="report-request">
                    <summary>Library name & source conversation</summary>
                    <p>{report.name}</p>
                    <Link href={workspacePath(report.conversation_id)}>
                      Open source conversation
                    </Link>
                  </details>
                )}
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
                  <AppSelect
                    id="report-version"
                    value={revision?.version}
                    onValueChange={(selectedValue) => {
                      setRevision(null);
                      setVersion(Number(selectedValue));
                      history.replaceState(
                        null,
                        "",
                        `/reports/${id}?version=${selectedValue}`,
                      );
                    }}
                  >
                    {[...report.versions].reverse().map((v) => (
                      <AppSelectItem value={String(v)} key={v}>
                        Version {v}
                      </AppSelectItem>
                    ))}
                  </AppSelect>
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
                <dl
                  className="report-facts"
                  aria-label="Saved report information"
                >
                  <div>
                    <dt>Saved version</dt>
                    <dd>
                      {revision?.version} ·{" "}
                      {doc.style === "business" ? "Business" : "Technical"}
                    </dd>
                  </div>
                  <div>
                    <dt>Created</dt>
                    <dd>
                      {new Date(doc.created_at).toLocaleDateString(undefined, {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                    </dd>
                  </div>
                  <div>
                    <dt>Evidence</dt>
                    <dd>{doc.artifact_ids.length} saved results</dd>
                  </div>
                  <div>
                    <dt>Source scope</dt>
                    <dd>
                      {doc.data_profile === "timeseries"
                        ? "Synthetic retail · multi-year"
                        : doc.data_profile}
                    </dd>
                  </div>
                </dl>
                <div className="report-mobile-outline">
                  <label htmlFor="report-section-select">Jump to section</label>
                  <AppSelect
                    id="report-section-select"
                    value={activeSection}
                    onCloseAutoFocus={(event) => {
                      if (pendingSectionFocus.current) {
                        event.preventDefault();
                        pendingSectionFocus.current.focus({
                          preventScroll: true,
                        });
                        pendingSectionFocus.current = null;
                      }
                    }}
                    onValueChange={(selectedValue) => {
                      const target = document.getElementById(selectedValue);
                      target?.scrollIntoView({
                        behavior: "instant",
                        block: "start",
                      });
                      pendingSectionFocus.current = target;
                      setActiveSection(selectedValue);
                    }}
                  >
                    <AppSelectItem value="executive-summary">
                      Executive summary
                    </AppSelectItem>
                    {doc.sections.map((section) => (
                      <AppSelectItem
                        key={section.id}
                        value={String(`section-${section.id}`)}
                      >
                        {section.title}
                      </AppSelectItem>
                    ))}
                    <AppSelectItem value="report-evidence">
                      Evidence & limitations
                    </AppSelectItem>
                  </AppSelect>
                </div>
                <div className="report-layout">
                  <nav className="report-outline" aria-label="Report sections">
                    <a
                      href="#executive-summary"
                      aria-current={
                        activeSection === "executive-summary"
                          ? "location"
                          : undefined
                      }
                    >
                      Executive summary
                    </a>
                    {doc.sections.map((s) => (
                      <a
                        key={s.id}
                        href={`#section-${s.id}`}
                        aria-current={
                          activeSection === `section-${s.id}`
                            ? "location"
                            : undefined
                        }
                      >
                        {s.title}
                      </a>
                    ))}
                    <a
                      href="#report-evidence"
                      aria-current={
                        activeSection === "report-evidence"
                          ? "location"
                          : undefined
                      }
                    >
                      Evidence & limitations
                    </a>
                  </nav>
                  <article className="report-document">
                    <section
                      id="executive-summary"
                      tabIndex={-1}
                      className="report-section report-executive"
                    >
                      <h2>Executive summary</h2>
                      <div className="report-summary">
                        <MarkdownContent>
                          {doc.summary.replace(/^\s*•\s+/gm, "- ")}
                        </MarkdownContent>
                      </div>
                      {doc.claims.length > 0 && (
                        <dl
                          className="report-highlights"
                          aria-label="Saved verified highlights"
                        >
                          {doc.claims
                            .filter(
                              (claim) =>
                                !/number of saved result rows|dimension labels/i.test(
                                  claim.label,
                                ),
                            )
                            .slice(0, 3)
                            .map((claim) => (
                              <div key={claim.id}>
                                <dt>{claim.label}</dt>
                                <dd>{claim.formatted}</dd>
                                <details>
                                  <summary>Calculation & evidence</summary>
                                  <p>{claim.calculation}</p>
                                  <p>Saved result: {claim.artifact_id}</p>
                                </details>
                              </div>
                            ))}
                        </dl>
                      )}
                    </section>
                    {doc.sections.map((s) => (
                      <section
                        key={s.id}
                        id={`section-${s.id}`}
                        tabIndex={-1}
                        className={`report-section report-section-${s.kind}`}
                      >
                        <h2>{s.title}</h2>
                        {s.kind === "recommendation" && (
                          <Badge variant="outline">
                            Recommendation · analyst interpretation
                          </Badge>
                        )}
                        <MarkdownContent>
                          {s.markdown.replace(/^\s*•\s+/gm, "- ")}
                        </MarkdownContent>
                        {s.artifact_ids.map(
                          (a) =>
                            artifacts[a] ? (
                              <div key={a} className="report-result-section">
                                {artifacts[a].prediction && (
                                  <ReportPrediction artifact={artifacts[a]} />
                                )}
                                <ResultCard
                                  artifact={artifacts[a]}
                                  showPredictionEvidence={false}
                                />
                              </div>
                            ) : <div key={a} className="report-result-section" aria-busy={evidenceResource.pending}><p role="status">{evidenceResource.error ? "Saved chart unavailable. Retry loading saved report charts above." : "Loading saved chart…"}</p>{evidenceResource.pending && <Skeleton aria-hidden="true" className="h-64" />}</div>,
                        )}
                      </section>
                    ))}
                    <section
                      id="report-evidence"
                      tabIndex={-1}
                      className="report-section"
                    >
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
                      <details className="report-source-times">
                        <summary>Independent source timestamps</summary>
                        <ul>
                          {Object.values(artifacts).flatMap((artifact) =>
                            artifact.provenance.map((source, index) => (
                              <li key={`${artifact.id}-${index}`}>
                                <strong>{source.source}</strong> ·{" "}
                                {new Date(source.executed_at).toLocaleString()}
                                <br />
                                {artifact.title}
                              </li>
                            )),
                          )}
                        </ul>
                        <p>
                          Each timestamp belongs to its saved source execution;
                          sources are not assumed to be one synchronized
                          snapshot.
                        </p>
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
                <AppSelect
                  value={revisionMode}
                  onValueChange={(selectedValue) =>
                    setRevisionMode(selectedValue)
                  }
                >
                  <AppSelectItem value="presentation">
                    Rework presentation — saved evidence
                  </AppSelectItem>
                  <AppSelectItem value="reanalyze">
                    Reanalyze — new source queries
                  </AppSelectItem>
                </AppSelect>
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
                <AppSelect
                  value={style}
                  onValueChange={(selectedValue) =>
                    setStyle(selectedValue as "business" | "technical")
                  }
                >
                  <AppSelectItem value="business">Business</AppSelectItem>
                  <AppSelectItem value="technical">Technical</AppSelectItem>
                </AppSelect>
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
  const researchConfig = useReadResource("report-research-configuration", (signal) => api<{ research_enabled: boolean }>("/reports/config", { signal }), (v) => setEnabled(v.research_enabled));
  if (!enabled) return <ResourceFeedback resource={researchConfig} label="Loading research configuration" />;
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
        <AppSelect
          id="research-topic"
          value={topic}
          onValueChange={(selectedValue) => setTopic(selectedValue)}
        >
          {[
            "retail seasonality",
            "retail forecasting methods",
            "retail inventory planning",
            "retail promotion measurement",
          ].map((t) => (
            <AppSelectItem value={String(t)} key={t}>
              {t}
            </AppSelectItem>
          ))}
        </AppSelect>
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

export function ReportPrediction({ artifact }: { artifact: Artifact }) {
  const prediction = artifact.prediction;
  if (!prediction) return null;
  const scenario = prediction.kind === "scenario";
  const adjusted = prediction.kind === "adjusted_plan";
  return (
    <div className="report-prediction">
      <p className="reports-eyebrow">
        {adjusted
          ? "Planning assumptions — not statistical predictions"
          : scenario
            ? "Conditional scenario"
            : "Forecast overview"}
      </p>
      <dl className="report-facts">
        <div>
          <dt>Observed through</dt>
          <dd>{prediction.cutoff}</dd>
        </div>
        <div>
          <dt>Horizon</dt>
          <dd>
            {prediction.horizon} {prediction.grain} periods
          </dd>
        </div>
        <div>
          <dt>Selected method</dt>
          <dd>
            {prediction.method === "timesfm_3"
              ? "TimesFM 3.0"
              : prediction.method.replaceAll("_", " ")}
            {prediction.preview ? " · Preview" : ""}
          </dd>
        </div>
      </dl>
      {prediction.status === "allocated" && (
        <p>Allocated estimate; this node was not independently modeled.</p>
      )}
      <p>{prediction.selection_reason}</p>
      <p className="report-prediction-caveat">
        {prediction.interval
          ? `Saved interval level: ${Math.round(prediction.interval.level * 100)}%.`
          : "Validated intervals unavailable; uncertainty is not quantified."}{" "}
        Solid lines represent observations; dashed lines represent predictions.
      </p>
      {prediction.scores && (
        <details>
          <summary>Candidate comparison · chronological backtests</summary>
          <div
            className="report-comparison-scroll"
            role="region"
            aria-label="Forecast candidate comparison"
            tabIndex={0}
          >
            <table>
              <caption>
                Held-out errors in the saved target units; lower is better. This
                is not an accuracy percentage.
              </caption>
              <thead>
                <tr>
                  <th scope="col">Method</th>
                  <th scope="col">MAE</th>
                  <th scope="col">RMSE</th>
                  <th scope="col">Outcome</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(prediction.scores).map(([method, score]) => (
                  <tr key={method}>
                    <th scope="row">{forecastMethodLabel(method)}</th>
                    <td>
                      {score.mae.toLocaleString(undefined, {
                        maximumFractionDigits: 2,
                      })}
                    </td>
                    <td>
                      {score.rmse.toLocaleString(undefined, {
                        maximumFractionDigits: 2,
                      })}
                    </td>
                    <td>
                      {method === prediction.method ? "Selected" : "Compared"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      )}
      {scenario && (
        <div className="report-scenario-assumptions">
          <h3>Explicit future assumptions</h3>
          <p>
            Baseline and alternative paths are conditional inputs, not causal
            lift estimates.
          </p>
          <ul>
            {(prediction.assumptions ?? []).map((assumption, index) => (
              <li key={index}>{assumption}</li>
            ))}
          </ul>
          <div className="report-scenario-paths">
            <div>
              <strong>Baseline path</strong>
              <p>
                {prediction.future_drivers?.length ?? 0} saved future periods
              </p>
            </div>
            <div>
              <strong>Alternative path</strong>
              <p>
                {prediction.scenario_drivers?.length ?? 0} saved future periods
              </p>
            </div>
          </div>
          <details>
            <summary>Baseline & alternative driver paths</summary>
            <div
              className="report-comparison-scroll"
              role="region"
              aria-label="Saved scenario assumptions"
              tabIndex={0}
            >
              <table>
                <caption>
                  Explicit assumptions for each future period; held-out targets
                  are not future inputs.
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Period</th>
                    <th scope="col">Driver</th>
                    <th scope="col">Baseline</th>
                    <th scope="col">Alternative</th>
                  </tr>
                </thead>
                <tbody>
                  {(prediction.future_drivers ?? []).flatMap((path, index) =>
                    (prediction.drivers ?? []).map((driver) => (
                      <tr key={`${index}-${driver}`}>
                        <th scope="row">{index + 1}</th>
                        <td>{driver}</td>
                        <td>{path[driver] ?? "Not available"}</td>
                        <td>
                          {prediction.scenario_drivers?.[index]?.[driver] ??
                            "Not available"}
                        </td>
                      </tr>
                    )),
                  )}
                </tbody>
              </table>
            </div>
          </details>
        </div>
      )}
      <details>
        <summary>Technical provenance & reproducibility</summary>
        <PredictionEvidence
          prediction={prediction}
          artifactId={artifact.id}
          reportId={artifact.report_id}
          reportVersion={artifact.report_version}
        />
      </details>
    </div>
  );
}
