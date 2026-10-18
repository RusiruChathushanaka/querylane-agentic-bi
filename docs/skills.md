# Skills library

Open `/skills` from the workspace sidebar, mobile navigation, or Settings. Skills are public Markdown playbooks: **every visitor can create, change, disable, delete, and restore them**. Guest credentials attribute edits and enforce quotas; they do not establish ownership. Saving a new skill enables it immediately. Do not enter secrets or private information.

## Authoring and recovery

Create a skill with a name, description, when-to-use guidance, source compatibility, optional tags, and Markdown instructions. Use the starter template to document purpose, workflow, business definitions, and examples. Instructions support at most 16 KiB of UTF-8 text. Names have an 80-character limit, descriptions 300, when-to-use guidance 500, and up to eight tags of 30 characters each are allowed.

The preview ignores raw HTML and never loads Markdown images or embedded remote resources. Links retain the renderer's safe URL handling and open with `noopener noreferrer`. Previews and assistant replies share a Markdown renderer supporting tables, lists, emphasis, task lists, and code blocks; visitor messages retain their literal text. Scripts, attached resources, package installation, and additional tools are not supported. Conversational AI authoring prepares a reviewable Markdown draft through **Create with voice**, as described below.

Import an individual `.md` or `.markdown` file of at most 24 KiB. Import only fills the editor; review and save it to publish. YAML frontmatter requires text `name` and `description` fields. Duplicate keys, aliases, custom object tags, malformed mappings, and oversized content are rejected. Executable declarations are never installed or activated. Export produces `SKILL.md` with a compatible slug name and description. Querylane fields round-trip under `metadata.querylane`:

```markdown
---
name: revenue-review
description: Review revenue consistently.
metadata:
  querylane:
    display_name: Revenue review
    when_to_use: Questions about revenue trends.
    source: bigquery
    tags: [revenue, reporting]
---

## Workflow
Use completed orders, preserve filters, and disclose gross versus net assumptions.
```

Every edit, status change, deletion, and restoration creates a new immutable revision. Concurrent changes return `409 skill_conflict`; the editor retains your draft until you explicitly discard or replace it. Delete offers an Undo toast, and Recently deleted supports later restoration. Version history and links from answers remain readable after deletion.

## How the agent uses skills

Automatic discovery is on by default. Attach up to three skills to a conversation through **Attach skills**; attachments are shared and copied into forks. Disabled, deleted, or source-incompatible attachments must be removed before another analysis. A busy conversation cannot change attachments.

The backend queries active skill summaries, then uses one bounded structured Gemini call to select relevant IDs from their metadata. Manual attachments take priority, with at most three skills in total. Selection may return none. Only selected instruction bodies are loaded into the model context. No extra vector index or embedding refresh is required for this bounded catalog. Local fixture mode uses an explicitly deterministic metadata matcher; it does not interpret arbitrary skill instructions as an LLM would.

Before planning or executing SQL, the service captures selected revisions under `runs/{id}/skill_snapshots/{analysis_id}`. Planning, SQL repairs, and interpretation receive the same snapshots, with ADK sessions scoped to that analysis. Each voice `analyze_data` invocation captures its own set. Answers and artifacts expose skill/version references and whether selection was manual or automatic. Follow-ups select again; retries/replay of an existing text run do not rerun selection or SQL. Library changes during an analysis do not change its captured instructions.

Skill instructions remain subordinate to the visitor's question and application policy. Conflicting definitions should produce clarification when they materially affect an answer. SQL allowlists, read-only permissions, scan budgets, source checks, and fusion validation still apply outside the model. Automatic selector failure produces a visible warning and retains valid manual attachments; it never silently switches to a fixture model.

## Backend contract

Reads are public. Writes use the existing anonymous bearer token. `PATCH` bodies carry `expected_revision`; deletion uses that value as a query parameter. The conversation attachment request is `{ "skill_ids": [], "expected_revision": 0 }`; its revision starts at zero and is independent of the conversation lease generation.

| Endpoint | Purpose |
| --- | --- |
| `GET/POST /api/v1/skills` | List summaries or create an enabled skill |
| `GET/PATCH/DELETE /api/v1/skills/{id}` | Read, update, or soft-delete |
| `POST /api/v1/skills/{id}/restore` | Restore with a revision check |
| `GET /api/v1/skills/{id}/revisions` | List version summaries |
| `GET /api/v1/skills/{id}/revisions/{revision}` | Read immutable content |
| `POST /api/v1/skills/import` | Validate and preview an import without saving |
| `GET /api/v1/skills/{id}/export` | Download `SKILL.md` |
| `PATCH /api/v1/conversations/{id}/skills` | Replace shared attachments |

