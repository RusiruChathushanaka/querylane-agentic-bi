"use client";
import { useRef } from "react";

/** Keep the exact mutation identity after an ambiguous network failure. */
export function usePendingRequest() {
  const pending = useRef(new Map<string, string>());
  return {
    id(scope: string, payload: unknown) {
      const key = JSON.stringify([scope, payload]);
      if (!pending.current.has(key))
        pending.current.set(key, crypto.randomUUID());
      return pending.current.get(key)!;
    },
    complete(scope: string, payload: unknown) {
      pending.current.delete(JSON.stringify([scope, payload]));
    },
  };
}
