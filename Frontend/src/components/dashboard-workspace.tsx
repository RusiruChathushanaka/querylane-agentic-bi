"use client";

import Link from "next/link";
import { workspacePath } from "@/lib/workspace-links";
import dynamic from "next/dynamic";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowUp,
  ArrowLeft,
  LayoutDashboard,
  Pencil,
  PinOff,
  RefreshCw,
  RotateCcw,
  Save,
  Eye,
} from "lucide-react";
import { toast } from "sonner";
import { motion } from "motion/react";
import { useAppMotion } from "@/hooks/use-app-motion";
import { SPRING_LAYOUT } from "@/lib/ease";
import { api } from "@/lib/api";
import { savedResult } from "@/lib/saved-result-loader";
import { dashboardPath } from "@/lib/dashboard-links";
import type { Artifact } from "@/lib/types";
import type {
  ChartCapture,
  Dashboard,
  DashboardItem,
} from "@/lib/dashboard-types";
import {
  DashboardEditor,
  DashboardHeader,
  useDashboardMutation,
} from "@/components/dashboard-shared";
import {
  DashboardDownload,
  DashboardShare,
} from "@/components/dashboard-actions";
import { SkillEvidence } from "@/components/skill-evidence";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Empty,
  EmptyHeader,
  EmptyTitle,
  EmptyDescription,
  EmptyContent,
  EmptyMedia,
} from "@/components/ui/empty";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
  CardContent,
} from "@/components/ui/card";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

const ResultCard = dynamic(() => import("@/components/result-card"), {
  loading: () => <Skeleton className="h-80 w-full" />,
});

