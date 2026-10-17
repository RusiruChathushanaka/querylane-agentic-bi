# Deployed error-handling and retry release — 17 October 2026

The resilience fixes are deployed and verified against the existing larger retail dataset. This assessment follows the earlier [local fault-injection checkpoint](error-resilience-20261017.md); that checkpoint's zero-cloud-operation record remains historical.

## Serving release

| Component | Serving revision | Previous revision |
| --- | --- | --- |
| Public API | `agentic-bi-backend-00019-kwg` | `agentic-bi-backend-00018-ctv` |
| Private report worker | `agentic-bi-report-worker-00008-xwl` | `agentic-bi-report-worker-00007-pfq` |
| Frontend | `agentic-bi-frontend-00014-8p8` | `agentic-bi-frontend-00013-hrz` |

All three receive 100% traffic. Backend and worker use the same verified backend digest. Both Cloud Builds succeeded; image-only candidates were created with no traffic, checked for readiness and unchanged runtime specifications, then promoted by exact revision name. [Backend](resilience-release-backend.json), [worker](resilience-release-report-worker.json), [frontend](resilience-release-frontend.json) and [configuration](resilience-configuration.json) retain the actual build/revision evidence. [deployment.json](../deployment.json) records image digests and rollback references.

Images were built from the working tree over `598b72f78020c9116051a87ca1424b9965810dd3`, before the publication commit. The [source manifest](resilience-release-source.json) captures 151 application files and seven build/configuration files; all hashes still match after verification. Publication includes this exact application source and the subsequent documentation/smoke script. No application runtime source changed after its image build.

## What changed

- Safe model failure classification and one bounded retry for recognized transient structured-call failures. Permanent errors fail fast; SDK retries do not multiply the application policy. Embeddings have a bounded deadline and explicit schema fallback.
- Expected analytics tool failures return structured Live errors without ending the session. A fresh question can succeed in that connection. Voice frames, source SQL and ambiguous mutations are not automatically replayed.
- Every analyst voice exit requests source cancellation. Thread-held cancellation flags prevent late BigQuery submission after a cancelled dry run, even when local registry state has been removed.
- Context/task cleanup survives storage or transport finalization failures. Permanent report model errors do not trigger generic worker redelivery.
- Browser JSON and SSE operations have deadlines, safe gateway errors, bounded reconnect/replay, cancellation and visible exhaustion. Guest-cache recovery preserves refreshed tokens; malformed/late Live events cannot revive a stopped client.

See the complete [error-handling policy](../error-handling.md) and [local reproduction details](error-resilience-20261017.md).

## Verification

| Check | Outcome | Evidence |
| --- | --- | --- |
| Local backend | 340 passed, one existing emulator-dependent skip; Ruff passed | [Local audit](error-resilience-20261017.json) |
| Local frontend | 44 passed; lint, TypeScript and production build passed | [Local audit](error-resilience-20261017.json) |
| Public health/runtime URL/private worker | 6/6 passed; worker anonymous request rejected with 403 | [Health](resilience-health.json) |
| Hosted analytics and source evidence | 40/40 passed | [Analytics](resilience-timeseries-deployed.json) |
| Repeated Live tool analysis | 4/4 passed | [Live turns](resilience-voice-turns-deployed.json) |
| Expected Live tool failure and recovery | 7/7 passed | [Recovery](resilience-voice-recovery-deployed.json) |
| Conversational skill author | 5/5 passed | [Author](resilience-author-live.json) |
| Spoken browser analytics | 9/9 passed | [Speech](resilience-browser-speech.json) |
| Browser permission denial and reconnect | 3/3 passed | [Reconnect](resilience-browser-reconnect.json) |
| Durable reports, predictions and integrations | 26/26 passed | [Reports](resilience-reports-deployed.json) |
| Saved report reader/version switch | 7/7 passed | [Reader](resilience-report-browser.json) |
| Report reader automated accessibility | Zero axe violations; manual-review items retained | [Axe](resilience-report-browser-a11y.json) |

The normal analytics suite exercises Gemini 3.8 Flash and Gemini 3.5 Flash-Lite, complete 45-month and 1,369-day series including the zero-sales date, follow-ups, cross-source analysis, saved CSV, idempotency/forks/replay, and authentication/origin rejection. Daily and monthly merchandise revenue reconcile independently to **USD 354,425,112.20**.

