import type { ChartViewState } from "./dashboard-types";
import type { Artifact } from "./types";

export type MetricRef = { id: string; version: number };
export type MetricDefinition = {
  name: string;
  description: string;
  aliases: string[];
  formula: {
    operation: "sum" | "count" | "distinct_count" | "subtract" | "ratio";
    measure: string | null;
    left: MetricRef | null;
    right: MetricRef | null;
  };
  time_basis: "order_date" | "refund_date";
  unit: "currency" | "count" | "percent" | "number";
  dimensions: ("region" | "store" | "category" | "product" | "channel")[];
  limitations: string;
  examples: string[];
};
export type Metric = {
  id: string;
  name: string;
  revision: number;
  published_version: number;
  archived: boolean;
  draft: MetricDefinition;
  published_definition?: MetricDefinition;
  updated_at: string;
};
export type JobRun = {
  id: string;
  root_id: string;
  status: string;
  stage: string;
  revision: number;
  error?: string;
  clarification?: string;
  version: number;
};
export type ProposedCard = {
  artifact_id: string;
  title: string;
  note: string;
  width: "standard" | "wide";
  view: ChartViewState;
  reused: boolean;
};
export type DashboardBuild = {
  id: string;
  status: string;
  revision: number;
  dashboard_id?: string;
  base_revision?: number;
  base_cards?: ProposedCard[];
  run?: JobRun;
  proposal?: {
    name: string;
    description: string;
    cards: ProposedCard[];
    omitted: string[];
  };
};
export type ForecastPlan = {
  id: string;
  name: string;
  status: string;
  revision: number;
  latest_version?: number;
  versions: number[];
  deleted: boolean;
  run?: JobRun;
  active_run?: string;
};
export type HierarchyNode = {
  id: string;
  name: string;
  level: "company" | "region" | "store" | "category" | "product";
  parent: string | null;
  history: string[];
};
export type ForecastDocument = {
  preferred_view?: "both" | "geography" | "products";
  id: string;
  version: number;
  title: string;
  run_id: string;
  kind: string;
  created_at: string;
  history: {
    nodes: Record<string, HierarchyNode>;
    months: string[];
    input_hash: string;
  };
  predictions: Record<string, number[]>;
  statistical_predictions?: Record<string, number[]>;
  future_months: string[];
  horizon: number;
  cutoff: string;
  selection: {
    selected: string;
    baseline: number;
    adaptive: number;
    level_gate: boolean;
    folds: {
      train_end: string;
      test_start: string;
      test_end: string;
      baseline: number;
      adaptive: number;
    }[];
    node_errors: Record<
      string,
      { baseline_mae: number; adaptive_mae: number }[]
    >;
  };
  methods: Record<
    string,
    {
      method: string;
      scores: Record<string, { mae: number; rmse: number }>;
      comparison?: { status: string; reason: string };
    }
  >;
  limitations: string[];
  adjustments: {
    node_id: string;
    operation: string;
    value: number;
    reason: string;
  }[];
  metric_snapshot: {
    id: string;
    version: number;
    definition: MetricDefinition;
  };
  company_artifact_id?: string;
  artifact_ids: string[];
};
export type ForecastRevision = {
  version: number;
  document: ForecastDocument;
  downloads: Record<string, { sha256: string; size: number }>;
};
export type SavedArtifact = Artifact;
