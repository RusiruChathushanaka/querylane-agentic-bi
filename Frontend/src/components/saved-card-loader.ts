import { savedResult } from "@/lib/saved-result-loader";
import type { Artifact } from "@/lib/types";

let prepared: Promise<typeof import("./result-card")> | undefined;
export let ReadyResultCard: typeof import("./result-card").default | undefined;

export function preparedResultCard() {
  return ReadyResultCard;
}

/** Called only after viewport admission; code and saved evidence load independently. */
export function loadSavedCard(path: string, signal?: AbortSignal): Promise<Artifact> {
  // Keep the ordinary dynamic component's failure/retry path authoritative.
  const current = prepared ??= import("./result-card").then(value => { ReadyResultCard = value.default; return value; });
  void current.catch(() => { if (prepared === current) prepared = undefined; });
  return savedResult<Artifact>(path, signal);
}
