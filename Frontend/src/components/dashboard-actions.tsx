"use client";

import { useEffect, useRef, useState } from "react";
import { Download, Share2, Copy, LoaderCircle } from "lucide-react";
import { toast } from "sonner";
import { api, backendUrl } from "@/lib/api";
import { downloadBlob } from "@/lib/chart-export";
import { dashboardShareUrl } from "@/lib/dashboard-links";
import type { Dashboard } from "@/lib/dashboard-types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

export function DashboardShare({
  dashboard,
  compact = false,
}: {
  dashboard: Dashboard;
  compact?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const input = useRef<HTMLInputElement>(null);
  function show() {
    setUrl(dashboardShareUrl(location.origin, dashboard.id));
    setError("");
    setOpen(true);
  }
  async function copy() {
    try {
      if (!navigator.clipboard?.writeText)
        throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(url);
      toast.success("Dashboard link copied");
    } catch {
      input.current?.focus();
      input.current?.select();
      setError(
        "Automatic copying is unavailable. Copy the selected link with your keyboard or touch menu.",
      );
    }
  }
  return (
    <>
      <Button
        variant="outline"
        size={compact ? "sm" : "default"}
        aria-label={`Share ${dashboard.name}`}
        onClick={show}
      >
        <Share2 data-icon="inline-start" />
        Share
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="dashboard-dialog">
          <DialogHeader>
            <DialogTitle>Share dashboard</DialogTitle>
            <DialogDescription>
              Anyone with this link can view this public dashboard. Everyone can
              switch to edit mode. The link opens the latest saved dashboard in
              view mode.
            </DialogDescription>
          </DialogHeader>
          <label htmlFor={`share-${dashboard.id}`}>Public dashboard link</label>
          <Input
            ref={input}
            id={`share-${dashboard.id}`}
            value={url}
            readOnly
            onFocus={(e) => e.currentTarget.select()}
          />
          {error && <p role="status">{error}</p>}
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Close
            </Button>
            <Button variant="outline" onClick={() => void copy()}>
              <Copy data-icon="inline-start" />
              Copy link
            </Button>
            {typeof navigator !== "undefined" &&
              typeof navigator.share === "function" && (
                <Button
                  onClick={async () => {
                    try {
                      await navigator.share({
                        title: dashboard.name,
                        text: "Explore this public Querylane dashboard",
                        url,
                      });
                    } catch (e) {
                      if ((e as Error).name !== "AbortError")
                        setError(
                          "Device sharing is unavailable. Copy the public link instead.",
                        );
                    }
                  }}
                >
                  <Share2 data-icon="inline-start" />
                  Share with device
                </Button>
              )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

const formats = [
  {
    id: "png",
    label: "PNG image",
    description: "Full saved dashboard layout, with all cards and scope notes.",
    extension: "png",
  },
  {
    id: "jpeg",
    label: "JPEG image",
    description: "A smaller image for presentations and messages.",
    extension: "jpg",
  },
  {
    id: "pdf",
    label: "PDF document",
    description:
      "Paginated cards with source timestamps and completeness notes.",
    extension: "pdf",
  },
  {
    id: "data",
    label: "CSV data (ZIP)",
    description:
      "All saved rows for every card, plus a provenance manifest. Visual date filters do not trim the CSVs.",
    extension: "zip",
  },
  {
    id: "json",
    label: "JSON snapshot",
    description:
      "Dashboard layout, saved views and evidence metadata. Does not include data rows or create an importable backup.",
    extension: "json",
  },
];

export function DashboardDownload({
  dashboard,
  compact = false,
}: {
  dashboard: Dashboard;
  compact?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [snapshot, setSnapshot] = useState<Dashboard | null>(null);
  const [format, setFormat] = useState("png");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const controller = useRef<AbortController | null>(null);
  useEffect(() => () => controller.current?.abort(), []);
  async function prepare() {
    setOpen(true);
    setSnapshot(null);
    setError("");
    controller.current?.abort();
    const abort = new AbortController();
    controller.current = abort;
    try {
      const value = await api<Dashboard>(`/dashboards/${dashboard.id}`, {
        signal: abort.signal,
      });
      if (!value.items)
        throw new Error("Dashboard cards could not be loaded. Try again.");
      setSnapshot(value);
    } catch (e) {
      if (!abort.signal.aborted) setError((e as Error).message);
    }
  }
  function close(next: boolean) {
    if (!next) {
      controller.current?.abort();
      setBusy(false);
    }
    setOpen(next);
  }
  async function download() {
    if (!snapshot) return;
    const abort = new AbortController();
    controller.current = abort;
    setBusy(true);
    setError("");
    try {
      const response = await fetch(
        `${await backendUrl()}/api/v1/dashboards/${snapshot.id}/downloads/${format}?expected_revision=${snapshot.revision}`,
        { signal: abort.signal, cache: "no-store" },
      );
      if (!response.ok) {
        const body = await response.json();
        throw new Error(
          body.error?.message ?? "Dashboard download failed. Try again.",
        );
      }
      const blob = await response.blob();
      if (abort.signal.aborted) return;
      downloadBlob(
        blob,
        `querylane-dashboard-${snapshot.id}-r${snapshot.revision}.${formats.find((f) => f.id === format)!.extension}`,
      );
      toast.success("Dashboard download ready", {
        description: `${snapshot.name} · Revision ${snapshot.revision} · ${snapshot.card_count} saved cards`,
      });
    } catch (e) {
      if (!abort.signal.aborted) {
        setError((e as Error).message);
        toast.error("Could not download dashboard", {
          description: (e as Error).message,
        });
      }
    } finally {
      if (!abort.signal.aborted) setBusy(false);
    }
  }
  return (
    <>
      <Button
        variant="outline"
        size={compact ? "sm" : "default"}
        aria-label={`Download ${dashboard.name}`}
        onClick={() => void prepare()}
      >
        <Download data-icon="inline-start" />
        Download
      </Button>
      <Dialog open={open} onOpenChange={close}>
        <DialogContent className="dashboard-dialog dashboard-download-dialog">
          <DialogHeader>
            <DialogTitle>Download dashboard</DialogTitle>
            <DialogDescription>
              Export the published saved views, including cards you have not
              scrolled to. Temporary chart exploration and unsaved edits are
              excluded. No source queries or AI calls run.
            </DialogDescription>
          </DialogHeader>
          <div className="dashboard-download-body">
            {snapshot ? (
              <>
                <p>
                  <strong>{snapshot.name}</strong> · Revision{" "}
                  {snapshot.revision} · {snapshot.card_count}{" "}
                  {snapshot.card_count === 1 ? "card" : "cards"}
                </p>
                {snapshot.items?.some((item) => !item.summary.complete) && (
                  <p className="dash-export-warning">
                    Contains partial source results. Exports preserve these
                    limitations.
                  </p>
                )}
                <fieldset className="dashboard-export-formats" disabled={busy}>
                  <legend>Download format</legend>
                  {formats.map((option) => (
                    <label key={option.id}>
                      <input
                        type="radio"
                        name={`dashboard-format-${dashboard.id}`}
                        value={option.id}
                        checked={format === option.id}
                        onChange={() => setFormat(option.id)}
                      />
                      <span>
                        <strong>{option.label}</strong>
                        <small>{option.description}</small>
                      </span>
                    </label>
                  ))}
                </fieldset>
                <p className="dash-footnote">
                  Images and PDF use a print-friendly light palette and table
                  previews of up to 20 rows and 8 columns. Mixed units use
                  separate plots. CSV ZIP contains full saved results. Each card
                  retains its independent query timestamp; this is not a live
                  synchronized database snapshot.
                </p>
              </>
            ) : (
              !error && <p>Loading saved dashboard details…</p>
            )}
            {error && <p role="alert">{error}</p>}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => close(false)}>
              {busy ? "Cancel download" : "Close"}
            </Button>
            {error && (
              <Button
                variant="outline"
                disabled={busy}
                onClick={() => void prepare()}
              >
                Reload saved dashboard
              </Button>
            )}
            <Button
              disabled={!snapshot || busy || snapshot.deleted}
              onClick={() => void download()}
            >
              {busy ? (
                <LoaderCircle
                  className="animate-spin motion-reduce:animate-none"
                  data-icon="inline-start"
                />
              ) : (
                <Download data-icon="inline-start" />
              )}
              {busy ? "Preparing download…" : "Download file"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
