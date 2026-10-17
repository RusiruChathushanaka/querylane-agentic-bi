"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  FileChartColumn,
  LoaderCircle,
  Square,
  ArrowUpRight,
} from "lucide-react";
import { toast } from "sonner";
import { api, guestApi } from "@/lib/api";
import type { ReportRun, Report } from "@/lib/report-types";
import { assumptionHorizon, assumptionRows } from "@/lib/report-assumptions";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Reveal } from "@/components/motion/reveal";

const active = (run: ReportRun) =>
  ["queued", "running", "waiting_input"].includes(run.status);
export function ReportRunCard({
  runId,
  onComplete,
}: {
  runId: string;
  onComplete?: () => void;
}) {
  const router = useRouter();
  const [run, setRun] = useState<ReportRun | null>(null);
  const [canControl, setCanControl] = useState(false);
  const [answer, setAnswer] = useState("");
  const [assumptions, setAssumptions] = useState<Record<string, string>>({});
  const [scenario, setScenario] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [connectionError, setConnectionError] = useState("");
  const notified = useRef(false);
  const completeCallback = useRef(onComplete);
  useEffect(() => {
    completeCallback.current = onComplete;
  }, [onComplete]);
  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const next = await api<ReportRun>(`/report-runs/${runId}`);
        if (cancelled) return;
        setRun(next);
        setConnectionError("");
        if (next.status === "complete" && !notified.current) {
          notified.current = true;
          toast.success("Your report is ready", {
            id: `report:${runId}`,
            action: {
              label: "Open report",
              onClick: () => {
                router.push(
                  `/reports/${next.report_id}?version=${next.version}`,
                );
              },
            },
          });
          completeCallback.current?.();
        }
        if (active(next))
          timer = setTimeout(
            poll,
            next.status === "waiting_input" ? 4000 : 1500,
          );
      } catch (e) {
        if (!cancelled) {
          setConnectionError((e as Error).message);
          timer = setTimeout(poll, 5000);
        }
      }
    }
    void poll();
    void guestApi<{ can_control: boolean }>(`/report-runs/${runId}/controls`)
      .then((v) => {
        if (!cancelled) setCanControl(v.can_control);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [runId, router]);
  async function cancel() {
    setBusy(true);
    try {
      await api(`/report-runs/${runId}/cancel`, { method: "POST" });
      toast.info("Stop requested", {
        description: "The worker will confirm cancellation.",
      });
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function clarify(e: React.FormEvent) {
    e.preventDefault();
    if (!run) return;
    setBusy(true);
    setError("");
    try {
      const forecast_inputs = Object.fromEntries(
        (run.clarification_requirements ?? []).map((requirement) => {
          const read = (path: string) => Object.fromEntries(requirement.drivers.map((driver) =>
            [driver, assumptions[`${requirement.target}:${path}:${driver}`] ?? ""],
          ));
          return [requirement.target, {
            baseline: assumptionRows(requirement, read("baseline")),
            scenario: scenario ? assumptionRows(requirement, read("scenario")) : [],
          }];
        }),
      );
      const value = await api<ReportRun>(
        `/report-runs/${runId}/clarifications`,
        {
          method: "POST",
          body: JSON.stringify({
            answer: answer.trim() || "Use the future assumptions supplied in this form.",
            expected_revision: run.revision, forecast_inputs,
          }),
        },
      );
      setRun(value);
      setAnswer("");
      setAssumptions({});
      setScenario(false);
      toast.success("Report clarification saved");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Reveal className="report-run-card">
      <div className="report-run-heading">
        <FileChartColumn aria-hidden />
        <div>
          <strong>Advanced analysis</strong>
          <p>Public report · ordinary chat remains available</p>
        </div>
        <Badge variant="outline">
          {run?.status.replaceAll("_", " ") ?? "Connecting"}
        </Badge>
      </div>
      <p role="status" aria-live="polite">
        {run?.status === "complete"
          ? "Report and downloads are ready."
          : run?.status === "failed" || run?.status === "cancelled"
            ? run.error
            : (run?.stage ?? "Loading saved progress…")}
      </p>
      {run && ["running", "queued"].includes(run.status) && (
        <div className="report-run-working">
          <LoaderCircle className="spin" aria-hidden />
          <span>Typically a few minutes. You can leave this page.</span>
        </div>
      )}
      {run?.status === "waiting_input" && (
        <div className="report-clarification">
          <h3>One detail before continuing</h3>
          <p>{run.clarification}</p>
          {run.clarifications.map((c, i) => (
            <details key={i}>
              <summary>Previous clarification</summary>
              <p>{c.question}</p>
              <pre>{c.answer}</pre>
            </details>
          ))}
          {canControl ? (
            <form onSubmit={clarify}>
              {!!run.clarification_requirements?.length && (
                <>
                  <p>Enter one value to keep it constant, or comma-separated values in future-period order. Use the same units as the source data. No values are assumed for you.</p>
                  <label>
                    <input type="checkbox" checked={scenario} disabled={busy}
                      onChange={(event) => setScenario(event.target.checked)} />
                    {" "}Compare an alternative scenario
                  </label>
                  {run.clarification_requirements.map((requirement) => (
                    <fieldset key={requirement.target} disabled={busy}>
                      <legend>{requirement.target} · next {assumptionHorizon(requirement)} {requirement.grain} periods</legend>
                      {(scenario ? ["baseline", "scenario"] : ["baseline"]).map((path) =>
                        requirement.drivers.map((driver) => {
                          const key = `${requirement.target}:${path}:${driver}`;
                          return <label key={key} className="report-assumption-field">
                            {path === "baseline" ? "Baseline" : "Alternative"} · {driver}
                            <Textarea value={assumptions[key] ?? ""} required maxLength={3000}
                              onChange={(event) => setAssumptions((current) => ({ ...current, [key]: event.target.value }))} />
                          </label>;
                        }),
                      )}
                    </fieldset>
                  ))}
                </>
              )}
              <label htmlFor={`clarify-${runId}`}>{run.clarification_requirements?.length ? "Additional context (optional)" : "Your clarification"}</label>
              <Textarea
                id={`clarify-${runId}`}
                value={answer}
                maxLength={4000}
                onChange={(e) => setAnswer(e.target.value)}
                required={!run.clarification_requirements?.length}
                disabled={busy}
              />
              <Button disabled={busy || (!answer.trim() && !run.clarification_requirements?.length)} type="submit">
                Continue report
              </Button>
            </form>
          ) : (
            <p>
              The visitor who requested this report can provide the
              clarification.
            </p>
          )}
        </div>
      )}
      {(error || connectionError) && (
        <p role="alert" className="report-error">
          {error || connectionError} Your draft is preserved.
        </p>
      )}
      <div className="report-actions">
        {run && (
          <Button asChild variant="outline" size="sm">
            <Link href={`/reports/${run.report_id}`}>
              Open report
              <ArrowUpRight aria-hidden />
            </Link>
          </Button>
        )}
        {run && active(run) && canControl && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => void cancel()}
            disabled={busy || run.cancel_requested}
          >
            <Square aria-hidden />
            {run.cancel_requested ? "Stopping…" : "Stop report"}
          </Button>
        )}
      </div>
    </Reveal>
  );
}

export function ConversationReports({
  conversationId,
  refreshKey = 0,
}: {
  conversationId: string;
  refreshKey?: number;
}) {
  const [reports, setReports] = useState<Report[]>([]);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    const result = await api<{ reports: Report[] }>(
      `/reports?conversation_id=${conversationId}`,
    );
    setReports(result.reports);
    setError("");
  }, [conversationId]);
  useEffect(() => {
    let cancelled = false;
    void api<{ reports: Report[] }>(
      `/reports?conversation_id=${conversationId}`,
    )
      .then((v) => {
        if (!cancelled) {
          setReports(v.reports);
          setError("");
        }
      })
      .catch((e) => {
        if (!cancelled && e.code !== "reports_disabled") setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, [conversationId, refreshKey]);
  return (
    <section
      aria-label="Reports from this exploration"
      className="conversation-reports"
    >
      {error && <p role="alert">Reports could not load: {error}</p>}
      {reports.map((r) => (
        <div key={r.id}>
          {["running", "queued", "waiting_input"].includes(r.status) ? (
            <ActiveConversationReport
              reportId={r.id}
              onComplete={() => void load()}
            />
          ) : (
            <Link className="saved-report-link" href={`/reports/${r.id}`}>
              <FileChartColumn aria-hidden />
              <span>
                <strong>{r.name}</strong>
                <small>
                  {r.status === "complete"
                    ? `Saved report · version ${r.latest_version}`
                    : r.status}{" "}
                  · public
                </small>
              </span>
              <ArrowUpRight aria-hidden />
            </Link>
          )}
        </div>
      ))}
    </section>
  );
}
function ActiveConversationReport({
  reportId,
  onComplete,
}: {
  reportId: string;
  onComplete: () => void;
}) {
  const [runId, setRunId] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    void api<Report>(`/reports/${reportId}`)
      .then((r) => {
        if (!cancelled) setRunId(r.active_run_id ?? null);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [reportId]);
  return runId ? (
    <ReportRunCard runId={runId} onComplete={onComplete} />
  ) : (
    <Link href={`/reports/${reportId}`}>Open saved report</Link>
  );
}
