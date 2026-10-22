import type { StreamEvent } from "./types";
import { loadingMark, loadingMeasure } from "./loading-performance";

let bootstrapUrl: string | undefined;
const validatedReads = new Map<string, { etag: string; value: unknown; bytes: number }>();
let validatedBytes = 0;

let basePromise: Promise<string> | undefined;
let guestPromise: Promise<string> | undefined;
let guestCache: { token: string; expires: number } | undefined;

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public retryAfter?: number,
    public retryableRead = true,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Bound JSON requests, including body reads; caller cancellation always wins. */
async function jsonRequest(url: string, init: RequestInit = {}) {
  const started = typeof performance !== "undefined" ? performance.now() : 0;
  const controller = new AbortController();
  const abort = () => controller.abort(init.signal?.reason);
  if (init.signal?.aborted) abort();
  else init.signal?.addEventListener("abort", abort, { once: true });
  let timedOut = false;
  const timer = setTimeout(() => { timedOut = true; controller.abort(); }, 30000);
  try {
    const response = await fetch(url, { ...init, signal: controller.signal });
    if (response.status === 304) return { response, body: undefined };
    let body;
    try { body = await response.json(); }
    catch (error) {
      if (controller.signal.aborted) throw error;
      if (response.ok) throw new ApiError("The service returned an invalid response. Try again.", 502, "invalid_response");
      body = {};
    }
    return { response, body };
  } catch (error) {
    if (init.signal?.aborted) throw error;
    if (timedOut) throw new ApiError("The request timed out. Check saved history before retrying a change.", 504, "request_timeout", undefined, (init.method ?? "GET").toUpperCase() === "GET");
    if (error instanceof ApiError) throw error;
    throw new ApiError("The service connection was interrupted. Check saved history before retrying a change.", 0, "connection_failed", undefined, (init.method ?? "GET").toUpperCase() === "GET");
  } finally {
    const route = url.replace(/^https?:\/\/[^/]+/, "").split("?")[0].replace(/\/[a-f0-9]{32}(?=\/|$)/g, "/:id");
    loadingMeasure(`read:${route}`, started);
    clearTimeout(timer);
    init.signal?.removeEventListener("abort", abort);
  }
}

/** Installed before descendant read effects, from request-time application layouts only. */
export function configureBackend(value: string) {
  if (!/^https?:\/\/[^\s]+$/.test(value)) return false;
  try {
    const url = new URL(value);
    if (url.username || url.password || url.search || url.hash) return false;
  } catch { return false; }
  bootstrapUrl = value.replace(/\/$/, "");
  basePromise = Promise.resolve(bootstrapUrl);
  loadingMark("runtime-config-ready");
  return true;
}

export function backendUrl(): Promise<string> {
  if (bootstrapUrl) return Promise.resolve(bootstrapUrl);
  basePromise ??= jsonRequest("/api/config", { cache: "no-store" })
    .then(({ response, body }) => {
      if (!response.ok || typeof body?.backend_url !== "string" || !/^https?:\/\/[^\s]+$/.test(body.backend_url))
        throw new ApiError("Application configuration is unavailable.", response.status, "configuration_unavailable");
      return body.backend_url.replace(/\/$/, "") as string;
    })
    .catch((error) => { basePromise = undefined; throw error; });
  return basePromise;
}

function forgetGuest(rejectedToken?: string) {
  // A second stale 401 must not evict credentials another request just refreshed.
  if (rejectedToken && guestCache && guestCache.token !== rejectedToken) return;
  guestCache = undefined;
  try { sessionStorage.removeItem("bi-guest"); } catch { /* In-memory credentials still work. */ }
}

export async function guestToken(): Promise<string> {
  if (guestCache && guestCache.expires > Date.now()) return guestCache.token;
  try {
    const cached = sessionStorage.getItem("bi-guest");
    if (cached) {
      const parsed = JSON.parse(cached);
      if (typeof parsed?.token === "string" && parsed.token && Number.isFinite(parsed.expires) && parsed.expires > Date.now()) {
        guestCache = parsed;
        return parsed.token;
      }
    }
  } catch { /* Corrupt/blocked session storage must not disable the application. */ }
  forgetGuest();
  guestPromise ??= (async () => {
    const {response, body} = await jsonRequest(`${await backendUrl()}/api/v1/guest-sessions`, {method: "POST"});
    if (!response.ok || typeof body?.token !== "string" || !body.token || !Number.isFinite(body.expires_in) || body.expires_in <= 60)
      throw new ApiError(body?.error?.message ?? "Could not start a guest session. Try again.", response.status, body?.error?.code, undefined, false);
    guestCache = {token: body.token, expires: Date.now() + (body.expires_in - 60) * 1000};
    try { sessionStorage.setItem("bi-guest", JSON.stringify(guestCache)); } catch { /* Retain the in-memory token. */ }
    return body.token as string;
  })().finally(() => { guestPromise = undefined; });
  return guestPromise;
}

