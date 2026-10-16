import { api } from "./api";

// Shared saved-result reads only: bounded and deduplicated, with subscriber-aware aborts.
let active = 0;
const waiting: (() => void)[] = [];
const pending = new Map<
  string,
  { promise: Promise<unknown>; controller: AbortController; users: number }
>();
async function queued<T>(run: () => Promise<T>) {
  if (active >= 2) await new Promise<void>((resolve) => waiting.push(resolve));
  else active++;
  try {
    return await run();
  } finally {
    const next = waiting.shift();
    if (next) next();
    else active--;
  }
}
export function savedResult<T>(path: string, signal?: AbortSignal): Promise<T> {
  if (signal?.aborted)
    return Promise.reject(new DOMException("Aborted", "AbortError"));
  let entry = pending.get(path);
  if (!entry) {
    const controller = new AbortController();
    entry = {
      controller,
      users: 0,
      promise: queued(() => api<T>(path, { signal: controller.signal })),
    };
    pending.set(path, entry);
    const captured = entry;
    void entry.promise
      .finally(() => {
        if (pending.get(path) === captured) pending.delete(path);
      })
      .catch(() => {});
  }
  const current = entry;
  current.users++;
  let abort: (() => void) | undefined;
  const cancelled = new Promise<never>((_, reject) => {
    abort = () => reject(new DOMException("Aborted", "AbortError"));
    signal?.addEventListener("abort", abort, { once: true });
  });
  return Promise.race([current.promise as Promise<T>, cancelled]).finally(
    () => {
      if (abort) signal?.removeEventListener("abort", abort);
      if (--current.users === 0) {
        current.controller.abort();
        if (pending.get(path) === current) pending.delete(path);
      }
    },
  );
}
