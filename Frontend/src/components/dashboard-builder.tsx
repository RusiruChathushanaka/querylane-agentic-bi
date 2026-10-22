"use client";
import { useReadResource } from "@/hooks/use-read-resource";
import { ResourceFeedback } from "./resource-feedback";

import { AppSelect, AppSelectItem } from "@/components/ui/app-select";
import Link from "next/link";
import { dashboardChanges } from "@/lib/planning-review";
import { PlanningSkills } from "./planning-skills";
import { useUnsavedNavigation } from "@/hooks/use-unsaved-navigation";
import { usePreferences } from "@/hooks/use-preferences";
import { usePendingRequest } from "@/hooks/use-pending-request";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api, guestApi } from "@/lib/api";
import type {
  DashboardBuild,
  JobRun,
  ProposedCard,
} from "@/lib/planning-types";
import type { Artifact } from "@/lib/types";
import type { Dashboard } from "@/lib/dashboard-types";
import type { ChartCapture } from "@/lib/dashboard-types";
import { DashboardHeader } from "./dashboard-shared";
import dynamic from "next/dynamic";
const ResultCard = dynamic(() => import("./result-card"), { ssr: false });
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";

export function SavedArtifactPreview({
  id,
  view,
  allowPin = false,
  onUseView,
}: {
  id: string;
  view?: ProposedCard["view"];
  allowPin?: boolean;
  onUseView?: (view: ProposedCard["view"]) => void;
}) {
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const [capture, setCapture] = useState<ChartCapture | null>(null);
  const resource = useReadResource(`saved-preview:${id}`, (signal) => api<Artifact>(`/artifacts/${id}`, { signal }), setArtifact);
  return artifact ? (
    <>
      <ResultCard
        key={id}
        artifact={artifact}
        initialState={view}
        allowPin={allowPin}
        onCapture={onUseView ? setCapture : undefined}
      />
      {onUseView && (
        <Button
          variant="outline"
          disabled={!capture?.ready}
          onClick={() => capture && onUseView(capture.state)}
        >
          Use this explored view in the proposal
        </Button>
      )}
    </>
  ) : (
    <ResourceFeedback resource={resource} label="Loading saved chart" skeleton />
  );
}

export function JobControls({
  run,
  onChange,
}: {
  run: JobRun;
  onChange: () => void;
}) {
  const [canControl, setCanControl] = useState(false);
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    void guestApi<{ can_control: boolean }>(`/report-runs/${run.id}/controls`)
      .then((v) => setCanControl(v.can_control))
      .catch(() => setCanControl(false));
  }, [run.id]);
  async function send(clarify = false) {
    setBusy(true);
    setError("");
    try {
      await api(
        `/report-runs/${run.id}/${clarify ? "clarifications" : "cancel"}`,
        {
          method: "POST",
          ...(clarify
            ? {
                body: JSON.stringify({
                  answer,
                  expected_revision: run.revision,
                }),
              }
            : {}),
        },
      );
      toast.success(
        clarify ? "Clarification submitted" : "Cancellation requested",
        {
          description: clarify
            ? undefined
            : "The worker must confirm its terminal state.",
        },
      );
      onChange();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section aria-label="Analysis progress">
      <div className="bi-progress" role="status">
        <strong>{run.stage}</strong>
        <p>{run.status.replaceAll("_", " ")}</p>
      </div>
      {run.error && (
        <p className="bi-error" role="alert">
          {run.error}
        </p>
      )}
      {error && (
        <p className="bi-error" role="alert">
          {error}
        </p>
      )}
      {run.clarification && (
        <div className="bi-card">
          <p>{run.clarification}</p>
          {canControl && (
            <>
              <label className="bi-field">
                <span>Required information</span>
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                />
              </label>
              <Button
                disabled={busy || !answer.trim()}
                onClick={() => void send(true)}
              >
                Continue analysis
              </Button>
            </>
          )}
        </div>
      )}
      {canControl &&
        !["complete", "failed", "cancelled"].includes(run.status) && (
          <Button
            className="mt-3"
            disabled={busy}
            variant="outline"
            onClick={() => void send()}
          >
            Cancel computation
          </Button>
        )}
    </section>
  );
}

