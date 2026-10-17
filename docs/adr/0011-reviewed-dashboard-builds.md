# ADR 0011: Reviewable dashboard generation using shared durable execution

Accepted 18 October 2026 for local implementation; deployment is separate.

AI dashboard generation may reuse matching saved evidence and perform bounded missing analyses. It produces a guest-owned proposal. Only an explicit application action publishes its atomic dashboard change set, against the captured dashboard revision.

Reuse the report worker/outbox/checkpoints and shared quotas instead of a request-local task or additional infrastructure. Preserve old report workflows. Dashboard reads/exports never execute analytics. Conflicts retain generated evidence; reviewed rebase and conditional Undo prevent overwriting public edits. Expiring retention references preserve unpublished reused evidence through history reset.
