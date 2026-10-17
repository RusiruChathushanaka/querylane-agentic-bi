import type { SkillReference } from "./types";
export type ReportStatus =
  "queued" | "running" | "waiting_input" | "complete" | "failed" | "cancelled";
export type ReportRun = {
  id: string;
  report_id: string;
  version: number;
  conversation_id: string;
  status: ReportStatus;
  stage: string;
  sequence: number;
  revision: number;
  cancel_requested: boolean;
  clarification: string | null;
  clarification_requirements?: ForecastRequirement[] | null;
  error?: string;
  clarifications: { question: string; answer: string }[];
};
export type ForecastRequirement = {
  target: string;
  drivers: string[];
  grain: "day" | "week" | "month";
  horizon: number | null;
};
export type Report = {
  id: string;
  name: string;
  revision: number;
  versions: number[];
  latest_version: number | null;
  status: ReportStatus;
  created_at: string;
  updated_at: string;
  deleted: boolean;
  conversation_id: string;
  active_run_id?: string | null;
  run?: ReportRun | null;
};
export type ReportDocument = {
  report_id: string;
  version: number;
  title: string;
  scope: string;
  summary: string;
  style: "business" | "technical";
  created_at: string;
  sections: {
    id: string;
    title: string;
    markdown: string;
    kind: string;
    artifact_ids: string[];
  }[];
  artifact_ids: string[];
  claims: {
    id: string;
    label: string;
    value: string;
    formatted: string;
    calculation: string;
    artifact_id: string;
  }[];
  definitions: string[];
  assumptions: string[];
  limitations: string[];
  model: string;
  mode_note: string;
  data_profile: string;
  reviewed: boolean;
  skills_used: SkillReference[];
  skill_warnings: string[];
};
export type ReportRevision = {
  version: number;
  document: ReportDocument;
  downloads: Record<string, { size: number; sha256: string }>;
};
