# Validation and remaining deployment gates

Validated on 2026-10-15. Results distinguish local integration from deployed acceptance.

## Automated checks

| Check | Result | Scope |
| --- | --- | --- |
| Backend pytest | 85 passed | SQL restrictions, numerical fixtures, fusion cardinality/type/completeness checks, guest scopes, quotas, idempotency, leases, replay, forks, ADK persistence, failure recovery, voice handshake |
| Ruff | Passed | Backend application, tests, smoke scripts |
| Frontend ESLint / TypeScript | Passed | Application and generated components |
| Next.js production build | Passed | Standalone configuration, application routes, runtime configuration |
| Deterministic evaluation | 31/31 passed | Synthetic retail sources, independently calculated Python references |
| Real Gemini evaluation | 31/31 passed | `gemini-3.8-flash` generates SQL against the same synthetic sources; numeric assertions use independent references |
| Hosted numerical evaluation | 31/31 passed | Public deployed API over real BigQuery/PostgreSQL; all cases used vector retrieval |
| Deployed acceptance | 16/16 passed | Health, CORS, source evidence, follow-ups, forks, idempotency, voice handshake, live tool/audio/transcript |
| Runtime identity / persistence | 16/16 passed | Existing-resource denial, SELECT-only role, independent Firestore clients, atomic status, stale object rejection |
| Model compatibility | Passed | Text generation, 768-dimensional `gemini-embedding-001`, live model connection |
| Real live integration | Passed | Live transport → ADK tool → analysis → artifact + audio + transcript + completed turn |
| Frontend/backend HTTP | Passed locally | Production frontend `/api/health` reaches backend, runtime API configuration |
| Automated accessibility | Zero reported axe violations | Welcome and populated workspace; manual screen reader coverage remains separate |
| Responsive layout | Passed locally | 390×844 mobile viewport has no horizontal page overflow; desktop workspace inspected |
| Production dependency audit | Zero reported vulnerabilities | `npm audit --omit=dev` |

The final real-model evaluation includes one bounded retry for transient model transport failures. The first run's 29/31 outcome and targeted recheck remain in `evaluation/gemini-initial.json` and `evaluation/gemini-recheck.json`; they are not substituted for the final full run. The application retains the requested model identifiers rather than silently selecting another model.

The full npm audit also reports unresolved high-severity `braces` advisories through development tooling. `braces@3.0.3` was the available registry release at verification. The shadcn CLI is a development dependency; these packages are excluded from the final standalone runtime. Recheck tooling advisories before competition delivery. Pytest reports one upstream Starlette/httpx deprecation warning.

## Reproducible evidence

- `evaluation/fixture.json`: 31 deterministic cases.
- `evaluation/gemini.json`: full passing 31-case real-model run over fixtures.
- `evaluation/deployed-31.json`: full passing 31-case hosted-source run, with vector retrieval in every case.
- `evaluation/deployed.json`: deployed public API and live voice acceptance.
- `evaluation/cloud-runtime.json`: attached runtime identity and real Firestore checks.
- `deployment.json`: service URLs, images, identities, and serving revisions.
- `evaluation/vector-retrieval.json`: browser-submitted hosted question using the ready vector index.
- `evaluation/live-smoke.json`: live integration observations and explicit hardware limitation.
- `evaluation/accessibility.json`: populated-workspace axe report, with zero violations and an incomplete contrast check.
- Browser review also confirmed a real Gemini cross-source question, a September follow-up ($13,410 actual versus $17,600 target), and table switching over the same artifact.
- Backend tests: `pytest -q` from `Backend/`.
- UI checks: `npm run lint`, `npx tsc --noEmit`, `npm run build` from `Frontend/`.
- Real voice smoke: `uv run python -m scripts.smoke_voice` from `Backend/` (opt-in billed model access).

The original fixture and Gemini reports use local synthetic sources. Separate deployed reports exercise the seeded hosted sources and real named Firestore; see the cloud verification section below.

## Cloud deployment and identity checks

The explicitly approved IAM grants were applied on 2026-10-15. Both public Cloud Run services are deployed in `asia-southeast1`, using the dedicated frontend and backend identities. Firestore `agentic-bi-demo`, BigQuery `agentic_bi_demo`, Cloud SQL `agentic-bi-demo-pg`, demo secrets, and the source/image build resources are configured. Both hosted sources contain the deterministic seed. The 768-dimensional vector index is ready, and a hosted browser question was verified to use `gemini-embedding + full-schema` retrieval.

`evaluation/deployed.json` records passing health, runtime configuration, CORS, hosted numerical answers, follow-ups, fork context, query evidence, denied voice origins/tokens, and live audio/transcript/tool results. `evaluation/cloud-runtime.json` records real named-Firestore concurrency and ADK persistence checks, a rejected stale object write, restricted PostgreSQL reader privileges, and denied access to all pre-existing Firestore databases and enterprise BigQuery datasets. Existing-resource checks requested only metadata/read-only transaction setup, never business documents or table rows. The temporary private check job is removed after verification.

Cloud verification found and corrected two concurrency issues: revisions must belong to individual loaded session objects, and run/lease completion status must be read atomically. Regression tests cover both. The initial hosted 31-case evaluation retained correct numbers in the affected case but reported a false interruption; it is preserved separately in `evaluation/deployed-31-initial.json`. The final stable-revision run passes all 31 cases and uses vector retrieval throughout. A contention probe returned an unexpected loser response once; a diagnostic rerun and four targeted repetitions all produced exactly one winner and one `conversation_busy` response. No probe produced two committed turns or corrupted conversation state.

The scoped resources are active and billable. Request/scan/instance limits are configured. Billing alerts require a billing administrator and do not constitute a spending cap.

## Remaining manual competition checks

1. Exercise a real microphone and speaker across at least ten representative scenarios, including interruption, mute, reconnect, microphone denial, and source failure recovery. Automated live checks inject text into the live transport and do not prove microphone hardware operation.
2. Complete the manual keyboard/screen reader review. Automated axe checks cover the populated deployed workspace with zero reported violations, but include an incomplete contrast check.
3. Rehearse the five-minute script and prepare the backup recording using the deployed application.
4. Configure the desired billing alert recipients and thresholds with the billing administrator.

## Local review modes

The standard local command uses deterministic planning and in-memory synthetic sources. `app.cloud_preview` uses real Gemini with the same synthetic sources and memory history, and is labeled accordingly in the interface. Its operator token remains in memory and expires; restart the preview to refresh it. This local-only entry point must not be used for Cloud Run deployment.
