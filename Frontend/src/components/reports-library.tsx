"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  ArrowUpRight,
  FileChartColumn,
  Plus,
  RefreshCw,
  RotateCcw,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { Report } from "@/lib/report-types";
import { DashboardHeader } from "@/components/dashboard-shared";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Reveal } from "@/components/motion/reveal";

export function ReportsLibrary() {
  const [reports, setReports] = useState<Report[]>([]);
  const [deleted, setDeleted] = useState(false);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const [tick, setTick] = useState(0);
  const load = useCallback(
    async (signal?: AbortSignal) => {
      try {
        const result = await api<{ reports: Report[] }>(
          `/reports?deleted=${deleted}`,
          { signal },
        );
        if (!signal?.aborted) {
          setReports(result.reports);
          setError("");
        }
      } catch (e) {
        if (!signal?.aborted) setError((e as Error).message);
      } finally {
        if (!signal?.aborted) setLoading(false);
      }
    },
    [deleted],
  );
  useEffect(() => {
    const controller = new AbortController();
    void Promise.resolve().then(() => {
      if (!controller.signal.aborted) return load(controller.signal);
    });
    const interval = setInterval(() => {
      if (!document.hidden)
        void Promise.resolve().then(() => {
          if (!controller.signal.aborted) return load(controller.signal);
        });
    }, 5000);
    return () => {
      controller.abort();
      clearInterval(interval);
    };
  }, [load, tick]);
  async function restore(report: Report) {
    const result = await api<Report>(`/reports/${report.id}/restore`, {
      method: "POST",
      body: JSON.stringify({ expected_revision: report.revision }),
    });
    toast.success("Report restored");
    setTick((v) => v + 1);
    return result;
  }
  async function change(report: Report) {
    if (
      !deleted &&
      !window.confirm(
        `Delete “${report.name}” from the public library? Anyone can restore it for 30 days.`,
      )
    )
      return;
    setBusy(report.id);
    try {
      if (deleted) await restore(report);
      else {
        const result = await api<Report>(
          `/reports/${report.id}?expected_revision=${report.revision}`,
          { method: "DELETE" },
        );
        toast.success("Report moved to Recently deleted", {
          action: {
            label: "Undo",
            onClick: () => {
              void restore(result).catch((e) => toast.error(e.message));
            },
          },
          duration: 8000,
        });
        setTick((v) => v + 1);
      }
    } catch (e) {
      toast.error((e as Error).message);
      setTick((v) => v + 1);
    } finally {
      setBusy("");
    }
  }
  const shown = reports.filter(
    (r) =>
      r.name.toLowerCase().includes(query.toLowerCase()) &&
      (filter === "all" || r.status === filter),
  );
  return (
    <div className="reports-page">
      <a className="skip-link" href="#report-content">
        Skip to reports
      </a>
      <DashboardHeader />
      <main className="reports-main" id="report-content" tabIndex={-1}>
        <div className="reports-hero">
          <div>
            <div className="reports-eyebrow">A deeper understanding</div>
            <h1>
              Reports library<span>.</span>
            </h1>
            <p>
              Detailed analysis, backed by saved evidence. Explore findings,
              validated predictions, and the assumptions behind them. Every
              report is public.
            </p>
          </div>
          <Button asChild>
            <Link href="/">
              <Plus aria-hidden />
              Create in workspace
            </Link>
          </Button>
        </div>
        <div className="report-note">
          Everyone can view, download, rename, delete, and restore completed
          reports. Versions preserve their original evidence. Opening a report
          runs no new queries.
        </div>
        <div className="report-filter">
          <Input
            aria-label="Search public reports"
            placeholder="Find a report…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <select
            aria-label="Filter report status"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All statuses</option>
            <option value="complete">Ready</option>
            <option value="running">Analyzing</option>
            <option value="queued">Queued</option>
            <option value="waiting_input">Needs information</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <Button
            variant={deleted ? "secondary" : "outline"}
            onClick={() => {
              setDeleted((v) => !v);
              setLoading(true);
            }}
          >
            {deleted ? "Active reports" : "Recently deleted"}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Refresh reports"
            onClick={() => setTick((v) => v + 1)}
          >
            <RefreshCw />
          </Button>
        </div>
        {error && (
          <div role="alert" className="report-note">
            <p>{error}</p>
            <Button variant="outline" onClick={() => setTick((v) => v + 1)}>
              Try again
            </Button>
          </div>
        )}
        {loading ? (
          <div className="report-grid">
            {[0, 1, 2].map((i) => (
              <Skeleton key={i} className="h-56 rounded-2xl" />
            ))}
          </div>
        ) : shown.length ? (
          <div className="report-grid">
            {shown.map((report) => (
              <Reveal key={report.id} className="report-library-card">
                <div className="report-icon">
                  <FileChartColumn aria-hidden />
                  <Badge variant="outline">
                    {report.status.replaceAll("_", " ")}
                  </Badge>
                </div>
                <h2>
                  <Link href={`/reports/${report.id}`}>{report.name}</Link>
                </h2>
                <p>
                  {report.versions.length} saved{" "}
                  {report.versions.length === 1 ? "version" : "versions"} ·
                  Public
                </p>
                <time dateTime={report.updated_at}>
                  Updated {new Date(report.updated_at).toLocaleString()}
                </time>
                <div className="report-actions">
                  <Button asChild variant="outline" size="sm">
                    <Link href={`/reports/${report.id}`}>
                      Open
                      <ArrowUpRight aria-hidden />
                    </Link>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={
                      busy === report.id ||
                      ["queued", "running", "waiting_input"].includes(
                        report.status,
                      )
                    }
                    onClick={() => void change(report)}
                  >
                    {deleted ? (
                      <RotateCcw aria-hidden />
                    ) : (
                      <Trash2 aria-hidden />
                    )}
                    {deleted ? "Restore" : "Delete"}
                  </Button>
                </div>
              </Reveal>
            ))}
          </div>
        ) : (
          !error && (
            <div className="report-empty">
              <FileChartColumn className="mx-auto mb-4" aria-hidden />
              <h2>
                {query || filter !== "all"
                  ? "No matching reports"
                  : deleted
                    ? "No recently deleted reports"
                    : "Your next question deserves a report"}
              </h2>
              <p>
                Enable Advanced Analysis in the workspace, choose a report
                style, and ask a business question. The report appears here
                while you continue chatting.
              </p>
              <Button asChild>
                <Link href="/">Ask an advanced question</Link>
              </Button>
            </div>
          )
        )}
      </main>
    </div>
  );
}
