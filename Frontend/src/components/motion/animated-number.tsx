"use client";
// Adapted from beui.dev — MIT, Copyright (c) 2026 Saurabh Chauhan.
// See licenses/beui-MIT.txt. Querylane keeps an accessible final value.

import { animate, useInView } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { EASE_OUT } from "@/lib/ease";
import { cn } from "@/lib/utils";
import { useAppMotion } from "@/hooks/use-app-motion";

export interface AnimatedNumberProps {
  value: number;
  duration?: number;
  format?: (n: number) => string;
  className?: string;
  startOnView?: boolean;
}

export function AnimatedNumber({
  value,
  duration = 0.28,
  format = (n) => Math.round(n).toLocaleString(),
  className,
  startOnView = true,
}: AnimatedNumberProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.6 });
  const { reduced: reduce } = useAppMotion();
  const [display, setDisplay] = useState(value);
  const fromRef = useRef<number | null>(null);

  useEffect(() => {
    if (startOnView && !inView) return;
    if (reduce) {
      fromRef.current = value;
      return;
    }
    const controls = animate(fromRef.current ?? value * 0.94, value, {
      duration,
      ease: EASE_OUT,
      onUpdate: (v) => {
        fromRef.current = v;
        setDisplay(v);
      },
    });
    return () => controls.stop();
  }, [value, duration, inView, startOnView, reduce]);

  return (
    <span ref={ref} className={cn("tabular-nums", className)}>
      <span aria-hidden="true">{format(reduce ? value : display)}</span>
      <span className="sr-only">{format(value)}</span>
    </span>
  );
}
