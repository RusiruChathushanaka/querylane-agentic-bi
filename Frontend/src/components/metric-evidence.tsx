import Link from "@/components/ui/app-link";
import type { Artifact } from "@/lib/types";

export function MetricEvidence({
  metrics,
}: {
  metrics: NonNullable<Artifact["metric_snapshots"]>;
}) {
  if (!metrics.length) return null;
  return (
    <details className="report-note">
      <summary>Business metrics used · saved definitions</summary>
      <p>
        Published shared definitions; versions remain unchanged when visitors
        edit the catalog.
      </p>
      <ul>
        {metrics.map((m) => (
          <li key={`${m.id}:${m.version}`}>
            <Link
              className="underline"
              href={`/metrics/${m.id}/revisions/${m.version}`}
            >
              {m.definition.name} · v{m.version}
            </Link>
            <p>{m.definition.description}</p>
          </li>
        ))}
      </ul>
    </details>
  );
}
