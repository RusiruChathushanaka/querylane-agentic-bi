# ADR 0012: Adaptive, coherent revenue planning

Accepted 18 October 2026 for local implementation; deployment is separate.

The retail hierarchy has 224 leaves, exceeding the independent-report target budget. Use aggregate modeling plus explicit trailing-history leaf allocations, with both geographic and product views anchored to one company total. Backtest the complete reconciliation procedure and retain a coherent baseline unless the policy's improvement gates pass.

Give Forecast Plans a frozen, bounded 128-fit profile without raising report ceilings, TimesFM target/job limits or shared daily/concurrency allowances. Keep TimesFM as a candidate provider, not a reconciliation engine. Point forecasts avoid unsupported joint uncertainty claims. Separate user planning adjustments from learned scenarios and retain original statistical predictions in immutable versions.