function DashboardWidget({
  item,
  edit,
  busy,
  position,
  count,
  onChange,
  onMove,
  onUnpin,
}: {
  item: DashboardItem;
  edit: boolean;
  busy: boolean;
  position: number;
  count: number;
  onChange: (
    item: DashboardItem,
    payload: Record<string, unknown>,
  ) => Promise<boolean>;
  onMove: (id: string, step: number) => Promise<void>;
  onUnpin: (item: DashboardItem) => Promise<void>;
}) {
  const { reduced } = useAppMotion();
  const root = useRef<HTMLElement>(null);
  const [visible, setVisible] = useState(false);
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  const [capture, setCapture] = useState<ChartCapture | null>(null);
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(item.title);
  const [note, setNote] = useState(item.note);
  const [width, setWidth] = useState(item.width);
  const [highlights, setHighlights] = useState(item.view.highlights);
  const [decimals, setDecimals] = useState(item.view.decimals);
  const [formError, setFormError] = useState("");
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: "150px" },
    );
    if (root.current) observer.observe(root.current);
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    if (!visible) return;
    const controller = new AbortController();
    savedResult<Artifact>(
      `/artifacts/${item.artifact_id}?metadata_only=true`,
      controller.signal,
    )
      .then((value) => {
        if (!controller.signal.aborted) {
          setArtifact(value);
          setError("");
        }
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(e.message);
      });
    return () => controller.abort();
  }, [item.artifact_id, visible, retry]);
  const dirty =
    title !== item.title ||
    note !== item.note ||
    width !== item.width ||
    highlights !== item.view.highlights ||
    decimals !== item.view.decimals;
  useEffect(() => {
    if (!editing || !dirty) return;
    const guard = (e: BeforeUnloadEvent) => {
      e.preventDefault();
    };
    window.addEventListener("beforeunload", guard);
    return () => window.removeEventListener("beforeunload", guard);
  }, [editing, dirty]);
  function closeEditor() {
    if (!busy && (!dirty || window.confirm("Discard unsaved card details?")))
      setEditing(false);
  }
  return (
    <motion.section
      layout={reduced ? false : "position"}
      transition={reduced ? { duration: 0 } : SPRING_LAYOUT}
      ref={root}
      id={`dashboard-item-${item.id}`}
      className={cn(
        "dashboard-widget",
        item.width === "wide" && "dashboard-widget-wide",
      )}
      aria-label={`${item.title}, card ${position + 1} of ${count}`}
    >
      <div className="dash-widget-context">
        <Badge variant="outline">Saved result</Badge>
        <span>
          {item.summary.data_profile === "timeseries"
            ? "Expanded retail history"
            : "Original demo history"}{" "}
          · Pinned {new Date(item.pinned_at).toLocaleString()}
        </span>
      </div>
      {edit && (
        <div
          className="dash-widget-actions"
          role="group"
          aria-label={`Edit ${item.title}`}
        >
          <Button
            variant="outline"
            size="sm"
            disabled={busy || position === 0}
            data-move="earlier"
            onClick={() => void onMove(item.id, -1)}
          >
            <ArrowUp data-icon="inline-start" />
            Earlier
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={busy || position === count - 1}
            data-move="later"
            onClick={() => void onMove(item.id, 1)}
          >
            <ArrowDown data-icon="inline-start" />
            Later
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={busy}
            onClick={() => {
              setTitle(item.title);
              setNote(item.note);
              setWidth(item.width);
              setHighlights(item.view.highlights);
              setDecimals(item.view.decimals);
              setFormError("");
              setEditing(true);
            }}
          >
            <Pencil data-icon="inline-start" />
            Card details
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={busy || !capture?.ready}
            onClick={() => {
              if (capture) void onChange(item, { view: capture.state });
            }}
          >
            <Save data-icon="inline-start" />
            Save card view
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={busy}
            onClick={() => void onUnpin(item)}
          >
            <PinOff data-icon="inline-start" />
            Unpin
          </Button>
        </div>
      )}
      {item.note && <p className="dash-note">{item.note}</p>}
      {!visible || (!artifact && !error) ? (
        <div role="status" aria-label={`Loading ${item.title}`}>
          <Skeleton className="h-80 w-full" />
        </div>
      ) : error ? (
        <Alert variant="destructive">
          <AlertTitle>Saved chart unavailable</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
          <Button variant="outline" onClick={() => setRetry((r) => r + 1)}>
            Retry chart
          </Button>
        </Alert>
      ) : (
        artifact && (
          <>
            <ResultCard
              key={JSON.stringify(item.view)}
              artifact={{ ...artifact, title: item.title }}
              initialState={item.view}
              onCapture={setCapture}
              allowPin={false}
            />
            <SkillEvidence
              skills={artifact.skills_used ?? []}
              warnings={artifact.skill_warnings ?? []}
            />
          </>
        )
      )}
      <footer className="dash-widget-footer">
        <details>
          <summary>Original question</summary>
          <p>
            {item.summary.question ||
              "Question context was not recorded for this historical result."}
          </p>
        </details>
        {item.conversation_available === false ? (
          <span>
            Original chat removed; saved data and evidence remain available.
          </span>
        ) : (
          <Link href={workspacePath(item.conversation_id)}>
            Open original conversation ↗
          </Link>
        )}
        <span>
          {item.summary.executed_at
            .map(
              (at, i) =>
                `${item.summary.sources[i] ?? "Source"}: ${new Date(at).toLocaleString()}`,
            )
            .join(" · ")}
        </span>
      </footer>
      <Dialog
        open={editing}
        onOpenChange={(open) => {
          if (!open) closeEditor();
        }}
      >
        <DialogContent className="dashboard-dialog">
          <DialogHeader>
            <DialogTitle>Edit card details</DialogTitle>
            <DialogDescription>
              Changes are shared with everyone. The original result remains
              unchanged.
            </DialogDescription>
          </DialogHeader>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              setFormError("");
              if (
                await onChange(item, {
                  title,
                  note,
                  width,
                  ...(highlights !== item.view.highlights ||
                  decimals !== item.view.decimals
                    ? { view: { ...item.view, highlights, decimals } }
                    : {}),
                })
              )
                setEditing(false);
              else
                setFormError(
                  "Save failed. Your draft is preserved. Close this dialog and reload the dashboard if another visitor changed it.",
                );
            }}
          >
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor={`card-title-${item.id}`}>Title</FieldLabel>
                <Input
                  id={`card-title-${item.id}`}
                  maxLength={160}
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor={`card-note-${item.id}`}>Note</FieldLabel>
                <Textarea
                  id={`card-note-${item.id}`}
                  maxLength={500}
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor={`card-width-${item.id}`}>Width</FieldLabel>
                <select
                  className="dashboard-native-select"
                  id={`card-width-${item.id}`}
                  value={width}
                  onChange={(e) =>
                    setWidth(e.target.value as "standard" | "wide")
                  }
                >
                  <option value="standard">Standard</option>
                  <option value="wide">Wide</option>
                </select>
              </Field>
              <Field>
                <FieldLabel htmlFor={`card-highlights-${item.id}`}>
                  Automatic highlights
                </FieldLabel>
                <Switch
                  id={`card-highlights-${item.id}`}
                  checked={highlights}
                  onCheckedChange={setHighlights}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor={`card-decimals-${item.id}`}>
                  Number precision
                </FieldLabel>
                <select
                  className="dashboard-native-select"
                  id={`card-decimals-${item.id}`}
                  value={decimals}
                  onChange={(e) =>
                    setDecimals(Number(e.target.value) as 0 | 1 | 2)
                  }
                >
                  <option value="0">0 decimal places</option>
                  <option value="1">1 decimal place</option>
                  <option value="2">2 decimal places</option>
                </select>
              </Field>
            </FieldGroup>
            {formError && <p role="alert">{formError}</p>}
            <DialogFooter>
              <Button variant="outline" type="button" onClick={closeEditor}>
                Cancel
              </Button>
              <Button disabled={busy || !title.trim()} type="submit">
                Save card details
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </motion.section>
  );
}

