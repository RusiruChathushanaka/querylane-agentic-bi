# Querylane frontend

Next.js App Router, TypeScript, shadcn/ui, and Recharts. Application code is under `src/`; the backend runs separately in `Backend/`.

From this directory:

```bash
npm ci
npm run dev
```

Open [localhost:3000](http://localhost:3000). The default API URL is `http://localhost:8000`; see [local setup](../docs/setup.md) for backend modes and environment configuration.

```bash
npm run lint
npx tsc --noEmit
npm run build
```

## Deployment

Use the **[Deployment guide](../docs/deployment-guide.md)** before deploying or changing Cloud Run configuration. This application deploys a standalone container to Cloud Run; its API URL is provided at runtime through `/api/config`. Follow the guide for the build identity, service configuration, origin allowlist, verification, and rollback.

See [repository instructions](../AGENTS.md) and [frontend agent instructions](AGENTS.md) before making changes.
