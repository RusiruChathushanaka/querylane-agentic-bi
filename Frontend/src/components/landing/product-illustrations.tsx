import { ArrowUpRight, Check, FileText, MicOff, Pin } from "lucide-react";
import data from "@/lib/landing-preview-data.json";

const money = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: data.currency,
    maximumFractionDigits: 0,
  }).format(value);

/** Local saved evidence only. No chart runtime, source query, or model calls. */
export function RevenueIllustration({
  forecast = false,
  compact = false,
}: {
  forecast?: boolean;
  compact?: boolean;
}) {
  const points = forecast
    ? data.points
    : data.points.filter((p) => p.observed !== null);
  const x = (i: number) => 44 + i * (424 / (points.length - 1));
  const y = (value: number) => 190 - (value / 16_000_000) * 154;
  const observed = points.flatMap((p, i) =>
    p.observed === null ? [] : [`${x(i)},${y(p.observed)}`],
  );
  const predicted = points.flatMap((p, i) =>
    p.forecast === null ? [] : [`${x(i)},${y(p.forecast)}`],
  );
  const last = points.findLastIndex((p) => p.observed !== null);
  const forecastLine = forecast
    ? [observed.at(-1), ...predicted].join(" ")
    : "";
  return (
    <figure
      className={`landing-chart ${compact ? "landing-chart-compact" : ""}`}
    >
      <div className="landing-chart-heading">
        <span>Monthly merchandise revenue</span>
        <span>USD</span>
      </div>
      <svg
        viewBox="0 0 500 230"
        role="img"
        aria-label={
          forecast
            ? "Observed monthly revenue, January to September 2026; dashed TimesFM 3.0 Preview point forecast, October to December 2026. No validated prediction intervals."
            : "Observed monthly revenue, January to September 2026, ranging from 6.36 to 9.58 million US dollars."
        }
      >
        {[4, 8, 12, 16].map((v) => (
          <g key={v} className="landing-chart-grid">
            <line x1="44" x2="474" y1={y(v * 1e6)} y2={y(v * 1e6)} />
            <text x="4" y={y(v * 1e6) + 4}>
              ${v}m
            </text>
          </g>
        ))}
        {forecast && (
          <line
            className="landing-cutoff"
            x1={x(last)}
            x2={x(last)}
            y1="28"
            y2="193"
          />
        )}
        <polyline className="landing-observed" points={observed.join(" ")} />
        {forecast && (
          <polyline className="landing-predicted" points={forecastLine} />
        )}
        <circle
          className="landing-chart-dot"
          cx={x(last)}
          cy={y(points[last].observed!)}
          r="4.5"
        />
        {(forecast ? [0, 3, 6, 8, 11] : [0, 2, 4, 6, 8]).map((i) => (
          <text
            className="landing-chart-tick"
            key={i}
            x={x(i)}
            y="216"
            textAnchor="middle"
          >
            {new Date(points[i].date).toLocaleDateString("en-US", {
              month: "short",
              timeZone: "UTC",
            })}
          </text>
        ))}
      </svg>
      <figcaption>
        <span className="landing-legend-item">
          <i />
          Observed
        </span>
        {forecast && (
          <span className="landing-legend-item landing-legend-forecast">
            <i />
            Forecast
          </span>
        )}
        <span>2026 · saved synthetic data</span>
      </figcaption>
      {!compact && (
        <details className="landing-data-alternative">
          <summary>View chart data</summary>
          <div className="landing-table-scroll">
            <table>
              <caption>
                Saved example · USD · observation cutoff September 30, 2026
              </caption>
              <thead>
                <tr>
                  <th scope="col">Month</th>
                  <th scope="col">Observed</th>
                  {forecast && <th scope="col">Forecast</th>}
                </tr>
              </thead>
              <tbody>
                {points.map((p) => (
                  <tr key={p.date}>
                    <th scope="row">{p.date.slice(0, 7)}</th>
                    <td>{p.observed === null ? "—" : money(p.observed)}</td>
                    {forecast && (
                      <td>{p.forecast === null ? "—" : money(p.forecast)}</td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      )}
    </figure>
  );
}

export function ScenarioIllustration() {
  const points = data.scenario.points;
  const x = (i: number) => 44 + i * (424 / (points.length - 1));
  const y = (value: number) => 190 - (value / 500_000) * 154;
  const total = (field: "baseline" | "alternative") =>
    points.reduce((sum, point) => sum + point[field], 0);
  return (
    <figure className="landing-chart">
      <div className="landing-chart-heading">
        <span>Conditional daily revenue · Oct 1–14, 2026</span>
        <span>USD</span>
      </div>
      <svg
        viewBox="0 0 500 230"
        role="img"
        aria-label="Two saved conditional TimesFM revenue predictions for October 1 to 14, 2026. Dashed baseline assumes no promotion days; dotted alternative assumes promotion every day. Neither series is observed data or a causal effect. No validated prediction intervals."
      >
        {[0, 250, 500].map((v) => (
          <g key={v} className="landing-chart-grid">
            <line x1="44" x2="474" y1={y(v * 1000)} y2={y(v * 1000)} />
            <text x="2" y={y(v * 1000) + 4}>
              ${v}k
            </text>
          </g>
        ))}
        <polyline
          className="landing-scenario-baseline"
          points={points.map((p, i) => `${x(i)},${y(p.baseline)}`).join(" ")}
        />
        <polyline
          className="landing-scenario-alternative"
          points={points.map((p, i) => `${x(i)},${y(p.alternative)}`).join(" ")}
        />
        <rect
          className="landing-scenario-endpoint"
          x={x(13) - 4}
          y={y(points[13].baseline) - 4}
          width="8"
          height="8"
        />
        <circle
          className="landing-scenario-alternative-endpoint"
          cx={x(13)}
          cy={y(points[13].alternative)}
          r="4"
        />
        {[0, 6, 13].map((i) => (
          <text
            className="landing-chart-tick"
            key={i}
            x={x(i)}
            y="216"
            textAnchor="middle"
          >
            Oct {i + 1}
          </text>
        ))}
      </svg>
      <figcaption>
        <span className="landing-legend-item landing-legend-baseline">
          <i />
          Baseline · no promotion days
        </span>
        <span className="landing-legend-item landing-legend-alternative">
          <i />
          Alternative · promotion every day
        </span>
      </figcaption>
      <dl className="landing-scenario-totals">
        <div>
          <dt>Baseline predicted total</dt>
          <dd>{money(total("baseline"))}</dd>
        </div>
        <div>
          <dt>Alternative predicted total</dt>
          <dd>{money(total("alternative"))}</dd>
        </div>
      </dl>
      <details className="landing-data-alternative">
        <summary>View scenario data</summary>
        <div className="landing-table-scroll">
          <table>
            <caption>
              Saved conditional predictions · USD, rounded to dollars · Oct
              1–14, 2026
            </caption>
            <thead>
              <tr>
                <th scope="col">Date</th>
                <th scope="col">Baseline</th>
                <th scope="col">Alternative</th>
              </tr>
            </thead>
            <tbody>
              {points.map((p) => (
                <tr key={p.date}>
                  <th scope="row">{p.date}</th>
                  <td>{money(p.baseline)}</td>
                  <td>{money(p.alternative)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </figure>
  );
}

export function HeroProduct() {
  return (
    <div
      className="landing-product"
      role="group"
      aria-label="Illustrative composition of Querylane using saved retail evidence"
    >
      <div className="landing-product-top">
        <span className="landing-product-dot" />
        QUERYLANE / ANALYSIS <span>Saved example</span>
      </div>
      <div className="landing-question">
        <span className="landing-initial">Q</span>
        <p>What happened to sales—and what could come next?</p>
        <MicOff size={17} aria-hidden />
      </div>
      <div className="landing-document">
        <div className="landing-document-top">
          <span>
            <FileText size={15} aria-hidden /> RETAIL PERFORMANCE
          </span>
          <span>01 / INSIGHTS</span>
        </div>
        <h2>
          A clearer picture.
          <br />A better next question.
        </h2>
        <p>From 45 months of history to evidence and TimesFM forecasts.</p>
        <div className="landing-metric-pair">
          <div>
            <span>Total orders</span>
            <strong>573,348</strong>
          </div>
          <div>
            <span>Overall order value</span>
            <strong>$618.17</strong>
          </div>
        </div>
        <RevenueIllustration forecast compact />
        <div className="landing-evidence-line">
          <Check size={14} aria-hidden /> SQL &amp; source evidence{" "}
          <span>Jan 2023–Sep 2026</span>
        </div>
      </div>
      <div className="landing-pin-note">
        <span className="landing-pin-icon">
          <Pin size={17} aria-hidden />
        </span>
        <div>
          <strong>Keep the insight in view</strong>
          <span>Pin saved results to a shared dashboard</span>
        </div>
        <ArrowUpRight size={17} aria-hidden />
      </div>
      <p className="landing-product-caption">
        TimesFM 3.0 · Preview · saved synthetic example · cutoff Sep 30, 2026 ·
        no validated intervals
      </p>
    </div>
  );
}
