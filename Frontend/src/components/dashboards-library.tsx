"use client";
import Link from "next/link";
import { workspacePath } from "@/lib/workspace-links";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  LayoutDashboard,
  Plus,
  RefreshCw,
  Trash2,
  Pencil,
  RotateCcw,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { Dashboard } from "@/lib/dashboard-types";
import {
  DashboardHeader,
  DashboardEditor,
  useDashboardMutation,
} from "@/components/dashboard-shared";
import {
  DashboardDownload,
  DashboardShare,
} from "@/components/dashboard-actions";
import { dashboardPath } from "@/lib/dashboard-links";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Empty,
  EmptyHeader,
  EmptyTitle,
  EmptyDescription,
  EmptyContent,
  EmptyMedia,
} from "@/components/ui/empty";
import { Skeleton } from "@/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Reveal } from "@/components/motion/reveal";

export function DashboardsLibrary() {
  const [boards, setBoards] = useState<Dashboard[]>([]);
  const [deleted, setDeleted] = useState(false);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("updated");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editor, setEditor] = useState<Dashboard | "new" | null>(null);
  const [busy, setBusy] = useState("");
  const [tick, setTick] = useState(0);
  const send = useDashboardMutation();
  const loadGeneration = useRef(0);
  const invalidateLoads = useCallback(() => {
    loadGeneration.current++;
  }, []);
  const load = useCallback(async () => {
    const generation = ++loadGeneration.current;
    try {
      const result = await api<{ dashboards: Dashboard[] }>(
        `/dashboards?deleted=${deleted}`,
      );
      if (generation !== loadGeneration.current) return;
      setBoards(result.dashboards);
      setError("");
    } catch (e) {
      if (generation === loadGeneration.current) setError((e as Error).message);
    } finally {
      if (generation === loadGeneration.current) setLoading(false);
    }
  }, [deleted]);
  useEffect(() => {
    let cancelled = false;
    void Promise.resolve().then(() => {
      if (!cancelled) return load();
    });
    return () => {
      cancelled = true;
      invalidateLoads();
    };
  }, [load, tick, invalidateLoads]);
  useEffect(() => {
    const focus = () => {
      void load();
    };
    window.addEventListener("focus", focus);
    return () => window.removeEventListener("focus", focus);
  }, [load]);
  async function change(board: Dashboard, restore = false) {
    if (
      !restore &&
      !window.confirm(
        `Delete “${board.name}”? Everyone will lose it from the active library. It remains recoverable for 30 days.`,
      )
    )
      return;
    setBusy(board.id);
    try {
      const result = await send(
        `/dashboards/${board.id}${restore ? "/restore" : ""}`,
        restore ? "POST" : "DELETE",
        { expected_revision: board.revision },
      );
      setTick((t) => t + 1);
      toast.success(
        restore ? "Dashboard restored" : "Dashboard deleted",
        !restore
          ? {
              description: "Recoverable for 30 days.",
              action: {
                label: "Undo",
                onClick: () => {
                  void change(result.dashboard, true);
                },
              },
            }
          : undefined,
      );
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  const shown = [...boards]
    .filter((b) =>
      `${b.name} ${b.description}`.toLowerCase().includes(query.toLowerCase()),
    )
    .sort((a, b) =>
      sort === "name"
        ? a.name.localeCompare(b.name)
        : b.updated_at.localeCompare(a.updated_at),
    );
  return (
    <>
      <a className="skip-link" href="#dashboards-main">
        Skip to dashboards
      </a>
      <DashboardHeader />
      <main className="dash-main" id="dashboards-main" tabIndex={-1}>
        <Reveal>
          <header className="dash-hero">
            <div>
              <p className="dash-eyebrow">SHARED RETAIL INTELLIGENCE</p>
              <h1>
                Dashboards<span>.</span>
              </h1>
              <p>
                Keep the charts that matter. Bring saved answers together for
                everyone to explore.
              </p>
              <Badge variant="secondary">
                Public — anyone can view and edit
              </Badge>
            </div>
            <Button asChild variant="outline"><Link href="/dashboards/build">Build with AI</Link></Button>
            <Button onClick={() => setEditor("new")}>
              <Plus data-icon="inline-start" />
              Create dashboard
            </Button>
          </header>
        </Reveal>
        <div className="dash-library-controls">
          <ToggleGroup
            type="single"
            variant="outline"
            aria-label="Dashboard visibility"
            value={deleted ? "deleted" : "active"}
            onValueChange={(v) => {
              if (!v) return;
              setDeleted(v === "deleted");
              setLoading(true);
            }}
          >
            <ToggleGroupItem value="active">Dashboards</ToggleGroupItem>
            <ToggleGroupItem value="deleted">Recently deleted</ToggleGroupItem>
          </ToggleGroup>
          <Input
            aria-label="Search dashboards"
            placeholder="Search names and descriptions…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <select
            aria-label="Sort dashboards"
            className="dashboard-native-select"
            value={sort}
            onChange={(e) => setSort(e.target.value)}
          >
            <option value="updated">Recently updated</option>
            <option value="name">Name</option>
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setLoading(true);
              setTick((t) => t + 1);
            }}
          >
            <RefreshCw data-icon="inline-start" />
            Reload
          </Button>
        </div>
        {error && (
          <Alert variant="destructive">
            <AlertTitle>Dashboard library unavailable</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
            <Button variant="outline" onClick={() => setTick((t) => t + 1)}>
              Retry
            </Button>
          </Alert>
        )}
        {loading ? (
          <div
            className="dash-library-grid"
            role="status"
            aria-label="Loading dashboards"
          >
            {[1, 2, 3].map((n) => (
              <Skeleton key={n} className="h-52 w-full" />
            ))}
          </div>
        ) : !shown.length ? (
          <Card>
            <CardContent>
              <Empty>
                <EmptyHeader>
                  <EmptyMedia variant="icon">
                    <LayoutDashboard />
                  </EmptyMedia>
                  <EmptyTitle>
                    {query
                      ? "No matching dashboards"
                      : deleted
                        ? "No recently deleted dashboards"
                        : "Your next insight deserves a place"}
                  </EmptyTitle>
                  <EmptyDescription>
                    {query
                      ? "Try a different name or description."
                      : deleted
                        ? "Deleted dashboards can be restored within 30 days."
                        : "Create a dashboard, ask a question in the workspace, then choose Pin to dashboard on its result."}
                  </EmptyDescription>
                </EmptyHeader>
                <EmptyContent>
                  <Button asChild variant="outline">
                    <Link href={workspacePath()}>Ask a question</Link>
                  </Button>
                </EmptyContent>
              </Empty>
            </CardContent>
          </Card>
        ) : (
          <div className="dash-library-grid">
            {shown.map((board) => (
              <Card key={board.id}>
                <CardHeader>
                  <div className="dash-card-icon">
                    <LayoutDashboard />
                  </div>
                  <CardTitle>{board.name}</CardTitle>
                  <CardDescription>
                    {board.description ||
                      "A shared collection of saved analytical results."}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p>
                    {board.card_count}{" "}
                    {board.card_count === 1 ? "card" : "cards"} · Updated{" "}
                    {new Date(board.updated_at).toLocaleString()}
                  </p>
                  <div className="dash-badges">
                    {board.sources.map((source) => (
                      <Badge key={source} variant="outline">
                        {source === "bigquery" ? "BigQuery" : "PostgreSQL"}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
                <CardFooter className="dash-card-actions">
                  {deleted ? (
                    <Button
                      disabled={busy === board.id}
                      onClick={() => void change(board, true)}
                    >
                      <RotateCcw data-icon="inline-start" />
                      Restore
                    </Button>
                  ) : (
                    <>
                      <Button asChild>
                        <Link
                          aria-label={`View ${board.name}`}
                          href={dashboardPath(board.id)}
                        >
                          View
                        </Link>
                      </Button>
                      <Button variant="outline" size="sm" asChild>
                        <Link
                          aria-label={`Edit ${board.name}`}
                          href={dashboardPath(board.id, "edit")}
                        >
                          <Pencil data-icon="inline-start" />
                          Edit
                        </Link>
                      </Button>
                      <DashboardShare dashboard={board} compact />
                      <DashboardDownload dashboard={board} compact />
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={busy === board.id}
                        aria-label={`Delete ${board.name}`}
                        onClick={() => void change(board)}
                      >
                        <Trash2 />
                      </Button>
                    </>
                  )}
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
        <p className="dash-footnote">
          Saved results only. Opening a dashboard never runs SQL or calls
          Gemini. Charts retain their original query timestamps.
        </p>
      </main>
      {editor && (
        <DashboardEditor
          dashboard={editor === "new" ? undefined : editor}
          onClose={() => setEditor(null)}
          onSaved={() => {
            setEditor(null);
            void load();
          }}
        />
      )}
    </>
  );
}
