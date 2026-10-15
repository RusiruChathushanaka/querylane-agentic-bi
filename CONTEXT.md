# Agentic BI

A shared workspace for asking business questions across retail data sources and inspecting the evidence behind each answer.

## Language

**Skill**: A publicly editable Markdown playbook with discovery metadata, business definitions, and analytical guidance. It adds no tools or executable code.

**Skill Revision**: An immutable saved version, retained after edits, disabling, and deletion so historical evidence remains readable.

**Skill Attachment**: A shared conversation preference that asks the agent to apply a particular skill, subject to source compatibility and availability.

**Skill Snapshot**: The exact selected revisions captured for one analysis, including automatic/manual selection, reused for planning, repairs, and interpretation.

**Data Source**: A database or analytical warehouse whose retail data can be queried in the workspace.
_Avoid_: Application database, data lake

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
