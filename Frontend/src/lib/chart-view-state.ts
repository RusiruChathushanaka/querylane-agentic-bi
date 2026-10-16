import type { Artifact } from "./types";
import type { Preferences } from "./preferences";
import type { ChartViewState } from "./dashboard-types";

export function initialChartView(
  artifact: Artifact,
  preferences: Preferences,
  view: string,
): ChartViewState {
  const measures = artifact.visualization.measures ?? [];
  return {
    version: 1,
    view,
    start: null,
    end: null,
    primary:
      measures.find((m) => m.role === "primary")?.field ??
      artifact.visualization.y[0] ??
      null,
    visible_measures: measures.length
      ? measures
          .filter(
            (m) =>
              preferences.chartComparisons ||
              !["target", "comparison"].includes(m.role),
          )
          .map((m) => m.field)
      : artifact.visualization.y,
    order: "value_desc",
    top: 10,
    scatter_x: null,
    scatter_y: null,
    highlights: preferences.chartHighlights,
    decimals: Number(preferences.decimals) as 0 | 1 | 2,
  };
}
export function describeChartView(state: ChartViewState) {
  const scope =
    state.start || state.end
      ? `${state.start || "Start of saved result"} → ${state.end || "End of saved result"}`
      : "Full saved date scope";
  return `${state.view.toUpperCase()} · ${scope} · ${state.visible_measures.join(", ") || "Saved table columns"}${["bar", "pie"].includes(state.view) ? ` · Top ${state.top}, ${state.order.replaceAll("_", " ")}` : ""}`;
}
