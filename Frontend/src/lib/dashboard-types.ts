export type ChartViewState = {
  version: 1;
  view: string;
  start: string | null;
  end: string | null;
  primary: string | null;
  visible_measures: string[];
  order: string;
  top: 5 | 10 | 20;
  scatter_x: string | null;
  scatter_y: string | null;
  highlights: boolean;
  decimals: 0 | 1 | 2;
};
export type ChartCapture = { state: ChartViewState; ready: boolean };
export type Dashboard = {
  id: string;
  name: string;
  description: string;
  revision: number;
  item_ids: string[];
  card_count: number;
  sources: string[];
  created_at: string;
  updated_at: string;
  deleted: boolean;
  recover_until?: number | null;
  items?: DashboardItem[];
};
export type DashboardItem = {
  id: string;
  artifact_id: string;
  conversation_id: string;
  conversation_available?: boolean;
  title: string;
  note: string;
  width: "standard" | "wide";
  view: ChartViewState;
  pinned_at: string;
  removed: boolean;
  summary: {
    title: string;
    created_at: string;
    row_count: number;
    complete: boolean;
    data_profile: string | null;
    sources: string[];
    executed_at: string[];
    question?: string | null;
  };
};
export type DashboardMutation = {
  dashboard: Dashboard;
  item: DashboardItem | null;
};