The Live recovery test creates one clearly marked probe skill, attaches and disables it, receives a nonfatal `skill_unavailable`, reenables that probe, then sends a fresh question in the same connection. The answer returns **573,348** completed orders and spoken audio. Stop releases the analysis; the probe is soft-deleted in cleanup. No existing skill is edited. The reusable `Backend/scripts/smoke_voice_recovery.py` command and its side effects are documented in the [runbook](../deployment-guide.md#acceptance-checks).

Browser speech uses synthetic PCM as the microphone input while exercising the actual AudioWorklet, WebSocket, hosted Gemini Live, SQL and result rendering. Two questions in one connection return **573,348** all-history and **152,694** 2024 orders with distinct query jobs and single saved user/spoken transcripts. Mute disables the track, unmute reenables it, stop ends it, simulated microphone denial is visible, and reconnect reaches readiness without model errors. This is not a physical microphone/speaker quality test. The author test uses real model audio, saves a brief and review draft, acknowledges stop, and leaves the draft unpublished.

The report suite completes through the private task worker while ordinary chat stays usable. It validates a reviewed report, three-step monthly ETS point predictions from the **2026-09-30** observation cutoff, three chronological backtest folds and explicit absence of validated prediction intervals. PDF, Word and data ZIP checksums/version references reconcile with immutable evidence. Technical presentation revision, event replay, dashboard pin/retention, deletion/restoration and initiating-guest-only confirmed cancellation pass. The report-version UI was rechecked after correcting an assertion that incorrectly required an `aria-label` instead of the native select's associated label; no application fix was necessary.

## Dataset and configuration preservation

[Before](resilience-source-before.json)/[after](resilience-source-after.json) metadata and [preservation assertions](resilience-source-preservation.json) confirm identical BigQuery row counts, bytes, schemas and last-modified timestamps:

| Table | Rows |
| --- | ---: |
| `sales_orders` | 573,348 |
| `sales_order_items` | 1,317,941 |
| `sales_products` | 200 |
| `sales_returns` | 97,122 |
| `calendar` | 1,369 |

The profile spans January 2023–September 2026. Hosted cross-source analysis reads the complete **25,000-customer** PostgreSQL dimension in `retail_timeseries`. Backend and worker retain **`DATA_PROFILE=timeseries`**, **`SOURCE_ROW_LIMIT=30000`**, Cloud Tasks dispatch, model IDs, origins, workload identities, secrets, resource/concurrency/deadline settings and existing query/fusion controls.

No source upload/seed, schema migration, IAM/secret change, history reset, quota reset or new infrastructure occurred. Verification creates public conversations, reports, saved artifacts and a dashboard as normal product operations; it does not clear existing visitor history. The worker remains private, the queue RUNNING and the scheduled reconciler ENABLED. Search research remains disabled.

## Log observations

The [sanitized log record](resilience-runtime-logs.json) includes three ERROR traces from the deliberate owner-cancellation test, with no unexpected application ERROR entries in the inspected window. It also records deliberate 401/403/409 guard tests.

One private reconciler request returned **429** at 08:02:04 UTC because Cloud Run worker capacity was occupied. The **next scheduled minute returned 200**, as did all subsequent recorded invocations through 08:10 UTC. This is scheduled recovery, not evidence of an immediate HTTP retry. Existing capacity limits were preserved. A busy worker can delay reconciliation; the outbox, scheduled rechecks and task/checkpoint policies remain necessary. This finite log review is not continuous monitoring or proof of unlimited availability.

## Inspectable output

- [Business report, version 1](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/4cdb492ffa39d745be7c53c00ebc25c1?version=1)
- [Technical presentation, version 2](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/4cdb492ffa39d745be7c53c00ebc25c1?version=2)
- [Saved report dashboard](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards/4e1c7b1bea5c48b283542c66b1da3762)

## Boundaries

Recognized provider failures, race orderings, delayed dry runs and cleanup failures were injected locally, not by disrupting production. Successful hosted calls do not replace fault-injection tests. No real provider outage, production worker crash/redelivery injection, new emulator run, physical audio test, Safari/Firefox or full screen-reader verification was performed. Upstream unacknowledged Live delivery is not guaranteed exactly once; database cancellation remains a request with explicit terminal confirmation. The existing emulator-dependent skip and Starlette/httpx warning remain.

Previous dashboard export/UI acceptance and historical failed assessments retain their dated scope; this release reruns report dashboard integration, not every dashboard download format. Native `graphify-out/` remains the preceding dated extraction, while the curated architecture Mermaid views are synchronized. No raw audio, guest credentials, downloaded report binaries or generated data bundles are committed.
