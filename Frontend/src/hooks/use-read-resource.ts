"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, initialRead } from "@/lib/api";

/** Independent, cancellable reads. Polling skips pending work; manual retry replaces it. */
export function useReadResource<T>(
  key: string,
  read: (signal: AbortSignal) => Promise<T>,
  commit: (value: T) => void,
  interval = 0,
) {
  const callbacks = useRef({ read, commit });
  useEffect(() => { callbacks.current = { read, commit }; });
  const current = useRef<{
    controller?: AbortController;
    key: string;
    loaded: boolean;
    retryAt: number;
  }>({ key, loaded: false, retryAt: 0 });
  const [state, setState] = useState({ pending: true, loaded: false, error: "", retryAt: 0 });
  const refresh = useCallback(async (replace = true) => {
    const resource = current.current;
    if (!replace && (resource.controller || !resource.loaded)) return;
    if (resource.key !== key || resource.retryAt > Date.now()) return;
    resource.controller?.abort();
    const controller = new AbortController();
    resource.controller = controller;
    setState({ pending: true, loaded: resource.loaded, error: "", retryAt: 0 });
    try {
      const task = () => callbacks.current.read(controller.signal);
      const value = resource.loaded ? await task() : await initialRead(task, controller.signal);
      if (controller.signal.aborted || current.current !== resource) return;
      callbacks.current.commit(value);
      resource.loaded = true;
      setState({ pending: false, loaded: true, error: "", retryAt: 0 });
      return value;
    } catch (e) {
      if (controller.signal.aborted || current.current !== resource) return;
      resource.retryAt = e instanceof ApiError ? Date.now() + (e.retryAfter ?? 0) : 0;
      setState({
        pending: false,
        loaded: resource.loaded,
        error: e instanceof Error ? e.message : "The service is unavailable.",
        retryAt: resource.retryAt,
      });
    } finally {
      if (resource.controller === controller) resource.controller = undefined;
    }
  }, [key]);
  useEffect(() => {
    const resource = { key, loaded: false, retryAt: 0, controller: undefined as AbortController | undefined };
    current.current = resource;
    void refresh();
    const timer = interval ? setInterval(() => {
      if (!document.hidden) void refresh(false);
    }, interval) : undefined;
    return () => { resource.controller?.abort(); clearInterval(timer); };
  }, [key, interval, refresh]);
  return { ...state, refresh };
}
