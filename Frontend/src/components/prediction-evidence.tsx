import type { Artifact } from "@/lib/types";

export function forecastMethodLabel(method: string) {
  return method === "timesfm_3" ? "TimesFM 3.0 · Preview" : method.replaceAll("_", " ");
}

export function PredictionEvidence({ prediction, reportId, reportVersion, artifactId }: {
  prediction: NonNullable<Artifact["prediction"]>;
  reportId?: string;
  reportVersion?: number;
  artifactId: string;
}) {
  const comparison = prediction.comparison;
  const label = forecastMethodLabel(prediction.method);
  return (
    <div className="report-note">
      <strong>{prediction.kind === "scenario" ? "Conditional scenario comparison" : "Observed history and predictions"}</strong>
      <p>Observed through {prediction.cutoff} · {label} · {prediction.horizon} future periods. Dashed series are predictions, not observations.</p>
      {prediction.scenario_name && <p>Scenario: {prediction.scenario_name}. Baseline and alternative use the same method and history. Historical associations do not establish causal impact.</p>}
      {prediction.selection_reason && <p>{prediction.selection_reason}</p>}
      {comparison && <p>TimesFM comparison: {comparison.status}. {comparison.reason}</p>}
      {comparison?.scope_note && <p>{comparison.scope_note} Context: {comparison.context} observations.</p>}
      <p>{prediction.interval
        ? `Nominal ${prediction.interval.level * 100}% historical residual band · backtest coverage ${(prediction.interval.coverage * 100).toFixed(1)}% · future coverage is not guaranteed`
        : "Validated prediction intervals unavailable; uncertainty is not quantified."}</p>
      {prediction.scores && (
        <details>
          <summary>Forecast validation &amp; assumptions</summary>
          <p>Chronological backtests evaluate the whole prediction horizon. MAE is average absolute error; RMSE gives greater weight to larger errors. Lower is better within the same metric. Conditional scores assume the supplied driver paths are known.</p>
          <div className="overflow-x-auto" role="region" tabIndex={0} aria-label={`Forecast method comparison ${artifactId}`}>
            <table className="w-full text-left text-sm">
              <caption>Candidate backtest errors; {label} retained.</caption>
              <thead><tr><th scope="col">Method</th><th scope="col">MAE</th><th scope="col">RMSE</th><th scope="col">Outcome</th></tr></thead>
              <tbody>{Object.entries(prediction.scores).map(([name, score]) => (
                <tr key={name}>
                  <th scope="row">{forecastMethodLabel(name)}</th>
                  <td>{score.mae.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                  <td>{score.rmse.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                  <td>{name === prediction.method ? "Selected" : "Compared"}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
          <ul>{prediction.limitations.map((item, index) => <li key={index}>{item}</li>)}</ul>
          <pre tabIndex={0} role="region" aria-label={`Prediction reproducibility details ${artifactId}`}>
            {JSON.stringify({ backtests: prediction.scores, drivers: prediction.drivers, assumptions: prediction.assumptions,
              future_drivers: prediction.future_drivers, scenario_drivers: prediction.scenario_drivers,
              libraries: prediction.libraries, data_hash: prediction.data_hash, managed_comparison: comparison }, null, 2)}
          </pre>
        </details>
      )}
      {reportId && <a className="underline" href={`/reports/${reportId}?version=${reportVersion}`}>Report version {reportVersion}</a>}
    </div>
  );
}
