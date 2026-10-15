"use client";

import { useLayoutEffect } from "react";
import { ThemeProvider } from "next-themes";
import { MotionConfig } from "motion/react";
import { useAppMotion } from "@/hooks/use-app-motion";
import { EASE_OUT } from "@/lib/ease";
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
  const { reduced } = useAppMotion();
  return (
    <ThemeProvider
      attribute="class"
      storageKey={THEME_KEY}
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <MotionConfig
        reducedMotion={reduced ? "always" : "user"}
        transition={{ duration: reduced ? 0 : 0.24, ease: EASE_OUT }}
      >
        <AppearanceSync />
        <TooltipProvider>{children}</TooltipProvider>
        <Toaster
          position="top-right"
          offset={{ top: "84px", right: "24px" }}
          mobileOffset={{ top: "72px", left: "12px", right: "12px" }}
          closeButton
          visibleToasts={3}
        />
      </MotionConfig>
    </ThemeProvider>
  );
}
