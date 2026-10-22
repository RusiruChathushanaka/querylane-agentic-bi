"use client";
import { useEffect, useState } from "react";

/** One-way visibility admission; native reader scrolling remains independent. */
export function useNearViewport<T extends HTMLElement>() {
  const [node, ref] = useState<T | null>(null);
  const [near, setNear] = useState(false);
  useEffect(() => {
    if (!node) return;
    if (!window.IntersectionObserver) {
      const frame = requestAnimationFrame(() => setNear(true));
      return () => cancelAnimationFrame(frame);
    }
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) { setNear(true); observer.disconnect(); }
    }, { rootMargin: "200px" });
    observer.observe(node);
    return () => observer.disconnect();
  }, [node]);
  return { ref, near };
}
