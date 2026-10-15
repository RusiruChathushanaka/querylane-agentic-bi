"use client";

import { useLayoutEffect } from "react";
import { ThemeProvider } from "next-themes";
import { usePreferences } from "@/hooks/use-preferences";
import { THEME_KEY } from "@/lib/preferences";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";

function AppearanceSync() {
  const { preferences } = usePreferences();
  useLayoutEffect(() => {
    const root = document.documentElement;
    root.dataset.accent = preferences.accent;
    root.dataset.density = preferences.density;
    root.dataset.reduceMotion = String(preferences.reduceMotion);
  }, [preferences.accent, preferences.density, preferences.reduceMotion]);
  return null;
}

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      storageKey={THEME_KEY}
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <AppearanceSync />
      <TooltipProvider>{children}</TooltipProvider>
      <Toaster position="bottom-right" />
    </ThemeProvider>
  );
}
