# Error handling and retry audit — 17 October 2026

**Historical local checkpoint.** No deployment or push occurred during this audit stage; the larger hosted `timeseries` dataset and serving revisions were untouched then. The fixes were subsequently deployed and tested in [the resilience release](resilience-deployed.md). [Machine-readable evidence](error-resilience-20261017.json) records scope, source hashes, results and limitations. [The policy](../error-handling.md) documents the resulting behavior.

## Findings and changes

1. **Incomplete model retries/error normalization.** Rate limits, transport errors and some permanent provider failures escaped the existing policy. Structured calls now normalize safe errors, retry recognized transient failures once with jitter, honor short numeric Retry-After, and fail fast on permanent errors. Long/invalid/date Retry-After skips automatic retry rather than retrying early. Cancelled calls and programming failures are not retried. ADK status events use the same mapping; raw provider message bodies are no longer logged there. The selected model and report budget plugin remain unchanged. Embeddings have a ten-second single-attempt deadline and the existing explicit schema fallback.
2. **Voice tool failures ended the whole session.** Expected analytical failures now produce structured tool results and a nonfatal notification. The assistant can explain the problem and continue; stale ownership, cancellation and unexpected failures remain fatal. No application retry automatically reexecutes a failed SQL query.
3. **Voice stop could abandon source work.** Normal stop/session-limit cleanup now requests database cancellation too. A deterministic threaded test additionally reproduced billed BigQuery submission after cancellation/registry cleanup during a delayed dry run. A thread-held cancellation Event now survives cleanup and prevents that late submission; a job returned during cancellation is cancelled. This does not claim every database job has reached a terminal state.
4. **Cleanup failures could leak local state.** Voice client-close errors cannot leak the active conversation context. Storage failures during ordinary finalization or report cleanup cannot retain local task/model/lease context. Author transcript-flush failure cannot bypass the release attempt.
5. **Browser recovery gaps.** Malformed Live messages are handled safely; late ready events cannot revive a stopped client. JSON calls have a body-inclusive deadline, safe non-JSON gateway errors and caller cancellation. Corrupt/blocked guest storage has an in-memory fallback; concurrent stale 401s preserve newly refreshed identity. Mutations never replay after an ambiguous network failure. Event streams release readers, retain successfully delivered cursors, have an idle deadline, deliver saved terminal status and surface exhausted reconnect attempts.
6. **Permanent report model failures retried as generic server errors.** Worker redelivery now excludes permanent model errors. Transient recovery still carries existing budgets/checkpoints, with the three-delivery cap. Tests retain checkpoint reuse, cancellation ownership and fenced publication.
7. **Malformed voice handshakes could escape the boundary.** Non-object handshakes and disconnects now return/close safely without assuming a dictionary or an open socket. Unexpected setup/storage failures return a safe error rather than escaping the WebSocket boundary.

## Verification

| Check | Result |
| --- | --- |
| Initial structured/voice fault-injection suite | 9 failed / 3 passed, demonstrating the pre-fix gaps |
| Initial API/voice client seam tests | 5 failed / 11 passed |
| Delayed BigQuery cancellation race | Failed before the Event fix; passed after |
| Full backend suite | **340 passed, 1 existing skip**, 43.98 seconds |
| Focused model checks before the final full suite | **28 passed** |
| Full frontend suite | **44 passed** |
| Backend Ruff | Passed from `Backend/` |
| Frontend lint, TypeScript, production build | Passed; production build used an isolated output directory |
| Loaded Chromium: normal fixture analysis | Monthly chart rendered |
| Loaded Chromium: blocked submission | Safe banner/toast; draft retained; submit reenabled |
| Loaded Chromium: restored submission | Regional result rendered; exactly two user messages, with no failed-submit replay |
| Loaded Chromium: microphone denial | Simulated denial visible; controls removed; text chat usable |
| Loaded Chromium: corrupt guest cache | Malformed sessionStorage recovered after reload/submission; result rendered once |
| Final reloaded browser | No uncaught page errors recorded |

The existing skip is the independent-client durability variant requiring the Firestore emulator. The existing Starlette/httpx deprecation warning remains. Real source/model calls were not required: SDK status/transport failures, storage failures, worker delivery decisions, cancellation timing and browser handlers were injected at their actual application seams. The full suites retain SQL/fusion limits, skill provenance, report checkpoints, dashboard retention and export checks.

The sandboxed build stalled and was stopped; the unrestricted isolated production build completed successfully. Next.js-generated temporary TypeScript include entries were restored after testing. The test browser and servers were closed; the pre-existing local service on port 8011 was left untouched. No cloud deploy, source-data write, IAM change, history/quota reset or GitHub push occurred.

## Boundaries

This audit does not certify every possible provider outage, platform or failure ordering. No real Gemini outage, physical microphone/speaker test, Safari/Firefox run, full screen-reader test, Firestore emulator run or production Cloud Tasks crash/redelivery injection was performed. Upstream unacknowledged Live tool delivery is not an exactly-once contract. Source cancellation is requested and bounded by existing timeouts; terminal confirmation remains explicit. The native Graphify graph is the preceding dated snapshot; the architecture and curated Mermaid diagram describe these local changes.

I checked Modern Web Guidance's WebSocket/cancellation search and catalog; no directly applicable guide was returned, so no new guide-specific browser pattern was applied. SDK behavior was checked against current Context7 ADK documentation and the installed Google ADK 2.12.0 / GenAI 2.31.0 source.
