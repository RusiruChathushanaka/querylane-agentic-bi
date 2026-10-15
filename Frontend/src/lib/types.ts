export type Conversation = {
  id: string;
  title: string;
  source: string;
  updated_at: string;
  active_run: string | null;
  lease_until: number;
  visibility: string;
  parent_id?: string;
};
export type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  artifact_id?: string;
  followups?: string[];
  created_at: string;
  run_id: string;
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
