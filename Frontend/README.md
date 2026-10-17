# Querylane frontend

Next.js App Router, TypeScript, shadcn/ui, and Recharts. Application code is under `src/`; the backend runs separately in `Backend/`.

Routes include the public [landing page](../docs/landing-page.md) (`/`), conversation workspace (`/app`), shared dashboard library (`/dashboards`), report library (`/reports`), skills library (`/skills`) and browser-local settings (`/settings`). Dashboard View/Edit is URL-driven presentation state; all shared dashboards remain publicly editable. Charts and downloads preserve saved evidence. See [architecture](../docs/architecture.md) and [graph references](../docs/graphify/README.md).

From this directory:

```bash
npm ci
npm run dev
```

Open [the landing page](http://localhost:3000) or [workspace](http://localhost:3000/app). Legacy `/?chat=…` links receive a 307 redirect to `/app?chat=…`, preserving query parameters. The default API URL is `http://localhost:8000`; see [local setup](../docs/setup.md) for backend modes and environment configuration.

```bash
npm run lint
npm test
npx tsc --noEmit
npm run build
```

Verify affected loaded screens in a browser after application changes, including narrow layouts, keyboard controls, light/dark themes and reduced motion. [Validation notes](../docs/validation.md) distinguish local checks from dated hosted results. Documentation-only updates need local-link and graph-synchronization checks.

## Deployment

Use the **[Deployment guide](../docs/deployment-guide.md)** before deploying or changing Cloud Run configuration. This application deploys a standalone container to Cloud Run; its API URL is provided at runtime through `/api/config`. Follow the guide for the build identity, service configuration, origin allowlist, verification, and rollback.

See [repository instructions](../AGENTS.md) and [frontend agent instructions](AGENTS.md) before making changes.
