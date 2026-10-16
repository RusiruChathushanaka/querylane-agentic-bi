# Shared dashboards reference immutable results and validated views

Status: Accepted — 2026-10-16

Dashboards are publicly readable and editable, matching the application's existing account-free workspace. Anonymous guest credentials provide attribution and quotas, not ownership. Revision checks and recoverable removal address accidental clashes; they do not claim to stop an authorized public visitor from changing a board.

Cards reference immutable paginated artifacts and persist a typed chart view. Several dashboards can share one result without copying rows. Viewing, pinning, rearranging and removing cards have no connector or model access. An updated analysis produces a different artifact; source refresh and global filters require a separate future design. Independent source query timestamps remain visible.

The same chart renderer serves conversations and dashboard cards. A versioned view captures scope, primary/visible measures, sorting/Top N, scatter axes, highlights and precision. Saved dashboard defaults override browser chart defaults; visual theme and motion remain local. Unsupported configuration is rejected rather than converted into executable chart expressions.

A retained-reference count includes active and recoverable cards, so unpin and soft deletion do not break Undo. History reset and expired-record purge run behind an operator maintenance fence checked transactionally by dashboard mutations and new analytics/author leases. Reset preserves referenced artifact metadata/pages, dashboards and Skills. Failed maintenance remains fenced until inspected and explicitly recovered. No cleanup runs implicitly during application startup or deployment.