export async function api<T>(
  path: string,
  init: RequestInit = {},
  retry = true,
  conditional = false,
): Promise<T> {
  const headers = new Headers(init.headers);
  const saved = conditional ? validatedReads.get(path) : undefined;
  if (saved) headers.set("If-None-Match", saved.etag);
  if (
    ["POST", "PATCH", "PUT", "DELETE"].includes(
      (init.method ?? "GET").toUpperCase(),
    ) ||
    headers.has("Authorization")
  ) {
    headers.set("Authorization", `Bearer ${await guestToken()}`);
    if (init.body) headers.set("Content-Type", "application/json");
  }
  const { response, body } = await jsonRequest(`${await backendUrl()}/api/v1${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
  if (response.status === 304 && saved) return saved.value as T;
  if (response.status === 401 && retry) {
    forgetGuest(headers.get("Authorization")?.replace(/^Bearer /, ""));
    return api(path, init, false);
  }
  if (!response.ok)
    throw new ApiError(
      body?.error?.message ?? "Request failed. Please try again.",
      response.status,
      body?.error?.code,
      retryDelay(response.headers.get("Retry-After")),
      (init.method ?? "GET").toUpperCase() === "GET",
    );
  if (conditional && response.headers.get("ETag")) {
    const bytes = JSON.stringify(body).length * 2;
    if (saved) { validatedBytes -= saved.bytes; validatedReads.delete(path); }
    if (bytes <= 256 * 1024) {
      while (validatedReads.size >= 8 || validatedBytes + bytes > 1024 * 1024) {
        const first = validatedReads.keys().next().value!;
        validatedBytes -= validatedReads.get(first)!.bytes;
        validatedReads.delete(first);
      }
      validatedReads.set(path, { etag: response.headers.get("ETag")!, value: body, bytes });
      validatedBytes += bytes;
    }
  }
  return body as T;
}

/** Only public conversation reads may reuse a body, and only after a fresh 304 response. */
export function revalidatedRead<T>(path: string, signal?: AbortSignal) {
  if (!/^\/conversations(?:\/[a-f0-9]{32})?$/.test(path)) throw new Error("Conditional read scope is invalid.");
  return api<T>(path, { signal }, true, true);
}

/** Guest-scoped resources (such as unpublished author interviews) require authenticated reads. */
export async function guestApi<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${await guestToken()}`);
  return api<T>(path, { ...init, headers });
}

export async function streamRun(
  runId: string,
  signal: AbortSignal,
  onEvent: (event: StreamEvent) => void,
) {
  let cursor = 0;
  for (let attempt = 0; attempt < 4; attempt++) {
    if (signal.aborted) return;
    let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
    const controller = new AbortController();
    const abort = () => controller.abort(signal.reason);
    signal.addEventListener("abort", abort, { once: true });
    let idleTimer: ReturnType<typeof setTimeout>;
    const armIdleDeadline = () => {
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => controller.abort(), 45000);
    };
    armIdleDeadline();
    try {
      const response = await fetch(
        `${await backendUrl()}/api/v1/runs/${runId}/events?after=${cursor}`,
        { signal: controller.signal, cache: "no-store" },
      );
      if (!response.ok || !response.body)
        throw new ApiError("The analysis stream could not connect.", response.status);
      reader = response.body.getReader();
      const decoder = new TextDecoder();
      let pending = "";
      while (true) {
        const { value, done } = await reader.read();
        armIdleDeadline();
        pending += decoder
          .decode(value, { stream: !done })
          .replace(/\r\n/g, "\n");
        let boundary;
        while ((boundary = pending.indexOf("\n\n")) !== -1) {
          const block = pending.slice(0, boundary);
          pending = pending.slice(boundary + 2);
          let type = "message",
            data = "",
            id = 0;
          for (const line of block.split("\n")) {
            if (line.startsWith("event:")) type = line.slice(6).trim();
            if (line.startsWith("data:")) data += line.slice(5).trim();
            if (line.startsWith("id:")) id = Number(line.slice(3));
          }
          if (data) {
            const event = { type, id, data: JSON.parse(data) };
            if (id && id <= cursor) continue;
            onEvent(event);
            if (id) cursor = id;
            if (type === "complete" || type === "error") {
              await reader.cancel();
              return;
            }
          }
        }
        if (done) break;
      }
      const status = await api<{ status: string; error?: string }>(
        `/runs/${runId}`,
      );
      if (status.status !== "running") {
        onEvent(status.status === "complete"
          ? { type: "complete", data: { run_id: runId } }
          : { type: "error", data: { code: status.status, message: status.error || "Analysis did not complete. Inspect the saved conversation." } });
        return;
      }
    } catch (error) {
      if (signal.aborted) return;
      if (attempt === 3 || (error instanceof ApiError && error.status >= 400 && error.status < 500 && ![408, 429].includes(error.status))) throw error;
    } finally {
      clearTimeout(idleTimer!);
      signal.removeEventListener("abort", abort);
      if (reader) {
        await reader.cancel().catch(() => {});
        reader.releaseLock();
      }
    }
    if (attempt === 3) throw new Error("The analysis connection was interrupted. Reopen the conversation to reconnect to the saved run.");
    onEvent({
      type: "progress",
      data: { message: "Reconnecting to the saved analysis…" },
    });
    await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
  }
}

/** Retry-After supports seconds and HTTP dates; never shorten a server deadline. */
export function retryDelay(value: string | null): number | undefined {
  if (!value) return undefined;
  const seconds = Number(value);
  const delay = Number.isFinite(seconds) ? seconds * 1000 : Date.parse(value) - Date.now();
  return Number.isFinite(delay) ? Math.max(0, delay) : undefined;
}

/** Only bootstrap GETs use this policy. Mutations and execution streams are unchanged. */
export async function initialRead<T>(read: () => Promise<T>, signal: AbortSignal): Promise<T> {
  try { return await read(); }
  catch (error) {
    if (signal.aborted || !(error instanceof ApiError) || !error.retryableRead ||
        ![0, 408, 502, 503, 504].includes(error.status) ||
        error.code === "invalid_response") throw error;
    await new Promise<void>((resolve, reject) => {
      const abort = () => { clearTimeout(timer); reject(signal.reason ?? new DOMException("Aborted", "AbortError")); };
      const timer = setTimeout(() => { signal.removeEventListener("abort", abort); resolve(); }, Math.max(1000, error.retryAfter ?? 0));
      signal.addEventListener("abort", abort, { once: true });
    });
    if (signal.aborted) throw signal.reason;
    return read();
  }
}
