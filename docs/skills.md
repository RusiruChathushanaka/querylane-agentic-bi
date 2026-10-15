# Skills library

Open `/skills` from the workspace sidebar, mobile navigation, or Settings. Skills are public Markdown playbooks: **every visitor can create, change, disable, delete, and restore them**. Guest credentials attribute edits and enforce quotas; they do not establish ownership. Saving a new skill enables it immediately. Do not enter secrets or private information.

## Authoring and recovery

Create a skill with a name, description, when-to-use guidance, source compatibility, optional tags, and Markdown instructions. Use the starter template to document purpose, workflow, business definitions, and examples. Instructions support at most 16 KiB of UTF-8 text. Names have an 80-character limit, descriptions 300, when-to-use guidance 500, and up to eight tags of 30 characters each are allowed.

The preview ignores raw HTML and never loads Markdown images or embedded remote resources. Links retain the renderer's safe URL handling and open with `noopener noreferrer`. Scripts, attached resources, package installation, additional tools, and AI-assisted skill authoring are not supported.

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

Run backend pytest/Ruff and frontend lint, tests, type checks, and build. The skills tests cover CRUD, concurrency, quotas, metadata discovery, immutable snapshots, SQL repairs, malformed imports, forks, and repeated voice analysis. Browser verification and its limitations are recorded in [validation.md](validation.md).
