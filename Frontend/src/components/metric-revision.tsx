"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { MetricDefinition } from "@/lib/planning-types";
import { DashboardHeader } from "./dashboard-shared";

export function MetricRevision({
  id,
  version,
}: {
  id: string;
  version: number;
}) {
  const [saved, setSaved] = useState<{
    definition: MetricDefinition;
    version: number;
    dependencies: unknown;
  } | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    void api<NonNullable<typeof saved>>(`/metrics/${id}/revisions/${version}`, {
      signal: controller.signal,
    })
      .then(setSaved)
      .catch((e) => {
        if (!controller.signal.aborted) setError(e.message);
      });
    return () => controller.abort();
  }, [id, version]);
  return (
    <>
      <DashboardHeader />
      <main className="bi-main">
        <Link href="/metrics" className="underline">
          Metrics library
        </Link>
        {error && (
          <p className="bi-error" role="alert">
            {error}
          </p>
        )}
        {saved ? (
          <>
            <header className="bi-hero">
              <div>
                <span className="bi-kicker">
                  Immutable published shared definition
                </span>
                <h1>{saved.definition.name}</h1>
                <p>
                  Version {saved.version}. Editing or archiving the current
                  metric cannot change this evidence.
                </p>
              </div>
            </header>
            <p>{saved.definition.description}</p>
            <p className="bi-note">
              {saved.definition.time_basis} · {saved.definition.unit} ·{" "}
              {saved.definition.dimensions.join(", ")}
            </p>
            <pre
              className="bi-code"
              tabIndex={0}
              role="region"
              aria-label="Immutable metric revision details"
            >
              {JSON.stringify(saved, null, 2)}
            </pre>
            <Link href={`/metrics/${id}`} className="underline">
              Open current draft and publication history
            </Link>
          </>
        ) : (
          !error && <p role="status">Loading saved definition…</p>
        )}
      </main>
    </>
  );
}
