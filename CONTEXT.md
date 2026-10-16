# Agentic BI

A shared workspace for asking business questions across retail data sources and inspecting the evidence behind each answer.

## Language

**Skill**: A publicly editable Markdown playbook with discovery metadata, business definitions, and analytical guidance. It adds no tools or executable code.

**Skill Author Session**: A guest-scoped, expiring interview that captures requirements, transcripts, and an unpublished draft. It is separate from public analytics conversations.

**Skill Draft**: Editable playbook content prepared from an interview; unavailable to analytics until the visitor explicitly publishes it.

**Skill Publication**: An atomic transition from one reviewed draft revision to one enabled shared skill and its immutable first revision.

**Skill Revision**: An immutable saved version, retained after edits, disabling, and deletion so historical evidence remains readable.

**Skill Attachment**: A shared conversation preference that asks the agent to apply a particular skill, subject to source compatibility and availability.

**Skill Snapshot**: The exact selected revisions captured for one analysis, including automatic/manual selection, reused for planning, repairs, and interpretation.

**Data Source**: A database or analytical warehouse whose retail data can be queried in the workspace.
_Avoid_: Application database, data lake

**Data Profile**: An operator-selected source contract: the original `legacy` demo or the additional `timeseries` sales tables and `retail_timeseries` PostgreSQL schema. It is not a browser preference.

**Retail Data Bundle**: A versioned, reproducible set of typed Parquet source files, schema, checksums, and reconciliation ledger. Extending its as-of end adds sales and late-arriving refunds without changing old records.

**Merchandise Revenue**: In the time-series profile, sales after discounts and before refunds, tax, and shipping. `gross_sales` is the separate before-discount amount.

**Refund Date**: The date a refund was processed. It differs from the original order date; net revenue must state which date window or purchase cohort is used.

**Connection**: An administrator-configured association between the workspace and a data source.
_Avoid_: User account, login

**Schema Snapshot**: A versioned description of a source's available tables, columns, and business meanings.
_Avoid_: Database copy

**Conversation**: A public sequence of questions, answers, and result references that supports follow-up exploration.
_Avoid_: Private chat, session

**Guest**: An anonymous visitor who can contribute to public conversations.
_Avoid_: Registered user, member

**Analysis Run**: One attempt to answer a question using a particular conversation's context.
_Avoid_: Conversation, query

**Relationship Hypothesis**: An inferred correspondence between data in different sources, supported by stated evidence and uncertainty.
_Avoid_: Verified foreign key, guaranteed relationship

**Result Artifact**: An immutable analytical result with its visualization, source evidence, and assumptions.
_Avoid_: Dashboard, raw model response

**Fork**: A new conversation that retains a completed prefix of another conversation and its immutable result references.
_Avoid_: Edit, duplicate result

**Gross Revenue**: Completed-order revenue before refunds, denominated in USD for the synthetic retail demo.
_Avoid_: Net revenue, profit

- **Chart Presentation**: A bounded view of an immutable Result Artifact. Range selection, Top N, and sampling change display only; summaries use the full selected saved rows, and CSV exports all saved rows.
- **Measure Metadata**: Validated units, rate scale, additivity, and comparator relationships used for formatting and factual chart insights; it cannot authorize queries or tools.

**Dashboard**: A named, publicly editable collection of saved analytical cards. Opening it does not refresh its source data.
_Avoid_: Live report, private workspace

**Dashboard Item**: One retained artifact reference and its validated saved chart view, display title/note, width, and position within a dashboard. Unpinning removes this card, not its result.
_Avoid_: New query, copied dataset

**Saved Chart View**: A versioned presentation choice over an immutable artifact: chart family, range, measures, order, axes, highlights, and precision. Temporary exploration becomes shared only after an explicit save.
_Avoid_: SQL filter, current database snapshot

**Retained Artifact**: A result protected from history cleanup while an active or recoverable dashboard item references it. Its saved pages, query evidence, assumptions, and skill references remain inspectable after the original chat is removed.
_Avoid_: Refreshed result, duplicated rows
