# Conversational voice skill author

## Requirement and scope

A visitor opens **Create with voice** in Skills, describes an analytical capability, and has a two-way conversation that gathers enough information to create a useful Markdown playbook. The assistant asks targeted follow-ups, remembers corrections, prepares a draft, and supports further refinement. The visitor can review/edit the result and explicitly publish an enabled skill through the existing versioned library.

“New features” means new analytics instructions, business definitions, and examples within the application's existing tools. Application code generation, new connectors, executable scripts, and new database permissions remain outside this feature.

## Implementation sequence

1. Verify and refresh the installed Firebase agent skills first; retain backend-only access to the existing Standard/Native `agentic-bi-demo` database. Read current ADK/Next.js guidance and the running skills route before editing.
2. Add durable, guest-scoped author sessions and typed interview requirements. Implement bounded creation/reconnect quotas, revision checks, leases, draft updates, and atomic publication through the existing skills service.
3. Add an ADK Gemini Live author with narrowly scoped requirements/draft tools. Reuse the existing PCM capture/playback transport and transcript events; preserve the separate retail analyst voice flow.
4. Add the Skills entry point and a themed, responsive author dialog: welcome, conversation, requirements checklist, transcript, mute/end/reconnect, typed input fallback, draft preview/editing, and publish confirmation.
5. Verify deterministic state/concurrency/security behavior, mocked streaming/audio lifecycles, real Gemini Live interviewing and drafting, browser behavior, accessibility, lint, type checks, and production build. Record limitations and update operational documentation. Deploy only when separately requested.

## Conversation flow

- A welcome screen explains microphone use, draft recovery, and public publication. Connecting requires a user action; permission failure leaves a typing option available.
- The assistant asks one focused question at a time, at most two closely related questions. It gathers purpose, when to use, compatible source(s), workflow, business definitions/filters/grain, and example questions. It can suggest a name and description from the stated purpose.
- Known answers appear in a requirements checklist. Corrections replace the corresponding brief field and invalidate any earlier prepared draft, preventing accidental publication of outdated instructions.
- The assistant uses available source descriptions as context and asks about missing definitions. It does not invent metrics, schema, or analytical outcomes and cannot execute queries while authoring.
- Once the brief is complete, a deterministic compiler creates the `SkillContent` draft, with Purpose, Workflow, Business definitions, and Examples sections. Preparing a draft does not publish it.
- The visitor pauses the assistant to review. The draft remains editable with the existing safe Markdown renderer. Returning to the interview retains the brief; manual review edits are replaced only by an explicit subsequent regenerated draft.
- **Publish skill** is an explicit UI action showing public visibility. Publication validates the exact reviewed revision, normal skill limits/quotas, and capacity, then atomically creates one enabled skill plus its immutable revision. Retries return the same skill.
- A success state links the published skill to the library and offers a new author session. Published sessions cannot silently generate another skill or overwrite the published one.

## Backend contracts and state

Use a separate `skill_author_sessions` collection. Each document records guest attribution, logical expiry, brief, bounded transcript, draft, revision, published skill ID, and an expiring fenced connection lease. It contains no audio. No public session listing is exposed; reads and changes require the initiating guest token. This is browser-session attribution, not a verified user identity or a confidential-data feature.

| Interface | Contract |
| --- | --- |
| `POST /api/v1/skills/author-sessions` | Create once per guest/idempotency key; enforce creation quotas |
| `GET /api/v1/skills/author-sessions/{id}` | Recover the initiating guest's brief, transcript, draft, and publication status |
| `PATCH /api/v1/skills/author-sessions/{id}/draft` | Replace reviewed `SkillContent` with an expected revision; reject while voice is connected |
| `POST /api/v1/skills/author-sessions/{id}/publish` | Publish reviewed revision once, using normal skill mutation safeguards |
| `WS /api/v1/skills/author-sessions/{id}/voice` | Origin-checked, token-authenticated live interview; audio/text in, audio/transcript/brief/draft/status out |

States: collecting → draft ready → reviewing → published. Corrections return to collecting until a new draft is prepared. Disconnect/error does not discard the last committed brief or draft. Model/connection failures remain visible and never publish a partial skill.

## Live architecture

Browser PCM 16 kHz → FastAPI WebSocket → ADK `LiveRequestQueue`/`Runner.run_live()` → pinned Gemini Live model. Assistant audio returns at 24 kHz. Reuse the configured spoken-response/start-muted settings, safe AudioWorklet capture, playback interruption, and resource cleanup. Typed messages can use the same conversation without microphone access.

Give the author two tools: update the typed interview brief and prepare the draft from that brief. Neither tool publishes or executes analytics. Persist completed transcripts and authoritative brief/draft events; omit raw audio. Reconnect loads saved state into a fresh fenced ADK connection, with supported Live resumption handles scoped to that connection generation. A generation change cannot replay a stale draft tool result into the current author state. Browser recovery rehydrates committed state rather than trusting a cached copy.

The session adapter supports an explicit lease collection, defaulting to existing conversations so analyst sessions retain their current behavior. Only one author connection can hold a session lease. Heartbeats renew it; stale processes cannot write tools or ADK events. Close/error cancellation releases the lease and microphone resources.

## Initial limits and failure behavior

- Three new author sessions per guest/hour; twelve workspace-wide/day.
- Six live author connections per guest/hour; thirty workspace-wide/day, including reconnects.
- Six-hour logical session expiry; ten-minute live connection limit.
- At most 24 user turns, 24 brief/draft updates, 48 tool calls (including failed/no-op calls), and 64 KiB of stored transcript per session. ADK `max_llm_calls` does not limit `run_live()`; the application enforces these budgets itself.
- Existing 16 KiB skill instructions, field limits, 100-skill capacity, and 20 guest/hour / 100 workspace/day skill mutation quotas remain authoritative at publication.
- No automatic expiry deletion is implied: expired records require the documented administrator cleanup operation. Browser storage keeps only the author-session ID; the backend is the source of truth. Token expiry or browser-session loss can make an unpublished draft unrecoverable.
- Stale revision → 409 with the draft retained in the UI; active lease → busy response; quota/capacity failure → useful retry/recovery message without losing the draft.
- An unavailable model is reported directly. Fixture mode does not pretend to provide conversational AI; live tests use explicit Gemini configuration.

## Acceptance criteria

1. A multi-turn conversation asks for missing details, accepts corrections, and creates a structurally valid skill draft with no fabricated numerical answers.
2. No skill is visible to analytics before publication. Review edits are validated, and a concurrent/stale publish cannot publish another version or create duplicates.
3. The published skill is enabled, appears in the normal library, and is usable through automatic discovery/manual attachment with immutable evidence.
4. A disconnected session recovers its committed brief/draft/transcript. Competing or stale connections cannot overwrite it. Other guest tokens cannot access it.
5. Microphone denial, typing fallback, mute, interrupted playback, end/reconnect, model failure, expiry, and publication quota/capacity failures have usable UI states.
6. Desktop/mobile, dark/light themes, reduced motion, keyboard focus, transcripts, screen-reader status announcements, Sonner feedback, and safe Markdown follow existing application behavior.
7. Backend tests, frontend checks/build, real-model integration, and browser verification are recorded separately. Text injected through Live does not count as microphone-hardware verification.

## References

- [ADK custom live server](https://github.com/google/adk-docs/blob/main/docs/live/custom-server.md)
- [ADK Live sessions](https://github.com/google/adk-docs/blob/main/docs/live/sessions.md)
- [Skills contract](skills.md)
- [Deployment runbook](deployment-guide.md)
