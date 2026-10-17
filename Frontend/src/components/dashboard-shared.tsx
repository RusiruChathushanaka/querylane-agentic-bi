"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  ArrowLeft,
  FileChartColumn,
  BookOpen,
  LayoutDashboard,
  Settings2,
} from "lucide-react";
import { api } from "@/lib/api";
import type { Dashboard, DashboardMutation } from "@/lib/dashboard-types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { toast } from "sonner";

export function DashboardHeader() {
  return (
    <header className="dash-header">
      <Link className="dash-brand" href="/">
        Querylane<span>.</span>
      </Link>
      <nav aria-label="Application">
        <Button asChild variant="ghost" size="sm">
          <Link href="/">
            <ArrowLeft data-icon="inline-start" />
            Workspace
          </Link>
        </Button>
        <Button asChild variant="ghost" size="sm">
          <Link href="/dashboards">
            <LayoutDashboard data-icon="inline-start" />
            Dashboards
          </Link>
        </Button>
        <Button asChild variant="ghost" size="sm">
          <Link href="/reports">
            <FileChartColumn data-icon="inline-start" />
            Reports
          </Link>
        </Button>
        <Button asChild variant="ghost" size="sm">
          <Link href="/skills">
            <BookOpen data-icon="inline-start" />
            Skills
          </Link>
        </Button>
        <Button asChild variant="ghost" size="sm">
          <Link href="/settings">
            <Settings2 data-icon="inline-start" />
            Settings
          </Link>
        </Button>
      </nav>
    </header>
  );
}
export function useDashboardMutation() {
  const requests = useRef(new Map<string, string>());
  return async (
    path: string,
    method: string,
    payload: Record<string, unknown>,
  ) => {
    const key = JSON.stringify([path, method, payload]);
    if (!requests.current.has(key))
      requests.current.set(key, crypto.randomUUID());
    const requestId = requests.current.get(key)!;
    const result = await api<DashboardMutation>(
      method === "DELETE"
        ? `${path}?expected_revision=${payload.expected_revision}&request_id=${requestId}`
        : path,
      {
        method,
        ...(method !== "DELETE"
          ? { body: JSON.stringify({ ...payload, request_id: requestId }) }
          : {}),
      },
    );
    requests.current.delete(key);
    return result;
  };
}
export function DashboardEditor({
  dashboard,
  onClose,
  onSaved,
}: {
  dashboard?: Dashboard;
  onClose: () => void;
  onSaved: (board: Dashboard) => void;
}) {
  const [name, setName] = useState(dashboard?.name ?? "");
  const [description, setDescription] = useState(dashboard?.description ?? "");
  const [latest, setLatest] = useState(dashboard);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const send = useDashboardMutation();
  const dirty =
    name !== (dashboard?.name ?? "") ||
    description !== (dashboard?.description ?? "");
  useEffect(() => {
    if (!dirty) return;
    const guard = (event: BeforeUnloadEvent) => {
      event.preventDefault();
    };
    window.addEventListener("beforeunload", guard);
    return () => window.removeEventListener("beforeunload", guard);
  }, [dirty]);
  function close() {
    if (
      !busy &&
      (!dirty || window.confirm("Discard unsaved dashboard details?"))
    )
      onClose();
  }
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await send(
        latest ? `/dashboards/${latest.id}` : "/dashboards",
        latest ? "PATCH" : "POST",
        {
          name: name.trim(),
          description,
          ...(latest ? { expected_revision: latest.revision } : {}),
        },
      );
      toast.success(latest ? "Dashboard updated" : "Public dashboard created");
      onSaved(result.dashboard);
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
      <DialogContent className="dashboard-dialog">
        <DialogHeader>
          <DialogTitle>
            {dashboard ? "Edit dashboard details" : "Create dashboard"}
          </DialogTitle>
          <DialogDescription>
            Public — anyone can view and edit. Save charts here after asking a
            question.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={save}>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="dashboard-name">Name</FieldLabel>
              <Input
                autoFocus
                required
                id="dashboard-name"
                maxLength={80}
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="dashboard-description">
                Description
              </FieldLabel>
              <Textarea
                id="dashboard-description"
                maxLength={500}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </Field>
          </FieldGroup>
          {error && (
            <Alert variant="destructive">
              <AlertTitle>Could not save dashboard</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
              {dashboard && (
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={async () => {
                    try {
                      const board = await api<Dashboard>(
                        `/dashboards/${dashboard.id}`,
                      );
                      setLatest(board);
                      setError(
                        `Latest revision loaded (${board.name}). Your draft is preserved; review it before saving.`,
                      );
                    } catch (e) {
                      setError((e as Error).message);
                    }
                  }}
                >
                  Reload latest revision
                </Button>
              )}
            </Alert>
          )}
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              disabled={busy}
              onClick={close}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={busy || !name.trim()}>
              {busy ? "Saving…" : "Save dashboard"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
