# Startup feedback and resource loading

Querylane renders its frontend shell before browser-side API reads. Application pages then resolve the existing shared `/api/config` promise and load independent resources concurrently. There is no serial readiness probe and no artificial frontend/backend startup handshake. The landing page still makes no backend, guest-session, microphone or model calls before application entry.

## Visible states

`ResourceFeedback` provides a polite status announcement, a slow-response message after five seconds, and a resource-specific Retry button. Navigation remains available. Existing library/card skeletons and decorative placeholders reserve space while data is pending; zero counts and empty-library messages require a successful response. A refresh failure retains previously loaded content and explains that refreshing failed. Retrying does not reload the page, clear typed questions, change saved preferences or discard authoring drafts.

The shared hook covers public explorations, source availability, report configuration, dashboard/report/metric/skill/forecast libraries, saved readers and versions, dashboard build history/proposals/model choices, saved chart previews and model settings. Optional planning skills use the same feedback and initial-read retry policy. Local settings remain independent from the model catalog. The API being reachable does not establish that BigQuery or PostgreSQL is available: source-specific results retain that distinction.

The workspace loads history, source checks and report configuration separately. A valid deep-linked conversation starts alongside them. Messages appear before saved result cards; each missing card has its own loading/error/retry state. Source-dependent actions require the selected sources to be available; a history failure does not block a new question. Unavailable report configuration is an explicit recoverable failure, not a claim that reports are disabled.

## Read policy

- Each JSON request keeps its existing 30-second deadline, including the response body.
- Initial idempotent GETs receive one automatic retry after at least one second for interrupted connections, timeout or HTTP 408/502/503/504. Invalid successful JSON and invalid configuration are not treated as transient network failures.
- HTTP 429 is not automatically retried. `Retry-After` seconds or HTTP dates establish a cooldown for both manual retry and polling. A server-provided delay also extends a transient retry's minimum wait.
- Initial failure after the permitted retry stops polling until explicit retry. Once a resource has succeeded, background refresh can continue without hiding its data.
- A resource has at most one pending read. Polling skips pending work; manual retry aborts and replaces it. Navigation/key changes abort old reads, and generation/signal checks reject stale responses even when a transport ignores cancellation.
- Mutation retries, guest credential recovery, execution streams, query/model budgets and inference behavior remain unchanged. An ambiguous guest-session POST is never replayed by the initial-GET policy.

BigQuery and PostgreSQL availability checks execute concurrently with `asyncio.gather`. Response order, source metadata, individual failure results and existing connector deadlines are preserved. The expensive readiness endpoint is not added to frontend startup.

## Warm frontend/API policy and release boundary

The routine-release helper uses a **service-level frontend and API minimum of one** (`--min 1`), preserving a higher existing service minimum. Existing service/revision ceilings are not reset. Frontend and API billing modes, resources and existing ceilings are preserved; the private worker helper is unchanged. A positive revision-level frontend/API minimum requires operator review before combining scaling policies. See [deployment guidance](deployment-guide.md#startup-latency-and-warm-api-policy).

The [22 October UTC hosted release](evaluation/workspace-loading-release-20261022.md) verified service minima one on frontend and API; the private worker remains unchanged. With the currently recorded one CPU, 2 GiB and instance-based billing, a continuously warm API incurs CPU/memory charges while idle. Startup CPU boost, resource limits, identities, larger-data profile and verified TimesFM gates remain part of release preservation checks. No keepalive schedule is introduced. Service replacements, deployments and scale-out can still cause delays; the frontend minimum reduces first-HTML scale-from-zero exposure.

## Verification

See [the local startup assessment](evaluation/startup-loading-local-20261021.md) for controlled delayed/error response tests, browser checks, timing methodology and limitations. The subsequent [hosted assessment](evaluation/workspace-loading-release-20261022.md) records deployment, desktop/mobile checks, immutable downloads and mixed HTTP timings without claiming a universal speedup.

## Workspace containment and nearby charts

The header, desktop sidebar and composer remain inside the viewport-sized `/app` shell. Only conversation/history content scrolls. Hidden chart instructions have positioned figure containers; they remain accessible without extending the document. Automatic following uses conversation `scrollTop`, never ancestor-scrolling `scrollIntoView`. Scrolling upward pauses following, Jump to latest resumes it, and observers/animation frames are cleaned up on unmount. Browser scroll anchoring preserves the reading location as nearby content resolves.

At narrow unzoomed widths the shell follows Visual Viewport height/offset, with dynamic viewport fallback, safe-area padding and bounded textarea height. Chart metadata and rendering begin within 150px of the conversation viewport; text is independent, placeholder space is reserved, shared saved-result reads remain capped at two and unchanged poll JSON retains state identity. No mutable-resource persistent cache was added. Individual CSV/PNG exports retain their existing complete-evidence contract; whole-conversation printing is not a new export feature. See [local layout/performance evidence](evaluation/workspace-layout-local-20261022.md).
