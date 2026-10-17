# Advanced reports use independent durable execution and immutable evidence

Status: Accepted — 2026-10-17

Reports can outlive a browser request and must not reserve the ordinary conversation lease. A separate Cloud Tasks/private Cloud Run worker uses transactional outbox admission, fenced leases, ordered events and application-stage checkpoints in the named database. The public backend never exposes the internal worker handlers. OIDC invoker permission belongs to the dispatch identity only on that worker.

ADK App/Runner/Workflow coordinates specialist roles, while deterministic functions own SQL execution, calculations and publication. A shared plugin bounds all model calls. Experimental ADK invocation resumption is not the durability boundary. Application workflow versions prevent incompatible checkpoint recovery after a release.

A Report names a family of immutable revisions. Reanalysis creates new evidence; presentation revisions reuse prior artifacts. Shared metadata edits use optimistic revision checks and recoverable deletion. Anonymous attribution does not establish a private ownership boundary.

Report references independently retain evidence and ADK sessions through chat reset. Explicit expired-report purge releases only report-owned references; dashboard pins continue protecting their artifacts. Source databases and Skills are never reset or reseeded as part of report deployment.