`GET /skills?deleted=true` lists deleted summaries. Mutation failures do not consume a revision. Capacity and edit quotas update in the same transaction as the revision. Public responses omit internal guest attribution. Active listing uses the [Firestore equality-filter API](https://docs.cloud.google.com/firestore/docs/samples/firestore-query-filter-single-examples) and field projection to avoid loading instruction bodies during discovery.

Defaults are 100 non-deleted skills, 20 edits per guest/hour, and 100 edits per workspace/day. Configure `SKILL_CATALOG_LIMIT`, `SKILL_GUEST_HOURLY_LIMIT`, and `SKILL_WORKSPACE_DAILY_LIMIT` in the backend environment. All data stays in the existing named demo Firestore database. `reset-history` preserves the library, revision history, and capacity counter.

Operators can add two example playbooks without overwriting existing IDs, including edited or deleted examples:

```bash
cd Backend
uv run python -m app.admin seed-skills
```

This command writes to the named cloud demo database using operator credentials. Run it only when intentionally seeding that environment; routine deployment does not seed automatically. See [the deployment guide](deployment-guide.md) before cloud changes.

## Verification

The [analytics and prediction pack](analytics-skills.md) provides 24 focused playbooks, sample questions and an insert-only `seed-analysis-skills` operator command. Actual prediction fitting uses Advanced Analysis; skills preserve its validation gates and the shared three-skill budget.

Run backend pytest/Ruff and frontend lint, tests, type checks, and build. The skills tests cover CRUD, concurrency, quotas, metadata discovery, immutable snapshots, SQL repairs, malformed imports, forks, and repeated voice analysis. Browser verification and its limitations are recorded in [validation.md](validation.md).

The library is [deployed on Cloud Run](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/skills). [Hosted skills evidence](evaluation/skills-deployed.json) covers real named-Firestore revisions/conflicts, import/export, automatic and manual selection, follow-ups, forks, immutable historical evidence, persistence across a new revision, and skill-guided Gemini Live analysis. The verification playbook was soft-deleted after the checks; its used versions remain readable. See the [release validation](validation.md#skills-and-animation-cloud-release--2026-10-16) for limits and related reports.

## Conversational voice author

**Create with voice** opens a dedicated skill-building conversation. It gathers purpose, when to use, source compatibility, workflow, business definitions, and examples. Requirements appear as they are captured. The assistant can suggest metadata, prepare a Markdown draft, and refine it when you make corrections. Exact field names and categorical values should be supplied when known; review them before publication.

Speak naturally, interrupt to correct a detail, mute/unmute, or use **Continue with typing** without granting microphone access. Spoken responses/start-muted follow browser settings. Transcripts remain available alongside the requirements checklist. Pause the assistant before reviewing. Edit metadata or Markdown, check the explicit public-publication acknowledgement, and click **Publish skill**. The resulting enabled skill uses the normal library, quotas, revision history, and analytics selection pipeline. The assistant cannot publish, query databases, add tools, or generate application features.

The author saves its brief/draft and completed transcripts in a guest-scoped backend session. Closing the dialog keeps committed work; unsaved review edits require confirmation before discarding. Browser session storage retains only the author ID. Recovery requires the same guest token, and sessions logically expire after six hours. These are anonymous browser sessions, not verified identities or a confidential-data feature; do not supply private information. No raw audio is recorded.

Reconnect reconstructs context from saved requirements/draft and recent transcript under a fresh fenced connection. It does not reuse stale tool operations. Draft corrections invalidate the prior generated draft; manual review edits are preserved until you explicitly replace them or generate another draft. Stale edits or a competing connection return a conflict and preserve the local draft. Publication commits the reviewed revision and new skill atomically, so retrying a lost response creates no duplicate.

Limits: three new interviews per guest/hour and twelve workspace/day; six live connections per guest/hour and thirty workspace/day; ten minutes per live connection; 24 user turns and 24 draft/brief updates per session; 48 tool calls (including failed/no-op calls); and 64 KiB of stored transcript. Publication also obeys existing skill capacity/content/mutation limits. Configure the `AUTHOR_*` settings in [the backend environment example](../Backend/.env.example).

Expired sessions are rejected, not automatically erased. An operator can remove expired, inactive author documents and only their scoped ADK sessions with `uv run python -m app.admin cleanup-skill-authors` from `Backend/`. Published skills and revisions are preserved. Shared-history reset also clears author interviews while retaining published skills. Neither maintenance command has a public endpoint.

See the [detailed plan and contracts](voice-skill-author-plan.md) and [validation](validation.md#conversational-voice-skill-author--2026-10-16). The default fixture backend reports that Gemini is required; it never simulates a real interview. For an isolated real-model preview use `app.cloud_preview` with the documented operator credentials and a matching frontend origin. This feature has not been deployed as part of its implementation.
