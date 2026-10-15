"use client";

import { AnimatePresence, motion } from "motion/react";
import {
  Check,
  Database,
  GitMerge,
  MessageSquareText,
  ScanSearch,
} from "lucide-react";
import { useAppMotion } from "@/hooks/use-app-motion";
import { EASE_OUT } from "@/lib/ease";

const stages = [
  { id: "skills", label: "Skills", icon: ScanSearch },
  { id: "schema", label: "Understand", icon: ScanSearch },
  { id: "query", label: "Query", icon: Database },
  { id: "relationship", label: "Validate", icon: GitMerge },
  { id: "answer", label: "Explain", icon: MessageSquareText },
];

export function AnalysisProgress({
  stage,
  message,
}: {
  stage: string;
  message: string;
}) {
  const { reduced } = useAppMotion();
  const index = Math.max(
    0,
    stages.findIndex((item) => item.id === stage),
  );
  return (
    <div className="analysis-progress analysis-progress-card">
      <div
        className="analysis-progress-title"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        <span className="analysis-activity" aria-hidden="true">
          <motion.i
            animate={reduced ? { opacity: 1 } : { opacity: [0.45, 1, 0.45] }}
            transition={{ duration: 1.8, repeat: reduced ? 0 : Infinity }}
          />
        </span>
        <AnimatePresence initial={false} mode="popLayout">
          <motion.span
            key={stage || "schema"}
            initial={reduced ? false : { opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={reduced ? undefined : { opacity: 0, y: -5 }}
            transition={{ duration: reduced ? 0 : 0.18 }}
          >
            {message || "Working on your question"}
          </motion.span>
        </AnimatePresence>
      </div>
      <div className="analysis-track" aria-hidden="true">
        <motion.span
          animate={{ scaleX: (index + 1) / stages.length }}
          style={{ originX: 0 }}
          transition={{ duration: reduced ? 0 : 0.25, ease: EASE_OUT }}
        />
      </div>
      <ol
        aria-label="Analysis stages"
        style={{
          gridTemplateColumns: `repeat(${stages.length}, minmax(0, 1fr))`,
        }}
      >
        {stages.map(({ id, label, icon: Icon }, step) => (
          <li
            key={id}
            data-current={step === index}
            data-complete={step < index}
            aria-current={step === index ? "step" : undefined}
          >
            <motion.span
              animate={{ scale: step === index && !reduced ? 1.08 : 1 }}
              transition={{ duration: reduced ? 0 : 0.2 }}
            >
              {step < index ? <Check aria-hidden /> : <Icon aria-hidden />}
            </motion.span>
            <span>{label}</span>
            {step < index && <span className="sr-only">completed</span>}
          </li>
        ))}
      </ol>
    </div>
  );
}
