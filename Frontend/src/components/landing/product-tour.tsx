"use client";

import { useState } from "react";
import { motion } from "motion/react";
import {
  AudioLines,
  Check,
  FileChartColumn,
  MicOff,
  TrendingUp,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { useAppMotion } from "@/hooks/use-app-motion";
import { RevenueIllustration } from "./product-illustrations";

const views = [
  { id: "reports", label: "Reports", icon: FileChartColumn },
  { id: "predictions", label: "Predictions", icon: TrendingUp },
  { id: "voice", label: "Voice BI", icon: AudioLines },
] as const;

export function ProductTour() {
  const [followup, setFollowup] = useState(false);
  const { reduced } = useAppMotion();
  return (
    <Tabs defaultValue="reports" className="landing-tour">
      <TabsList
        aria-label="Guided product preview"
        className="min-h-14 w-full max-w-lg mx-auto"
      >
        {views.map(({ id, label, icon: Icon }) => (
          <TabsTrigger key={id} value={id} className="min-h-11 px-3">
            <Icon aria-hidden />
            {label}
          </TabsTrigger>
        ))}
      </TabsList>
      {views.map(({ id }) => (
        <TabsContent key={id} value={id}>
          <motion.div
            initial={reduced ? false : { y: 6 }}
            animate={{ y: 0 }}
            transition={{ duration: reduced ? 0 : 0.18 }}
            className="landing-tour-panel"
          >
            {id === "reports" && (
              <>
                <div className="landing-tour-copy">
                  <span className="landing-eyebrow">01 / ADVANCED REPORTS</span>
                  <h3>
                    Your analyst.
                    <br />
                    From brief to boardroom.
                  </h3>
                  <p>
                    Go beyond a quick answer. Coordinate deeper analysis into a
                    Business or Technical report, with saved evidence behind its
                    findings.
                  </p>
                  <ul className="landing-checks">
                    <li>
                      <Check aria-hidden />
                      Background progress; return after navigating away
                    </li>
                    <li>
                      <Check aria-hidden />
                      Findings, charts, assumptions and methodology
                    </li>
                    <li>
                      <Check aria-hidden />
                      PDF, Word and full saved-result CSV downloads
                    </li>
                  </ul>
                  <p className="landing-fine-print">
                    Typically several minutes. When a narrative cannot be
                    supported, the report can fall back to a verified evidence
                    summary.
                  </p>
                </div>
                <div className="landing-preview-paper">
                  <div className="landing-preview-label">
                    <FileChartColumn size={16} aria-hidden />
                    SAVED REPORT EXCERPT<span>Business style</span>
                  </div>
                  <p className="landing-example-question">
                    “Review retail sales performance and the outlook.”
                  </p>
                  <h4>Retail performance review</h4>
                  <p className="landing-preview-subtitle">
                    Executive summary · Jan 2023–Sep 2026
                  </p>
                  <div className="landing-report-callout">
                    <strong>$354.43m</strong>
                    <span>
                      Merchandise revenue · before refunds, tax and shipping
                    </span>
                  </div>
                  <p>
                    573,348 completed orders across 45 months. Overall average
                    order value: <strong>$618.17</strong>.
                  </p>
                  <RevenueIllustration />
                  <details className="landing-methodology">
                    <summary>Inspect definitions &amp; methodology</summary>
                    <p>
                      Revenue after item discounts, before refunds, tax and
                      shipping. Overall AOV = total revenue ÷ completed orders,
                      rather than an unweighted mean of monthly AOVs. Synthetic
                      retail evidence; this excerpt is not a newly generated
                      report.
                    </p>
                  </details>
                  <div
                    className="landing-format-labels"
                    role="group"
                    aria-label="Available report export formats"
                  >
                    <span>PDF</span>
                    <span>Word</span>
                    <span>CSV data</span>
                    <small>Formats available in the application</small>
                  </div>
                </div>
              </>
            )}
            {id === "predictions" && (
              <>
                <div className="landing-tour-copy">
                  <span className="landing-eyebrow">
                    02 / VALIDATED PREDICTIONS
                  </span>
                  <h3>
                    Look ahead.
                    <br />
                    Know the limits.
                  </h3>
                  <p>
                    Explore a forecast grounded in history, checked against
                    chronological backtests and simple baselines.
                  </p>
                  <ul className="landing-checks">
                    <li>
                      <Check aria-hidden />
                      Observed and predicted values clearly separated
                    </li>
                    <li>
                      <Check aria-hidden />
                      Model diagnostics and observation cutoffs
                    </li>
                    <li>
                      <Check aria-hidden />
                      Conditional scenarios with explicit future inputs
                    </li>
                  </ul>
                  <p className="landing-fine-print">
                    Insufficient history or weak validation can withhold a
                    prediction. Scenarios describe associations under stated
                    assumptions; they do not establish causal lift.
                  </p>
                </div>
                <div className="landing-preview-paper">
                  <div className="landing-preview-label">
                    <TrendingUp size={16} aria-hidden />
                    SAVED FORECAST EXAMPLE<span>ETS · monthly</span>
                  </div>
                  <p className="landing-example-question">
                    “What could revenue look like next quarter?”
                  </p>
                  <h4>History, then the horizon</h4>
                  <p className="landing-preview-subtitle">
                    Observation cutoff: September 30, 2026
                  </p>
                  <RevenueIllustration forecast />
                  <div className="landing-forecast-notes">
                    <span>3 rolling-origin backtests</span>
                    <span>October–December 2026 horizon</span>
                  </div>
                  <p className="landing-caution">
                    Point predictions from the saved validated example. No
                    validated prediction intervals are available for this
                    example. Forecasts are estimates, not guarantees.
                  </p>
                </div>
              </>
            )}
            {id === "voice" && (
              <>
                <div className="landing-tour-copy">
                  <span className="landing-eyebrow">
                    03 / CONVERSATIONAL VOICE BI
                  </span>
                  <h3>
                    Good questions.
                    <br />
                    Great conversations.
                  </h3>
                  <p>
                    Talk through the data with an AI business analyst. Follow up
                    naturally while transcripts, spoken responses and visual
                    results stay together.
                  </p>
                  <ul className="landing-checks">
                    <li>
                      <Check aria-hidden />
                      Live voice and text follow-ups
                    </li>
                    <li>
                      <Check aria-hidden />
                      Interrupt, mute and reconnect
                    </li>
                    <li>
                      <Check aria-hidden />
                      Charts and query evidence alongside answers
                    </li>
                  </ul>
                  <p className="landing-fine-print">
                    This guided example uses no audio or microphone. Start
                    Advanced Analysis from the application composer when you
                    want a detailed report.
                  </p>
                </div>
                <div className="landing-preview-paper landing-voice-preview">
                  <div className="landing-preview-label">
                    <MicOff size={16} aria-hidden />
                    EXAMPLE CONVERSATION<span>Microphone off</span>
                  </div>
                  <div className="landing-transcript landing-transcript-user">
                    <small>You · scripted transcript</small>
                    <p>Show me monthly revenue for 2026 so far.</p>
                  </div>
                  <div className="landing-transcript">
                    <small>
                      <AudioLines size={14} aria-hidden />
                      Analyst · example spoken response
                    </small>
                    <p>
                      Here is January through September. Revenue in September
                      was $9.45 million. The latest complete month is September
                      2026.
                    </p>
                  </div>
                  <RevenueIllustration />
                  <div aria-live="polite">
                    {followup && (
                      <div className="landing-followup">
                        <p>
                          <strong>You:</strong> How does September compare with
                          August?
                        </p>
                        <p>
                          <strong>Analyst:</strong> September revenue was 1.35%
                          lower than August, before refunds, tax and shipping.
                        </p>
                      </div>
                    )}
                  </div>
                  <Button
                    variant="outline"
                    className="min-h-11"
                    onClick={() => setFollowup(!followup)}
                  >
                    {followup
                      ? "Reset conversation example"
                      : "Reveal a follow-up"}
                  </Button>
                </div>
              </>
            )}
          </motion.div>
        </TabsContent>
      ))}
      <p className="landing-tour-disclaimer">
        Guided previews · saved synthetic evidence and scripted interactions ·
        no live queries
      </p>
    </Tabs>
  );
}
