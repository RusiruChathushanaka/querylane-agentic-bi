# Error handling, retries and voice recovery

This policy is deployed in the 17 October 2026 [resilience release](evaluation/resilience-deployed.md). The [local fault-injection audit](evaluation/error-resilience-20261017.md) and hosted evidence distinguish injected provider/transport failures from real AI and voice checks. [deployment.json](deployment.json) records serving revisions, source hashes and unchanged runtime/data configuration.

## Failure boundaries

| Path | Policy and recovery |
| --- | --- |
| Structured Gemini calls | At most two attempts total. Retry transient HTTP/status events (including 429), recognized network failures and timeouts once, with jitter. A numeric Retry-After of up to five seconds is honored; a longer, date-formatted or invalid value stops automatic retry. |
| Permanent model failures | Authentication/access/model-location failures and invalid requests fail fast with safe application errors. Programming errors and cancellation are not retried. No model substitution. |
| Model deadlines | Each structured generation retains a 45-second HTTP timeout and 55-second invocation deadline. The existing overall analysis/report deadlines still bound aggregate work. SDK HTTP retries remain disabled for these calls so retry layers do not multiply. |
| Embeddings | Ten-second HTTP deadline, one SDK attempt; ordinary schema retrieval falls back explicitly to the full bounded schema. Administrative indexing surfaces failure instead of claiming success. |
| SQL | No new automatic source-query replay. Only invalid/unsafe generated SQL enters the existing maximum-two-repair path. Source permissions, scan/row/byte limits and timeouts are unchanged. |
| Query cancellation | Every analyst voice exit requests cancellation, including normal stop and session limit. A thread-held BigQuery cancellation Event survives registry cleanup, preventing a delayed dry run from launching a new billed query; jobs returning during cancellation are cancelled. A cancellation request does not prove the database job is terminal. |
| Analyst voice tools | Expected AppError failures and analysis deadlines return a safe structured tool error and a nonfatal browser notification. The model is instructed to explain the limitation and wait for the visitor rather than automatically repeat the failed analysis. Stale ownership/cancellation and unexpected failures still end the session. |
| Voice transport | No application retry loop replays microphone frames, text frames or analytical calls. Live error codes are classified for actionable feedback. Reconnect is explicit and uses the existing session-resumption/durable-context mechanisms. This does not promise exactly-once provider delivery of an unacknowledged Live tool call. |
| Browser voice | Malformed server messages stop safely; late ready/audio events cannot reactivate a stopped client. A graceful author pause still accepts final transcript/draft acknowledgements. Microphone tracks and audio contexts are released on failure; asynchronous close rejection is contained. |
| Browser JSON API | Thirty-second deadline covers headers and JSON reads. Non-JSON gateway errors retain status with safe fallback text. Caller abort is preserved. Mutations are not retried on ambiguous network failures. A rejected guest token can refresh once before replaying the authenticated request. |
| Guest credentials | Corrupt or blocked session storage falls back to bounded in-memory credentials. Concurrent stale 401 responses cannot evict another request's fresh token. Tokens still provide attribution, not private accounts. |
| Ordinary event stream | Four connection attempts replay persisted events after the last successfully delivered cursor. Forty-five seconds without bytes aborts a stalled connection (the server sends keepalives every fifteen seconds). EOF checks saved run status; terminal state is delivered, exhaustion is visible, and readers/timers/listeners are released. No query is restarted. |
| Durable reports | Existing outbox, fencing, checkpoints, three-delivery cap and shared budgets remain authoritative. Model-call retries pass through the budget plugin. Transient failures can redeliver; permanent model-access/invalid-request errors cannot trigger another worker delivery. Writing can retain the established verified-evidence fallback. |
| Persistence cleanup | Ordinary tasks clear their local registry even if finalization storage fails; leases then expire. Report model/lease context resets even if a cleanup read fails. Voice author flush failure cannot prevent release from being attempted. |
| Shared libraries / downloads | Existing optimistic revision conflicts, saved-result exports, recoverable deletion and explicit error feedback remain covered by regression suites. Conflict or export failure does not trigger a hidden mutation/query retry. |

Retries can consume another model request and additional time; they are not guarantees of successful completion. Two source queries still do not share a distributed database snapshot. Cloud Tasks delivery and upstream live transport are not exactly-once systems.

## Implementation and regressions

- `Backend/app/model_errors.py`: shared safe classification and bounded delay policy.
- `Backend/app/ai.py`: tool-free structured retries, event normalization and embedding deadline.
- `Backend/app/voice.py`, `skill_author_voice.py`: analyst/author error boundaries and resource cleanup.
- `Backend/app/connectors.py`: thread-held cancellation flags; existing stable query identities retained.
- `Backend/app/analysis.py`, `report_engine.py`: cleanup/finalization and durable worker retry decisions.
- `Frontend/src/lib/api.ts`, `voice.ts`: request/stream/credential/voice recovery.
- `Backend/tests/test_ai_resilience.py`, `test_reports.py`, `test_api.py`: injected provider, thread, storage, lease, handshake and retry tests.
- `Frontend/tests/api-recovery.test.mjs`, `voice-preferences.test.mjs`: bounded reconnect, cursor replay, concurrent 401, malformed frames and audio cleanup.

Run the backend checks from `Backend/` and frontend checks from `Frontend/` using the [README commands](../README.md#verify). Authorized hosted verification additionally follows the [deployment guide](deployment-guide.md); do not replace failure-injection coverage with a successful model probe. Preserve `timeseries` and the worker's dispatch configuration when a release is requested.
