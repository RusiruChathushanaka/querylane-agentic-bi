"use client";

import { useSyncExternalStore } from "react";
import {
  DEFAULT_PREFERENCES,
  PREFERENCES_KEY,
  parsePreferences,
  type Preferences,
} from "@/lib/preferences";

type Snapshot = { preferences: Readonly<Preferences>; persistent: boolean };
const serverSnapshot: Snapshot = {
  preferences: DEFAULT_PREFERENCES,
  persistent: true,
};
let snapshot = serverSnapshot;
let previousRaw: string | null | undefined;
let memoryOnly = false;
const eventName = "querylane:preferences";

function getSnapshot(): Snapshot {
  if (typeof window === "undefined" || memoryOnly) return snapshot;
  try {
    const raw = localStorage.getItem(PREFERENCES_KEY);
    if (raw !== previousRaw) {
      previousRaw = raw;
      snapshot = { preferences: parsePreferences(raw), persistent: true };
    }
  } catch {
    memoryOnly = true;
    snapshot = { ...snapshot, persistent: false };
  }
  return snapshot;
}

function subscribe(listener: () => void) {
  const storage = (event: StorageEvent) => {
    if (event.key === PREFERENCES_KEY || event.key === null) {
      // Retry storage after a cross-tab update, even if an earlier write failed.
      memoryOnly = false;
      previousRaw = undefined;
      listener();
    }
  };
  window.addEventListener("storage", storage);
  window.addEventListener(eventName, listener);
  return () => {
    window.removeEventListener("storage", storage);
    window.removeEventListener(eventName, listener);
  };
}

function save(preferences: Preferences) {
  const raw = JSON.stringify(preferences);
  let persistent = true;
  try {
    localStorage.setItem(PREFERENCES_KEY, raw);
    previousRaw = raw;
    memoryOnly = false;
  } catch {
    persistent = false;
    memoryOnly = true;
  }
  snapshot = { preferences, persistent };
  window.dispatchEvent(new Event(eventName));
  return persistent;
}

export function updatePreference<K extends keyof Preferences>(
  key: K,
  value: Preferences[K],
) {
  return save(
    parsePreferences(
      JSON.stringify({ ...getSnapshot().preferences, [key]: value }),
    ),
  );
}

export function resetPreferences() {
  return save({ ...DEFAULT_PREFERENCES });
}

export function usePreferences() {
  return useSyncExternalStore(subscribe, getSnapshot, () => serverSnapshot);
}

const subscribeHydration = () => () => {};
export function useHydrated() {
  return useSyncExternalStore(
    subscribeHydration,
    () => true,
    () => false,
  );
}
