"use client";

import { motion, type HTMLMotionProps } from "motion/react";
import { useAppMotion } from "@/hooks/use-app-motion";
import { EASE_OUT } from "@/lib/ease";

export function Reveal({
  delay = 0,
  children,
  ...props
}: HTMLMotionProps<"div"> & { delay?: number }) {
  const { reduced, hydrated } = useAppMotion();
  return (
    <motion.div
      initial={hydrated && !reduced ? { opacity: 0, y: 10 } : false}
      animate={{ opacity: 1, y: 0 }}
      exit={reduced ? undefined : { opacity: 0, y: -4 }}
      transition={{
        duration: reduced ? 0 : 0.24,
        delay: reduced ? 0 : delay,
        ease: EASE_OUT,
      }}
      data-motion-entry=""
      {...props}
    >
      {children}
    </motion.div>
  );
}
