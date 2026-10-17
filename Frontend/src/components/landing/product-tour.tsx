"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "motion/react";
import {
  AudioLines,
  Check,
  FileChartColumn,
  GitBranch,
  MicOff,
  TrendingUp,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { useAppMotion } from "@/hooks/use-app-motion";
import {
  RevenueIllustration,
  ScenarioIllustration,
} from "./product-illustrations";
import data from "@/lib/landing-preview-data.json";

const views = [
  { id: "reports", label: "Reports", icon: FileChartColumn },
  { id: "predictions", label: "Forecasts", icon: TrendingUp },
  { id: "scenarios", label: "Scenarios", icon: GitBranch },
  { id: "voice", label: "Voice BI", icon: AudioLines },
] as const;

export function ProductTour() {
  const [followup, setFollowup] = useState(false);
  const { reduced } = useAppMotion();
  return (
    <Tabs defaultValue="reports" className="landing-tour">
      <TabsList
        aria-label="Guided product preview"
        className="landing-tour-tabs"
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
                    02 / TIMESFM FORECASTING
                  </span>
                  <h3>
                    Look ahead.
                    <br />
                    Put models to the test.
                  </h3>
                  <p>
                    Google TimesFM 3.0 Preview brings managed time-series
                    forecasting to Advanced Analysis. The agent proposes useful
                    forecasts; measured backtests choose the published method.
                  </p>
                  <ul className="landing-checks">
                    <li>
                      <Check aria-hidden />
                      Compared with statistical methods and a seasonal baseline
                    </li>
                    <li>
                      <Check aria-hidden />
                      Three chronological backtests across the full horizon
                    </li>
                    <li>
                      <Check aria-hidden />
                      Saved predictions, model scores and observation cutoffs
                    </li>
                  </ul>
                  <p className="landing-fine-print">
                    Insufficient history or weak validation can withhold a
                    prediction. When TimesFM is unavailable, supported
                    statistical findings remain available with clear
                    limitations.
                  </p>
                </div>
                <div className="landing-preview-paper">
                  <div className="landing-preview-label">
                    <TrendingUp size={16} aria-hidden />
                    VERIFIED FORECAST<span>TimesFM 3.0 · Preview</span>
                  </div>
                  <p className="landing-example-question">
                    “What could revenue look like next quarter?”
                  </p>
                  <h4>A saved, backtested revenue outlook</h4>
                  <p className="landing-preview-subtitle">
                    Observation cutoff: September 30, 2026
                  </p>
                  <RevenueIllustration forecast />
                  <div className="landing-forecast-notes">
                    <span>3 rolling-origin backtests</span>
                    <span>October–December 2026 horizon</span>
                  </div>
                  <details className="landing-methodology">
                    <summary>Compare the verified forecasting methods</summary>
                    <p>
                      Three monthly backtest folds. MAE is average absolute
                      error in USD; lower is better. A candidate must improve
                      baseline MAE by at least 5% and win at least two folds.
                    </p>
                    <div className="landing-table-scroll">
                      <table>
                        <caption>
                          Saved monthly revenue comparison · three-month horizon
                        </caption>
                        <thead>
                          <tr>
                            <th scope="col">Method</th>
                            <th scope="col">MAE · USD</th>
                            <th scope="col">Outcome</th>
                          </tr>
                        </thead>
                        <tbody>
                          {data.scores.map((score) => (
                            <tr key={score.method}>
                              <th scope="row">
                                {score.method === "timesfm_3"
                                  ? "TimesFM 3.0 · Preview"
                                  : score.method === "seasonal_naive"
                                    ? "Seasonal-naive baseline"
                                    : score.method.toUpperCase()}
                              </th>
                              <td>
                                {score.mae.toLocaleString("en-US", {
                                  maximumFractionDigits: 2,
                                  minimumFractionDigits: 2,
                                })}
                              </td>
                              <td>
                                {score.selected ? "Selected" : "Compared"}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </details>
                  <p className="landing-caution">
                    Point predictions from the saved validated example. No
                    validated prediction intervals are available for this
                    example. Forecasts are estimates, not guarantees.
                  </p>
                  <Link
                    prefetch={false}
                    href={data.reportUrl}
                    className="landing-text-link landing-example-link"
                  >
                    Open verified forecast report{" "}
                    <TrendingUp size={15} aria-hidden />
                  </Link>
                </div>
              </>
            )}
            {id === "scenarios" && (
              <>
                <div className="landing-tour-copy">
                  <span className="landing-eyebrow">
                    03 / CONDITIONAL SCENARIOS
                  </span>
                  <h3>
                    Change the assumptions.
                    <br />
                    Compare the outlook.
                  </h3>
                  <p>
                    Explore what the model predicts under explicit alternative
                    driver paths. The same validated method and history keep the
                    comparison consistent.
                  </p>
                  <ul className="landing-checks">
                    <li>
                      <Check aria-hidden />
                      You supply each future driver for the full horizon
                    </li>
                    <li>
                      <Check aria-hidden />
                      Historical support and backtests gate the analysis
                    </li>
                    <li>
                      <Check aria-hidden />A separate saved scenario artifact
                      retains both paths
                    </li>
                  </ul>
                  <p className="landing-fine-print">
                    These are conditional estimates based on historical
                    associations. They do not establish causal promotion lift or
                    guaranteed revenue.
                  </p>
                </div>
                <div className="landing-preview-paper">
                  <div className="landing-preview-label">
                    <GitBranch size={16} aria-hidden />
                    VERIFIED SCENARIO<span>TimesFM 3.0 · Preview</span>
                  </div>
                  <p className="landing-example-question">
                    “Compare no promotion days with promotion every day for the
                    next 14 days.”
                  </p>
                  <h4>Two assumptions. One consistent model.</h4>
                  <p className="landing-preview-subtitle">
                    Saved synthetic example · observation cutoff September 30,
                    2026
                  </p>
                  <ScenarioIllustration />
                  <div className="landing-forecast-notes">
                    <span>14 explicit future driver values per path</span>
                    <span>1,369 saved days of history</span>
                  </div>
                  <details className="landing-methodology">
                    <summary>Inspect scenario assumptions</summary>
                    <p>
                      The requester supplied promotion_day=0 for every baseline
                      date and promotion_day=1 for every alternative date,
                      October 1–14, 2026. TimesFM used the same
                      1,312-observation context for each comparison fold.
                      Conditional backtest errors assume driver paths are known.
                      Full values and model evidence remain in report version 1.
                    </p>
                  </details>
                  <p className="landing-caution">
                    Both lines are predictions. Totals and chart values are
                    rounded; no validated prediction intervals are available. A
                    different future schedule requires a new analysis.
                  </p>
                  <Link
                    prefetch={false}
                    href={data.scenario.reportUrl}
                    className="landing-text-link landing-example-link"
                  >
                    Open verified scenario report{" "}
                    <GitBranch size={15} aria-hidden />
                  </Link>
                </div>
              </>
            )}
            {id === "voice" && (
              <>
                <div className="landing-tour-copy">
                  <span className="landing-eyebrow">
                    04 / CONVERSATIONAL VOICE BI
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
