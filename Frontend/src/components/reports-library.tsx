"use client";
import { useReadResource } from "@/hooks/use-read-resource";
import { ResourceFeedback } from "./resource-feedback";

import { AppSelect, AppSelectItem } from "@/components/ui/app-select";
import Link from "@/components/ui/app-link";
import { workspacePath } from "@/lib/workspace-links";
import { useState } from "react";
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
  const [sort, setSort] = useState("updated");

  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const [tick, setTick] = useState(0);
  const resource = useReadResource(`reports:${deleted}:${tick}`, (signal) => api<{ reports: Report[] }>(`/reports?deleted=${deleted}`, { signal }), (v) => { setReports(v.reports); setError(""); }, 5000);
  const loading = !resource.loaded && resource.pending;
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
        <ResourceFeedback resource={resource} label="Loading public reports" />
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
            <Link href={workspacePath()}>
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
        <div className="report-library-overview" aria-label="Reports overview">
          <div>
            <strong>{resource.loaded ? reports.length : "…"}</strong>
            <span>{deleted ? "Recoverable reports" : "Public reports"}</span>
          </div>
          <div>
            <strong>
              {resource.loaded ? reports.filter((report) => report.status === "complete").length : "…"}
            </strong>
            <span>Ready to read</span>
          </div>
          <div>
            <strong>
              {
                resource.loaded ? reports.filter((report) =>
                  ["running", "queued", "waiting_input"].includes(
                    report.status,
                  ),
                ).length : "…"
              }
            </strong>
            <span>In progress / awaiting input</span>
          </div>
        </div>
        <div className="report-filter">
          <Input
            aria-label="Search public reports"
            placeholder="Find a report…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <AppSelect
            aria-label="Filter report status"
            value={filter}
            onValueChange={(selectedValue) => setFilter(selectedValue)}
          >
            <AppSelectItem value="all">All statuses</AppSelectItem>
            <AppSelectItem value="complete">Ready</AppSelectItem>
            <AppSelectItem value="running">Analyzing</AppSelectItem>
            <AppSelectItem value="queued">Queued</AppSelectItem>
            <AppSelectItem value="waiting_input">
              Needs information
            </AppSelectItem>
            <AppSelectItem value="failed">Failed</AppSelectItem>
            <AppSelectItem value="cancelled">Cancelled</AppSelectItem>
          </AppSelect>
          <AppSelect
            aria-label="Sort reports"
            value={sort}
            onValueChange={(selectedValue) => setSort(selectedValue)}
          >
            <AppSelectItem value="updated">Recently updated</AppSelectItem>
            <AppSelectItem value="name">Name A–Z</AppSelectItem>
            <AppSelectItem value="created">Newest created</AppSelectItem>
          </AppSelect>
          <Button
            variant={deleted ? "secondary" : "outline"}
            onClick={() => {
              setDeleted((v) => !v);

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
            {[...shown]
              .sort((a, b) =>
                sort === "name"
                  ? a.name.localeCompare(b.name)
                  : Date.parse(
                      sort === "created" ? b.created_at : b.updated_at,
                    ) -
                    Date.parse(
                      sort === "created" ? a.created_at : a.updated_at,
                    ),
              )
              .map((report) => (
                <Reveal key={report.id} className="report-library-card">
                  <div className="report-icon">
                    <FileChartColumn aria-hidden />
                    <Badge variant="outline">
                      {
                        {
                          complete: "Ready",
                          running: "Analyzing",
                          queued: "Queued",
                          waiting_input: "Needs information",
                          failed: "Failed",
                          cancelled: "Cancelled",
                        }[report.status]
                      }
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
                  <div className="report-actions report-library-actions">
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
          !error && resource.loaded && (
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
                <Link href={workspacePath()}>Ask an advanced question</Link>
              </Button>
            </div>
          )
        )}
      </main>
    </div>
  );
}
