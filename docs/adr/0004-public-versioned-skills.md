# Public versioned skills with analysis-scoped instructions

Status: Accepted — 2026-10-15

Visitors can manage shared Markdown playbooks without accounts, matching the public competition workspace. New skills are enabled on save. Revisions, soft deletion, transactional quotas, and optimistic concurrency provide recovery and attribution rather than an ownership boundary.

The existing planner produces a structured plan without model-controlled database tools. Preserve that pipeline: discover skill metadata in one bounded selector call, load at most three bodies, capture immutable snapshots, and supply them as subordinate task guidance to planning/repairs/interpretation. Do not attach executable `SkillToolset` scripts or expand the model's permissions. ADK sessions are scoped to an analysis so previous skill prompts cannot silently apply to later questions.

Manual conversation attachments take priority and are copied to forks. Each voice tool invocation selects independently. Answers reference immutable revisions, preserving evidence after public changes. The small catalog uses metadata selection rather than a separate vector index; retrieval remains behind a service boundary for later replacement. Public edits can affect future answers, so the UI discloses this and existing SQL/resource controls remain enforced outside the model.
