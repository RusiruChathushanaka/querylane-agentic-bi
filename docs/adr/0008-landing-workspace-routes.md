# Separate the public introduction from the analytical workspace

Status: Accepted — 2026-10-17

Serve a server-rendered product landing page at `/` and the existing workspace at `/app`. The primary action is direct, unauthenticated application entry. Keep Reports, Dashboards, Skills and Settings at their established routes; shared content remains public.

Use a query-aware Next.js configuration redirect to forward legacy root conversation links to a fixed same-origin `/app` destination with HTTP 307. Configuration runs before route rendering and preserves query parameters, allowing the bare homepage to remain statically rendered. Centralize generated conversation paths so New exploration, sharing, forks and source links cannot return to the marketing page accidentally.

Guided previews use checked local evidence and scripted interactions, with no analytical/model/audio clients. Keep important copy and native links server-rendered; constrain client code to the tour and mobile sheet. Disable application-entry prefetch. Scope the landing palette independently of saved workspace appearance preferences. This isolates an informational visit from live analysis while making the real application immediately accessible.