export function DashboardWorkspace({
  id,
  initialEdit = false,
}: {
  id: string;
  initialEdit?: boolean;
}) {
  const router = useRouter();
  const query = useSearchParams();
  const [board, setBoard] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const edit = query ? query.get("mode") === "edit" : initialEdit;
  const [details, setDetails] = useState(false);
  const [busy, setBusy] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  const [removed, setRemoved] = useState<DashboardItem[] | null>(null);
  const [offset, setOffset] = useState<number | null>(0);
  const [showRemoved, setShowRemoved] = useState(false);
  const [loadTick, setLoadTick] = useState(0);
  const send = useDashboardMutation();
  const load = useCallback(async () => {
    try {
      const value = await api<Dashboard>(`/dashboards/${id}`);
      setBoard(value);
      setError("");
      setNotice("");
    } catch (e) {
      setError((e as Error).message);
    }
  }, [id]);
  useEffect(() => {
    let cancelled = false;
    void Promise.resolve().then(() => {
      if (!cancelled) return load();
    });
    return () => {
      cancelled = true;
    };
  }, [load, loadTick]);
  useEffect(() => {
    if (!board) return;
    const focus = () => {
      void api<Dashboard>(`/dashboards/${id}`)
        .then((latest) => {
          if (latest.revision !== board.revision)
            setNotice(
              "Another visitor changed this dashboard. Reload latest when you are ready; your current view is preserved.",
            );
        })
        .catch(() =>
          setNotice("Could not check for shared changes. Reload to try again."),
        );
    };
    window.addEventListener("focus", focus);
    return () => window.removeEventListener("focus", focus);
  }, [board, id]);
  function reload() {
    if (
      board?.items?.length &&
      !window.confirm(
        "Reload the latest dashboard? Unsaved details and temporary chart views will be discarded.",
      )
    )
      return;
    setLoadTick((t) => t + 1);
  }
  function setMode(editing: boolean) {
    router.replace(dashboardPath(id, editing ? "edit" : "view"), {
      scroll: false,
    });
  }
  async function refreshRemoved(append = false) {
    try {
      const result = await api<{
        items: DashboardItem[];
        next_offset: number | null;
      }>(
        `/dashboards/${id}/items?removed=true&offset=${append ? (offset ?? 0) : 0}`,
      );
      setRemoved((old) =>
        append ? [...(old ?? []), ...result.items] : result.items,
      );
      setOffset(result.next_offset);
    } catch (e) {
      toast.error((e as Error).message);
    }
  }
  async function changeItem(
    item: DashboardItem,
    payload: Record<string, unknown>,
  ) {
    if (!board) return false;
    setBusy(true);
    try {
      await send(`/dashboards/${id}/items/${item.id}`, "PATCH", {
        ...payload,
        expected_revision: board.revision,
      });
      await load();
      toast.success("Dashboard card saved");
      return true;
    } catch (e) {
      setNotice((e as Error).message);
      toast.error((e as Error).message);
      return false;
    } finally {
      setBusy(false);
    }
  }
  async function move(itemId: string, step: number) {
    if (!board) return;
    const order = [...board.item_ids],
      position = order.indexOf(itemId),
      next = position + step;
    if (next < 0 || next >= order.length) return;
    [order[position], order[next]] = [order[next], order[position]];
    setBusy(true);
    try {
      await send(`/dashboards/${id}/layout`, "PUT", {
        expected_revision: board.revision,
        item_ids: order,
      });
      await load();
      setAnnouncement(`Card moved to position ${next + 1} of ${order.length}.`);
      requestAnimationFrame(() =>
        document
          .getElementById(`dashboard-item-${itemId}`)
          ?.querySelector<HTMLButtonElement>("[data-move]:not(:disabled)")
          ?.focus(),
      );
    } catch (e) {
      setNotice((e as Error).message);
      toast.error((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function restoreItem(item: DashboardItem, revision?: number) {
    if (!board) return;
    setBusy(true);
    try {
      await send(`/dashboards/${id}/items/${item.id}/restore`, "POST", {
        expected_revision: revision ?? board.revision,
      });
      await load();
      await refreshRemoved();
      toast.success("Card restored");
    } catch (e) {
      setNotice((e as Error).message);
      toast.error((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function unpin(item: DashboardItem) {
    if (!board) return;
    setBusy(true);
    try {
      const result = await send(
        `/dashboards/${id}/items/${item.id}`,
        "DELETE",
        { expected_revision: board.revision },
      );
      await load();
      if (showRemoved) await refreshRemoved();
      setAnnouncement(`${item.title} removed from this dashboard.`);
      toast.success("Chart unpinned", {
        description: "The original answer and other dashboards are unchanged.",
        action: {
          label: "Undo",
          onClick: () => {
            void restoreItem(item, result.dashboard.revision);
          },
        },
      });
    } catch (e) {
      setNotice((e as Error).message);
      toast.error((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <a className="skip-link" href="#dashboard-main">
        Skip to dashboard
      </a>
      <DashboardHeader />
      <main className="dash-main" id="dashboard-main" tabIndex={-1}>
        <Button asChild variant="ghost" size="sm">
          <Link href="/dashboards">
            <ArrowLeft data-icon="inline-start" />
            All dashboards
          </Link>
        </Button>
        {error && (
          <Alert variant="destructive">
            <AlertTitle>Dashboard unavailable</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
            <Button variant="outline" onClick={() => setLoadTick((t) => t + 1)}>
              Retry
            </Button>
          </Alert>
        )}
        {!board && !error && (
          <div role="status" aria-label="Loading dashboard">
            <Skeleton className="h-72 w-full" />
          </div>
        )}
        {board && (
          <>
            <header className="dash-hero">
              <div>
                <p className="dash-eyebrow">PUBLIC DASHBOARD</p>
                <h1>{board.name}</h1>
                <p>
                  {board.description ||
                    "A shared collection of saved analytical results."}
                </p>
                <Badge variant="secondary">
                  Public — anyone can view and edit
                </Badge>
                <Badge variant="outline">
                  {edit ? "Edit mode" : "View mode"}
                </Badge>
                <p className="dash-footnote">
                  Saved results — no automatic refresh. {board.card_count}{" "}
                  {board.card_count === 1 ? "card" : "cards"} · Version{" "}
                  {board.revision}
                </p>
              </div>
              <div className="dash-card-actions">
                {edit && !board.deleted && <Button asChild variant="outline"><Link href={`/dashboards/build?dashboard=${board.id}`}>Improve with AI</Link></Button>}
                <DashboardShare dashboard={board} />
                {!board.deleted && <DashboardDownload dashboard={board} />}
                <Button variant="outline" onClick={reload}>
                  <RefreshCw data-icon="inline-start" />
                  Reload latest
                </Button>
                {!board.deleted && (
                  <>
                    {edit && (
                      <Button
                        variant="outline"
                        onClick={() => setDetails(true)}
                      >
                        <Pencil data-icon="inline-start" />
                        Edit details
                      </Button>
                    )}
                    <div
                      role="group"
                      aria-label="Dashboard mode"
                      className="dash-card-actions"
                    >
                      <Button
                        variant={!edit ? "default" : "outline"}
                        aria-pressed={!edit}
                        onClick={() => setMode(false)}
                      >
                        <Eye data-icon="inline-start" />
                        View dashboard
                      </Button>
                      <Button
                        variant={edit ? "default" : "outline"}
                        aria-pressed={edit}
                        onClick={() => setMode(true)}
                      >
                        <Pencil data-icon="inline-start" />
                        Edit dashboard
                      </Button>
                    </div>
                  </>
                )}
              </div>
            </header>
            {notice && (
              <Alert>
                <AlertTitle>Shared dashboard update</AlertTitle>
                <AlertDescription>{notice}</AlertDescription>
                <Button variant="outline" size="sm" onClick={reload}>
                  Reload latest
                </Button>
              </Alert>
            )}
            <p className="sr-only" role="status" aria-live="polite">
              {announcement}
            </p>
            {board.deleted ? (
              <Card>
                <CardHeader>
                  <CardTitle>This dashboard is recently deleted</CardTitle>
                  <CardDescription>
                    Restore it within its recovery window to view its cards.
                  </CardDescription>
                </CardHeader>
                <CardFooter>
                  <Button
                    disabled={busy}
                    onClick={async () => {
                      setBusy(true);
                      try {
                        await send(`/dashboards/${id}/restore`, "POST", {
                          expected_revision: board.revision,
                        });
                        await load();
                        toast.success("Dashboard restored");
                      } catch (e) {
                        toast.error((e as Error).message);
                      } finally {
                        setBusy(false);
                      }
                    }}
                  >
                    <RotateCcw data-icon="inline-start" />
                    Restore dashboard
                  </Button>
                </CardFooter>
              </Card>
            ) : (
              <>
                {edit && (
                  <p className="dash-footnote">
                    Move cards with Earlier/Later. Layout changes save
                    immediately. Chart exploration stays temporary until you
                    choose Save card view.
                  </p>
                )}
                {!board.items?.length ? (
                  <Card>
                    <CardContent>
                      <Empty>
                        <EmptyHeader>
                          <EmptyMedia variant="icon">
                            <LayoutDashboard />
                          </EmptyMedia>
                          <EmptyTitle>Start with a question</EmptyTitle>
                          <EmptyDescription>
                            Ask the business analyst, then choose Pin to
                            dashboard on any saved chart, KPI, or table.
                          </EmptyDescription>
                        </EmptyHeader>
                        <EmptyContent>
                          <Button asChild>
                            <Link href={workspacePath()}>Ask a question</Link>
                          </Button>
                        </EmptyContent>
                      </Empty>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="dashboard-grid">
                    {board.items.map((item, index) => (
                      <DashboardWidget
                        key={item.id}
                        item={item}
                        edit={edit}
                        busy={busy}
                        position={index}
                        count={board.items!.length}
                        onChange={changeItem}
                        onMove={move}
                        onUnpin={unpin}
                      />
                    ))}
                  </div>
                )}
                {edit && (
                  <div className="dash-removed">
                    <Button
                      variant="ghost"
                      onClick={() => {
                        setShowRemoved(!showRemoved);
                        if (!showRemoved) void refreshRemoved();
                      }}
                    >
                      <RotateCcw data-icon="inline-start" />
                      {showRemoved
                        ? "Hide removed cards"
                        : "Recently removed cards"}
                    </Button>
                    {showRemoved && (
                      <section aria-label="Recently removed cards">
                        <h2>Recently removed</h2>
                        {removed === null ? (
                          <p role="status">Loading removed cards…</p>
                        ) : !removed.length ? (
                          <p>
                            No recoverable cards. Removed cards can be restored
                            for 30 days.
                          </p>
                        ) : (
                          removed.map((item) => (
                            <div className="dash-removed-item" key={item.id}>
                              <span>{item.title}</span>
                              <Button
                                size="sm"
                                variant="outline"
                                disabled={busy}
                                onClick={() => void restoreItem(item)}
                              >
                                Restore card
                              </Button>
                            </div>
                          ))
                        )}
                        {offset !== null && removed !== null && (
                          <Button
                            variant="outline"
                            onClick={() => void refreshRemoved(true)}
                          >
                            Load more removed cards
                          </Button>
                        )}
                      </section>
                    )}
                  </div>
                )}
              </>
            )}
          </>
        )}
        {details && board && (
          <DashboardEditor
            dashboard={board}
            onClose={() => setDetails(false)}
            onSaved={() => {
              setDetails(false);
              void load();
            }}
          />
        )}
      </main>
    </>
  );
}
