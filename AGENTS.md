# Repository instructions

## Deployment reference

Before deployment, cloud provisioning, IAM/secret changes, rollback, or cloud troubleshooting, read and follow [docs/deployment-guide.md](docs/deployment-guide.md). It is the primary runbook for Cloud Run and this application's supporting Google Cloud services.

- Choose the guide's routine-release or first-time-foundation path for the actual task. Treat seeding and shared-history reset as separate data operations.
- Use the existing `infra/` helpers and the actual frontend origin. Preserve the dedicated identities and resource boundaries described in the guide.
- Work within the user's authorized scope; the guide itself is not authorization to deploy or delete data. Existing session authorization remains applicable.
- When deployment behavior changes, update the guide alongside the implementation. After an actual deployment, record real serving revisions/configuration in `docs/deployment.json` and verification evidence in `docs/validation.md` and relevant evaluation reports.
- Treat `docs/deployment.json` and historical evaluation reports as dated records. Inspect current cloud state when the task requires it.

## Current documentation

Use the `ctx7` CLI to fetch current documentation for library, framework, SDK, API, CLI, and cloud-service questions, including setup, configuration, migrations, and library-specific debugging. Prefer this to web search.

1. Resolve the official library name with `npx ctx7@latest library <name> "<specific question>"` before using an ID, unless the user supplied the ID.
2. Select the relevant `/org/project` result using name, relevance, reputation, snippet coverage, and score. Use a returned version-specific ID when needed.
3. Fetch with `npx ctx7@latest docs <libraryId> "<specific question>"`. Keep distinct concepts separate and use no more than three commands per question.
4. Base the implementation or answer on the fetched documentation. Keep credentials out of queries.

Run Context7 CLI requests outside the default sandbox. If DNS/network resolution fails inside the sandbox, rerun outside it. On a quota error, inform the user and suggest `npx ctx7@latest login` or `CONTEXT7_API_KEY`; do not silently fall back to training data. Context7 is unnecessary for general programming concepts, business-logic debugging, refactoring, code review, or scripts that do not depend on a library/service question.
