import type { StreamEvent } from "./types";

let basePromise: Promise<string> | undefined;
let guestPromise: Promise<string> | undefined;

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function backendUrl(): Promise<string> {
  basePromise ??= fetch("/api/config", { cache: "no-store" })
    .then(async (response) => {
      if (!response.ok)
        throw new Error("Application configuration is unavailable.");
      return (await response.json()).backend_url.replace(/\/$/, "") as string;
    })
    .catch((error) => {
      basePromise = undefined;
      throw error;
    });
  return basePromise;
}

export async function guestToken(): Promise<string> {
  const cached = sessionStorage.getItem("bi-guest");
  if (cached) {
    const parsed = JSON.parse(cached) as { token: string; expires: number };
    if (parsed.expires > Date.now()) return parsed.token;
    sessionStorage.removeItem("bi-guest");
  }
  guestPromise ??= (async () => {
    const response = await fetch(
      `${await backendUrl()}/api/v1/guest-sessions`,
      { method: "POST" },
    );
    const body = await response.json();
    if (!response.ok)
      throw new Error(
        body.error?.message ?? "Could not start a guest session.",
      );
    sessionStorage.setItem(
      "bi-guest",
      JSON.stringify({
        token: body.token,
        expires: Date.now() + (body.expires_in - 60) * 1000,
      }),
    );
    return body.token as string;
  })().finally(() => {
    guestPromise = undefined;
  });
  return guestPromise;
}

export async function api<T>(
  path: string,
  init: RequestInit = {},
  retry = true,
): Promise<T> {
  const headers = new Headers(init.headers);
  if (
    ["POST", "PATCH", "PUT", "DELETE"].includes(
      (init.method ?? "GET").toUpperCase(),
    )
  ) {
    headers.set("Authorization", `Bearer ${await guestToken()}`);
    if (init.body) headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${await backendUrl()}/api/v1${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
  if (response.status === 401 && retry) {
    sessionStorage.removeItem("bi-guest");
    return api(path, init, false);
  }
  const body = await response.json();
  if (!response.ok)
    throw new ApiError(
      body.error?.message ?? "Request failed. Please try again.",
      response.status,
      body.error?.code,
    );
  return body as T;
}

export async function streamRun(
  runId: string,
  signal: AbortSignal,
  onEvent: (event: StreamEvent) => void,
) {
  let cursor = 0;
  for (let attempt = 0; attempt < 4; attempt++) {
    if (signal.aborted) return;
    try {
      const response = await fetch(
        `${await backendUrl()}/api/v1/runs/${runId}/events?after=${cursor}`,
        { signal, cache: "no-store" },
      );
      if (!response.ok || !response.body)
        throw new Error("The analysis stream could not connect.");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let pending = "";
      while (true) {
        const { value, done } = await reader.read();
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
            if (id) cursor = id;
            onEvent({ type, id, data: JSON.parse(data) });
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
      if (status.status !== "running") return;
    } catch (error) {
      if (signal.aborted) return;
      if (attempt === 3) throw error;
    }
    onEvent({
      type: "progress",
      data: { message: "Reconnecting to the saved analysis…" },
    });
    await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
  }
}