export function DashboardBuilder({
  dashboardId,
  buildId,
}: {
  dashboardId?: string;
  buildId?: string;
}) {
  const router = useRouter();
  const pending = usePendingRequest();
  const [skillIds, setSkillIds] = useState<string[]>([]);
  const { preferences } = usePreferences();
  const [objective, setObjective] = useState("");
  const [audience, setAudience] = useState("Business leadership");
  const [source, setSource] = useState("all");
  const [model, setModel] = useState<string | null>(null);
  const selectedModel =
    model ?? (preferences.textModel === "default" ? "" : preferences.textModel);
  const [models, setModels] = useState<
    { id: string; label?: string; name?: string }[]
  >([]);
  const [reuse, setReuse] = useState(true);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [build, setBuild] = useState<DashboardBuild | null>(null);
  const [recent, setRecent] = useState<JobRun[]>([]);
  const [proposal, setProposal] =
    useState<DashboardBuild["proposal"]>(undefined);
  const [dirty, setDirty] = useState(false);
  useUnsavedNavigation(dirty);
  const [runId, setRunId] = useState(buildId ?? "");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const recentResource = useReadResource("dashboard-build-history", (signal) => guestApi<{ builds: JobRun[] }>("/dashboard-builds", { signal }), (v) => setRecent(v.builds));
  const modelResource = useReadResource("dashboard-build-models", (signal) => api<{ models: { id: string; label?: string; name?: string }[] }>("/models", { signal }), (v) => setModels(v.models));
  const resource = useReadResource(`dashboard-build:${runId}`, (signal) => runId ? guestApi<DashboardBuild>(`/dashboard-builds/${runId}`, { signal }) : Promise.resolve(null), (v) => {
    if (v && !dirty) { setBuild(v); setProposal(v.proposal); }
  }, 5000);
  const load = resource.refresh;
  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => {
      if (dirty) e.preventDefault();
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);
  async function startBuild() {
    setBusy(true);
    setError("");
    try {
      const board = dashboardId
        ? await api<Dashboard>(`/dashboards/${dashboardId}`)
        : null;
      const run = await api<JobRun>("/dashboard-builds", {
        method: "POST",
        body: JSON.stringify({
          objective,
          skill_ids: skillIds,
          audience,
          source,
          model: selectedModel || null,
          reuse_saved: reuse,
          start: start || null,
          end: end || null,
          dashboard_id: board?.id,
          expected_revision: board?.revision,
          request_id: pending.id("build", {
            objective,
            audience,
            source,
            model: selectedModel,
            reuse,
            start,
            end,
            dashboardId,
            skillIds,
          }),
        }),
      });
      pending.complete("build", {
        objective,
        audience,
        source,
        model: selectedModel,
        reuse,
        start,
        end,
        dashboardId,
        skillIds,
      });
      setRunId(run.id);
      setDirty(false);
      setProposal(undefined);
      history.replaceState(null, "", `/dashboards/build?build=${run.id}`);
      toast.success("Dashboard analysis queued", {
        description: "You can leave and return to review the saved proposal.",
      });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function patchCard(index: number, patch: Partial<ProposedCard>) {
    setDirty(true);
    setProposal((p) =>
      p
        ? {
            ...p,
            cards: p.cards.map((c, i) =>
              i === index ? { ...c, ...patch } : c,
            ),
          }
        : p,
    );
  }
  async function save(rebase = false) {
    if (!build || !proposal) return;
    setBusy(true);
    setError("");
    try {
      const value = await api<DashboardBuild>(`/dashboard-builds/${runId}`, {
        method: "PATCH",
        body: JSON.stringify({
          ...proposal,
          omitted: undefined,
          rebase,
          expected_revision: build.revision,
          request_id: pending.id("proposal", {
            runId,
            proposal,
            rebase,
            revision: build.revision,
          }),
        }),
      });
      pending.complete("proposal", {
        runId,
        proposal,
        rebase,
        revision: build.revision,
      });
      setBuild(value);
      setProposal(value.proposal);
      setDirty(false);
      toast.success(
        rebase
          ? "Proposal rebased; review changes before publishing"
          : "Proposal saved",
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function publish(undo = false) {
    if (!build || dirty) return;
    setBusy(true);
    setError("");
    try {
      const result = await api<{ dashboard_id: string; build: DashboardBuild }>(
        `/dashboard-builds/${runId}/${undo ? "undo" : "publish"}`,
        {
          method: "POST",
          body: JSON.stringify({
            expected_revision: build.revision,
            request_id: pending.id("publish", {
              runId,
              undo,
              revision: build.revision,
            }),
          }),
        },
      );
      pending.complete("publish", { runId, undo, revision: build.revision });
      setBuild(result.build);
      toast.success(
        undo
          ? "Dashboard restored to its previous state"
          : "Dashboard published",
        {
          action: {
            label: "Open",
            onClick: () => {
              router.push(`/dashboards/${result.dashboard_id}`);
            },
          },
        },
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const changes = dashboardChanges(
    build?.base_cards ?? [],
    proposal?.cards ?? [],
  );
  return (
    <>
      <a className="skip-link" href="#builder-main">
        Skip to dashboard builder
      </a>
      <DashboardHeader />
      <main id="builder-main" className="bi-main" tabIndex={-1}>
        <ResourceFeedback resource={resource} label="Loading dashboard proposal" />
        <ResourceFeedback resource={recentResource} label="Loading your dashboard builds" />
        <ResourceFeedback resource={modelResource} label="Loading dashboard model choices" />
        <header className="bi-hero">
          <div>
            <span className="bi-kicker">
              From objective to a reviewed dashboard
            </span>
            <h1>{dashboardId ? "Improve with AI." : "Build with AI."}</h1>
            <p>
              Describe the decisions you want to support. Querylane assembles
              saved evidence, analyzes missing questions, and gives you the
              final say before publication.
            </p>
            <Badge variant="secondary">
              Public dashboards · review before publishing
            </Badge>
          </div>
          <Button asChild variant="outline">
            <Link href="/dashboards">Dashboard library</Link>
          </Button>
        </header>
        {error && (
          <div role="alert" className="bi-error">
            {error}
          </div>
        )}
        {!runId && (
          <form
            className="bi-editor"
            onSubmit={(e) => {
              e.preventDefault();
              void startBuild();
            }}
          >
            <div className="bi-fields">
              <label className="bi-field bi-wide">
                <span>Business objective</span>
                <textarea
                  required
                  minLength={3}
                  maxLength={4000}
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  placeholder="Build a retail performance dashboard with revenue trends, regional targets and returns."
                />
              </label>
              <label className="bi-field">
                <span>Audience</span>
                <input
                  maxLength={200}
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                />
              </label>
              <label className="bi-field">
                <span>Sources</span>
                <AppSelect
                  value={source}
                  onValueChange={(selectedValue) => setSource(selectedValue)}
                >
                  <AppSelectItem value="all">
                    BigQuery + PostgreSQL
                  </AppSelectItem>
                  <AppSelectItem value="bigquery">BigQuery</AppSelectItem>
                  <AppSelectItem value="postgres">PostgreSQL</AppSelectItem>
                </AppSelect>
              </label>
              <label className="bi-field">
                <span>Start date (optional)</span>
                <input
                  type="date"
                  value={start}
                  onChange={(e) => setStart(e.target.value)}
                />
              </label>
              <label className="bi-field">
                <span>End date (optional)</span>
                <input
                  type="date"
                  value={end}
                  onChange={(e) => setEnd(e.target.value)}
                />
              </label>
              <label className="bi-field">
                <span>Analysis model</span>
                <AppSelect
                  value={selectedModel}
                  onValueChange={(selectedValue) => setModel(selectedValue)}
                >
                  <AppSelectItem value="">Workspace default</AppSelectItem>
                  {models.map((m) => (
                    <AppSelectItem key={m.id} value={String(m.id)}>
                      {m.label ?? m.name ?? m.id}
                    </AppSelectItem>
                  ))}
                </AppSelect>
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={reuse}
                  onChange={(e) => setReuse(e.target.checked)}
                />{" "}
                Reuse compatible saved evidence
              </label>
              <PlanningSkills
                source={source}
                selected={skillIds}
                onChange={setSkillIds}
              />
            </div>
            <p className="bi-note">
              Default four cards; at most four new analytical questions. New
              analysis consumes the shared advanced-analysis allowance. Saved
              charts retain their actual cutoffs.
            </p>
            <Button disabled={busy || !objective.trim()} type="submit">
              Generate dashboard proposal
            </Button>
          </form>
        )}
        {build?.run && (
          <JobControls
            run={build.run}
            onChange={() => void load().catch((e) => setError(e.message))}
          />
        )}
        {build?.status === "review" && proposal && (
          <section className="bi-editor" aria-labelledby="proposal-title">
            <h2 id="proposal-title">Review your dashboard proposal</h2>
            <div className="bi-fields">
              <label className="bi-field">
                <span>Dashboard name</span>
                <input
                  value={proposal.name}
                  maxLength={80}
                  onChange={(e) => {
                    setProposal({ ...proposal, name: e.target.value });
                    setDirty(true);
                  }}
                />
              </label>
              <label className="bi-field">
                <span>Description</span>
                <input
                  value={proposal.description}
                  maxLength={500}
                  onChange={(e) => {
                    setProposal({ ...proposal, description: e.target.value });
                    setDirty(true);
                  }}
                />
              </label>
            </div>
            <p className="bi-note">
              For existing dashboards, retained cards are included below.
              Removing a card proposes an unpin. Publishing applies all reviewed
              changes together.
            </p>
            {changes.removed.length > 0 && (
              <div className="bi-note">
                <strong>Proposed removals</strong>
                <ul>
                  {changes.removed.map((c) => (
                    <li key={c.artifact_id}>{c.title}</li>
                  ))}
                </ul>
              </div>
            )}
            {proposal.omitted.map((v, i) => (
              <p className="bi-note" key={i}>
                {v}
              </p>
            ))}
            {proposal.cards.map((card, i) => (
              <article className="bi-card my-4" key={card.artifact_id}>
                <div className="bi-toolbar">
                  <Badge variant="outline">{changes.cards[i]?.status}</Badge>
                  <Badge variant="outline">
                    {card.reused
                      ? "Reused / retained evidence"
                      : "New analysis"}
                  </Badge>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setProposal({
                        ...proposal,
                        cards: proposal.cards.filter((_, index) => i !== index),
                      });
                      setDirty(true);
                    }}
                  >
                    Remove card
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={!i}
                    onClick={() => {
                      const cards = [...proposal.cards];
                      [cards[i - 1], cards[i]] = [cards[i], cards[i - 1]];
                      setProposal({ ...proposal, cards });
                      setDirty(true);
                    }}
                  >
                    Move earlier
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={i === proposal.cards.length - 1}
                    onClick={() => {
                      const cards = [...proposal.cards];
                      [cards[i + 1], cards[i]] = [cards[i], cards[i + 1]];
                      setProposal({ ...proposal, cards });
                      setDirty(true);
                    }}
                  >
                    Move later
                  </Button>
                </div>
                <div className="bi-fields">
                  <label className="bi-field">
                    <span>Card {i + 1} title</span>
                    <input
                      maxLength={160}
                      value={card.title}
                      onChange={(e) => patchCard(i, { title: e.target.value })}
                    />
                  </label>
                  <label className="bi-field">
                    <span>Width</span>
                    <AppSelect
                      value={card.width}
                      onValueChange={(selectedValue) =>
                        patchCard(i, {
                          width: selectedValue as ProposedCard["width"],
                        })
                      }
                    >
                      <AppSelectItem value="standard">Standard</AppSelectItem>
                      <AppSelectItem value="wide">Wide</AppSelectItem>
                    </AppSelect>
                  </label>
                  <label className="bi-field">
                    <span>Published chart type</span>
                    <AppSelect
                      value={card.view.view}
                      onValueChange={(selectedValue) =>
                        patchCard(i, {
                          view: { ...card.view, view: selectedValue },
                        })
                      }
                    >
                      {[
                        "table",
                        "kpi",
                        "line",
                        "area",
                        "bar",
                        "pie",
                        "scatter",
                      ].map((v) => (
                        <AppSelectItem value={String(v)} key={v}>
                          {v}
                        </AppSelectItem>
                      ))}
                    </AppSelect>
                  </label>
                  <label className="bi-field">
                    <span>Note</span>
                    <input
                      maxLength={500}
                      value={card.note}
                      onChange={(e) => patchCard(i, { note: e.target.value })}
                    />
                  </label>
                </div>
                <SavedArtifactPreview
                  key={`${card.artifact_id}:${card.view.view}`}
                  id={card.artifact_id}
                  view={card.view}
                  onUseView={(view) => patchCard(i, { view })}
                />
              </article>
            ))}
            <div className="bi-toolbar">
              <Button
                disabled={busy || !dirty}
                variant="outline"
                onClick={() => void save()}
              >
                Save proposal edits
              </Button>
              {build.dashboard_id && (
                <Button
                  disabled={busy}
                  variant="outline"
                  onClick={() => void save(true)}
                >
                  Rebase onto latest dashboard
                </Button>
              )}
              <Button
                disabled={busy || dirty || !proposal.name.trim()}
                onClick={() => void publish()}
              >
                Publish reviewed dashboard
              </Button>
            </div>
            <p className="bi-note">
              Publication performs no new queries. Unsupported chart choices are
              rejected with your draft preserved.
            </p>
          </section>
        )}
        {build?.status === "published" && (
          <section className="bi-card mt-5">
            <h2>Dashboard published</h2>
            <p>
              Your evidence is saved. Opening the dashboard runs no new
              analysis.
            </p>
            <div className="bi-toolbar">
              <Button asChild>
                <Link href={`/dashboards/${build.dashboard_id}`}>
                  Open dashboard
                </Link>
              </Button>
              <Button
                disabled={busy}
                variant="outline"
                onClick={() => void publish(true)}
              >
                Undo AI publication
              </Button>
            </div>
            <p className="bi-note">
              Undo requires the dashboard to remain at the published revision.
            </p>
          </section>
        )}
        {recent.length > 0 && (
          <section className="mt-8">
            <h2>Your recent builds in this browser session</h2>
            <div className="bi-grid mt-3">
              {recent.map((r) => (
                <article className="bi-card" key={r.id}>
                  <p>
                    {r.stage} · {r.status}
                  </p>
                  <Link href={`/dashboards/build?build=${r.id}`}>
                    Open saved build
                  </Link>
                </article>
              ))}
            </div>
          </section>
        )}
      </main>
    </>
  );
}
