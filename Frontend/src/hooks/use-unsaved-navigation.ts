"use client";
import { useEffect } from "react";

export function useUnsavedNavigation(dirty: boolean) {
  useEffect(() => {
    function follow(event: MouseEvent) {
      if (
        !dirty ||
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey
      )
        return;
      const anchor = (event.target as Element | null)?.closest("a");
      if (
        !anchor ||
        anchor.target === "_blank" ||
        anchor.hasAttribute("download")
      )
        return;
      const target = new URL(anchor.href, location.href);
      if (
        target.pathname === location.pathname &&
        target.search === location.search
      )
        return;
      if (!window.confirm("Discard unsaved edits before leaving?")) {
        event.preventDefault();
        event.stopPropagation();
      }
    }
    document.addEventListener("click", follow, true);
    return () => document.removeEventListener("click", follow, true);
  }, [dirty]);
}
