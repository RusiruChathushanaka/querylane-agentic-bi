export type Conversation = {
  id: string;
  title: string;
  source: string;
  updated_at: string;
  active_run: string | null;
  lease_until: number;
  visibility: string;
  parent_id?: string;
  skill_ids?: string[];
  skills_revision?: number;
};
export type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  artifact_id?: string;
  followups?: string[];
  created_at: string;
  run_id: string;
  skills_used?: SkillReference[];
  skill_warnings?: string[];
};
export type Connection = {
  id: string;
  name: string;
  engine: string;
  tables: number;
  connected: boolean;
  mode: string;
  error?: string;
};
export type Visualization = {
  type: string;
  title: string;
  x: string | null;
  y: string[];
  format: "number" | "currency" | "percent";
};
export type Artifact = {
  ai?: {
    backend: "fixture" | "gemini";
    text_model: string | null;
    selected_text_model: string;
  };
  id: string;
  title: string;
  columns: { name: string; type: string }[];
  rows: Record<string, unknown>[];
  row_count: number;
  preview_count: number;
  complete: boolean;
  page_count: number;
  visualization: Visualization;
  assumptions: string[];
  retrieval?: string;
  skills_used?: SkillReference[];
  skill_warnings?: string[];
  join_diagnostics?: Record<string, unknown>;
  provenance: {
    source: string;
    sql: string;
    row_count: number;
    elapsed_ms: number;
    executed_at: string;
    job_id?: string;
    bytes_processed?: number;
    complete: boolean;
  }[];
};
export type StreamEvent = {
  type: string;
  data: Record<string, unknown>;
  id?: number;
};

export type SkillContent = {
  name: string;
  description: string;
  when_to_use: string;
  source: "all" | "bigquery" | "postgres";
  tags: string[];
  instructions: string;
};
export type Skill = SkillContent & {
  id: string;
  enabled: boolean;
  deleted: boolean;
  revision: number;
  created_at: string;
  updated_at: string;
};
export type SkillReference = Pick<
  Skill,
  "id" | "name" | "description" | "revision"
> & {
  mode: "manual" | "automatic";
};

export type SkillSummary = Omit<Skill, "instructions">;

export type AuthorBrief = {
  name: string;
  description: string;
  purpose: string;
  when_to_use: string;
  source: "" | SkillContent["source"];
  workflow: string;
  definitions: string;
  examples: string;
  tags: string;
};
export type AuthorSession = {
  id: string;
  revision: number;
  status: "collecting" | "draft_ready" | "published";
  brief: AuthorBrief;
  draft: SkillContent | null;
  transcript: {
    role: "user" | "assistant";
    text: string;
    created_at: string;
  }[];
  missing_fields: string[];
  connected: boolean;
  turns: number;
  expires_at: number;
  published_skill_id: string | null;
};
