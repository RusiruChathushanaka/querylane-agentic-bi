"use client";

import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { useAppMotion } from "@/hooks/use-app-motion";
import { Skeleton } from "./ui/skeleton";

type Resource = { pending: boolean; loaded: boolean; error: string; retryAt?: number; refresh: () => unknown };
export function ResourceFeedback({ resource, label, skeleton = false }: { resource: Resource; label: string; skeleton?: boolean }) {
  const { reduced } = useAppMotion();
  const [slow, setSlow] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!resource.pending) return;
    const timer = setTimeout(() => setSlow(true), 5000);
    return () => { clearTimeout(timer); setSlow(false); };
  }, [resource.pending]);
  useEffect(() => {
    if (!resource.retryAt) return;
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [resource.retryAt]);
  if (resource.loaded && !resource.error) return null;
  const wait = Math.max(0, Math.ceil(((resource.retryAt ?? 0) - now) / 1000));
  return <section className="resource-feedback" aria-label={label}>
    <p role="status" aria-live="polite">{resource.error
      ? `${label.startsWith("Connecting") ? "Could not connect to Querylane" : `${resource.loaded ? "Could not refresh" : "Could not load"} ${label.replace(/^Loading /, "").toLowerCase()}`}. ${resource.error}`
      : `${label}…`}
      {resource.pending && slow && <span className="resource-feedback-note block">This is taking longer than usual. The service may be starting.</span>}
    </p>
    {resource.error && <Button type="button" variant="outline" size="sm" disabled={resource.pending || wait > 0} onClick={() => resource.refresh()}>{wait > 0 ? `Retry in ${wait}s` : "Retry"}</Button>}
    {skeleton && resource.pending && !resource.loaded && <div aria-hidden="true" aria-busy={resource.pending} className={`resource-skeletons${reduced ? " resource-no-motion" : ""}`}><Skeleton className="h-5 w-3/4" /><Skeleton className="h-5 w-full" /><Skeleton className="h-5 w-2/3" /></div>}
  </section>;
}
