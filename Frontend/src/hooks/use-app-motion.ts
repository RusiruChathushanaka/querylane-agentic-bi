"use client";

import { useReducedMotion } from "motion/react";
import { useHydrated, usePreferences } from "@/hooks/use-preferences";

/** CSS alone cannot stop JavaScript springs or number animations. */
export function useAppMotion() {
  const { preferences } = usePreferences();
  const systemReduced = useReducedMotion();
  const hydrated = useHydrated();
  return {
    // Keep server markup and the first client render identical, including Motion's
    // interactive tabIndex attributes. Opt into motion only after hydration.
    reduced: !hydrated || preferences.reduceMotion || systemReduced === true,
    hydrated,
  };
}
