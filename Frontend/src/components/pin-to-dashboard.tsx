"use client";

import { AppSelect, AppSelectItem } from "@/components/ui/app-select";
import "@/app/dashboards.css";

import Link from "@/components/ui/app-link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { Pin, Plus } from "lucide-react";
import { toast } from "sonner";
import { api, ApiError } from "@/lib/api";
import { describeChartView } from "@/lib/chart-view-state";
import type { Artifact } from "@/lib/types";
import type {
  ChartCapture,
  Dashboard,
  DashboardMutation,
} from "@/lib/dashboard-types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";

export function PinToDashboard({
  artifact,
  capture,
}: {
  artifact: Artifact;
  capture: ChartCapture;
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [boards, setBoards] = useState<Dashboard[]>([]);
  const [selected, setSelected] = useState("");
  const [query, setQuery] = useState("");
  const [title, setTitle] = useState(artifact.title);
  const [name, setName] = useState("");
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [duplicate, setDuplicate] = useState(false);
  const [reload, setReload] = useState(0);
  const requests = useRef(new Map<string, string>());
  function requestFor(payload: unknown) {
    const key = JSON.stringify(payload);
    if (!requests.current.has(key))
      requests.current.set(key, crypto.randomUUID());
    return requests.current.get(key)!;
  }
  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    api<{ dashboards: Dashboard[] }>("/dashboards")
      .then((result) => {
        if (!cancelled) {
          setBoards(result.dashboards);
          setLoading(false);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e.message);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [open, reload]);
  async function create() {
    setBusy(true);
    setError("");
    const payload = { name: name.trim(), description: "" };
    try {
      const result = await api<DashboardMutation>("/dashboards", {
        method: "POST",
        body: JSON.stringify({
          ...payload,
          request_id: requestFor(["create", payload]),
        }),
      });
      setBoards((old) => [
        ...old.filter((b) => b.id !== result.dashboard.id),
        result.dashboard,
      ]);
      requests.current.delete(JSON.stringify(["create", payload]));
      setSelected(result.dashboard.id);
      setCreating(false);
      setName("");
      setQuery("");
      toast.success("Dashboard created", {
        description: "Choose Pin saved result to add this chart.",
      });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function pin() {
    const board = boards.find((b) => b.id === selected);
    if (!board || !capture.ready) return;
    const payload = {
      artifact_id: artifact.id,
      view: capture.state,
      title,
      expected_revision: board.revision,
    };
    setBusy(true);
    setError("");
    setDuplicate(false);
    try {
      await api<DashboardMutation>(`/dashboards/${selected}/items`, {
        method: "POST",
        body: JSON.stringify({
          ...payload,
          request_id: requestFor([selected, payload]),
        }),
      });
      toast.success("Pinned to dashboard", {
        description: board.name,
        action: {
          label: "Open dashboard",
          onClick: () => {
            router.push(`/dashboards/${selected}`);
          },
        },
      });
      setOpen(false);
      requests.current.clear();
    } catch (e) {
      setError((e as Error).message);
      setDuplicate(
        e instanceof ApiError && e.code === "dashboard_already_pinned",
      );
    } finally {
      setBusy(false);
    }
  }
  const board = boards.find((b) => b.id === selected);
  return (
    <>
      <Button
        variant="outline"
        size="sm"
        disabled={!capture.ready}
        title={
          !capture.ready
            ? "Wait for the current saved view to finish loading"
            : undefined
        }
        onClick={() => {
          setLoading(true);
          setError("");
          setDuplicate(false);
          setOpen(true);
        }}
      >
        <Pin data-icon="inline-start" />
        Pin to dashboard
      </Button>
      <Dialog
        open={open}
        onOpenChange={(value) => {
          if (!busy) {
            if (
              !value &&
              (name.trim() || title !== artifact.title) &&
              !window.confirm("Discard the unsaved pin details?")
            )
              return;
            setOpen(value);
          }
        }}
      >
        <DialogContent className="dashboard-dialog">
          <DialogHeader>
            <DialogTitle>Pin saved result</DialogTitle>
            <DialogDescription>
              Public — anyone can view and edit. Pinning runs no new query.
            </DialogDescription>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            {describeChartView(capture.state)} ·{" "}
            {artifact.complete
              ? "Complete saved result"
              : "Partial result — warning will remain visible"}
          </p>
          {error && (
            <Alert variant="destructive">
              <AlertTitle>Could not pin this result</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setLoading(true);
                  setReload((r) => r + 1);
                }}
              >
                Reload latest dashboards
              </Button>
              {duplicate && (
                <Button asChild variant="outline" size="sm">
                  <Link href={`/dashboards/${selected}`}>
                    Open card and update its saved view
                  </Link>
                </Button>
              )}
            </Alert>
          )}
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="pin-card-title">Card title</FieldLabel>
              <Input
                id="pin-card-title"
                maxLength={160}
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="pin-dashboard-search">
                Find a dashboard
              </FieldLabel>
              <Input
                id="pin-dashboard-search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search names or descriptions"
              />
            </Field>
            {loading ? (
              <p role="status">Loading dashboards…</p>
            ) : (
              <Field>
                <FieldLabel htmlFor="pin-dashboard">Dashboard</FieldLabel>
                <AppSelect
                  id="pin-dashboard"
                  className="dashboard-native-select"
                  value={selected}
                  onValueChange={(selectedValue) => {
                    setSelected(selectedValue);
                    setError("");
                    setDuplicate(false);
                  }}
                >
                  <AppSelectItem value="">Choose a dashboard…</AppSelectItem>
                  {boards
                    .filter((b) =>
                      `${b.name} ${b.description}`
                        .toLowerCase()
                        .includes(query.toLowerCase()),
                    )
                    .map((b) => (
                      <AppSelectItem key={b.id} value={String(b.id)}>
                        {b.name} · {b.card_count}{" "}
                        {b.card_count === 1 ? "card" : "cards"}
                        {boards.filter((other) => other.name === b.name)
                          .length > 1
                          ? ` · ${b.id.slice(0, 6)}`
                          : ""}
                      </AppSelectItem>
                    ))}
                </AppSelect>
                {!boards.length && (
                  <p>
                    Create your first dashboard below. It will be visible to
                    everyone.
                  </p>
                )}
              </Field>
            )}
            {creating && (
              <Field>
                <FieldLabel htmlFor="pin-new-dashboard">
                  New dashboard name
                </FieldLabel>
                <Input
                  autoFocus
                  id="pin-new-dashboard"
                  maxLength={80}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
                <Button
                  variant="outline"
                  disabled={busy || !name.trim()}
                  onClick={() => void create()}
                >
                  Create dashboard
                </Button>
              </Field>
            )}
          </FieldGroup>
          <DialogFooter>
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => setCreating(!creating)}
            >
              <Plus data-icon="inline-start" />
              {creating ? "Cancel new dashboard" : "Create new dashboard"}
            </Button>
            <Button
              disabled={busy || !board || !capture.ready || duplicate}
              onClick={() => void pin()}
            >
              {busy ? "Saving…" : "Pin saved result"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
