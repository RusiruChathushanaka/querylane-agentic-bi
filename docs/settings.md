# Workspace settings

Open **Settings** in the workspace sidebar or the settings icon in the header. The `/settings` page saves changes automatically in the current browser and synchronizes them across tabs on the same origin. No account is required.

## Available preferences

| Group | Options | Default |
| --- | --- | --- |
| Appearance | Light, dark, or system color mode | System |
| Accent | Cobalt, teal, violet, rose; updates controls and the first chart series | Cobalt |
| Density | Comfortable or compact conversation and table spacing | Comfortable |
| Motion | Reduce transitions and animation; device preference always respected | Device preference |
| AI model | Workspace default, Gemini 3.8 Flash, or Gemini 3.5 Flash-Lite | Workspace default |
| Data sources | Starting source for new conversations | All sources |
| Visualization | Auto, table, bar, or line | Auto |
| Number display | Maximum decimal places in tables, KPIs, chart tooltips | 2 |
| Composer | Enter sends; when off, Enter adds a new line | On |
| Follow-ups | Suggested questions beneath answers | On |
| Scrolling | Follow incoming answers and progress | On |
| Voice output | Play spoken responses alongside transcripts and results | On |
| Microphone | Start new/reconnected voice sessions muted | Off |

Ctrl/⌘ + Enter sends in either composer mode; Shift + Enter inserts a new line. Composition events used by input methods do not submit a question.

Existing conversations retain their sources. For result presentation, a manual visualization selection takes priority over the browser preference. Unsupported preferred views fall back to the artifact’s recommendation, then a table. Formatting changes display precision only: stored numbers, currencies (USD), SQL, result completeness, and evidence are preserved. Narrative answers remain as generated.

Voice options are read when starting or reconnecting a session. Turning off spoken responses suppresses browser playback; Gemini still produces its live audio response. This preference does not reduce model usage. Microphone permission is requested only after starting voice. Transcripts remain public and raw audio is not recorded.

## Analysis model selection

In **Analysis & charts → AI model**, choose Flash for complex questions or Flash-Lite for lightweight questions with lower model cost. The pinned choices are [`gemini-3.8-flash`](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash) and [`gemini-3.5-flash-lite`](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash-lite), checked against Google's documentation on 16 October 2026. **Workspace default** uses the operator's `TEXT_MODEL` setting, currently Gemini 3.8 Flash. Model identifiers are pinned rather than automatically following a changing `latest` alias.

New questions, follow-ups, and new/reconnected analyst voice sessions capture the selected analysis model. Skill relevance selection, planning, bounded SQL repairs, and interpretation all use that model for the run. An active run or connected voice session keeps its captured selection. Other visitors' selections and the server default are unaffected. Live speech and conversational skill authoring continue to use the configured Gemini Live model; embedding retrieval keeps its embedding model.

The backend exposes its catalog at `GET /api/v1/models`, validates optional `model` values on turn creation and the analyst voice authentication frame, and persists the resolved model on the run. Repeating an idempotency key preserves the original run; changing its requested model returns `409`. Result evidence records the actual model. Fixture mode explicitly shows that no model calls occur, while retaining the requested preference for Gemini mode. A model-access failure is reported without silently substituting another model.

## Storage and reset

Preferences use `querylane-preferences-v1` and `querylane-theme` in localStorage. These are per-origin: localhost and the deployed app have separate preferences. They do not change other visitors’ preferences or server configuration. Browsers with blocked storage use in-memory preferences for the visit and show a persistence notice.

Preference changes use a single Sonner confirmation that updates as you make changes. Reduced motion controls CSS transitions, Motion animations, beUI selection springs, and number counters together. See [motion and feedback](motion-and-feedback.md).

**Reset preferences** restores the defaults after confirmation. It leaves shared conversations, results, data connections, and the guest session intact. Theme defaults follow the operating system, including system changes while the app is open. Corrupt or unsupported preference fields fall back individually to defaults.

## Development

`Frontend/src/lib/preferences.ts` defines the versioned contract, defaults, validation, and pre-paint appearance bootstrap. `Frontend/src/hooks/use-preferences.ts` manages hydration-safe snapshots and same-tab/cross-tab updates. Appearance and presentation stay browser-local; the selected analysis model is submitted to the backend and captured with each new run. `Backend/app/model_selection.py` owns the pinned catalog and task-scoped model context, avoiding mutation of shared settings across requests. Older browser preferences default to the workspace model; older runs/artifacts remain readable without model evidence.

Run `npm run lint`, `npx tsc --noEmit`, `npm test`, and `npm run build` in `Frontend/`. Voice preference regression tests use mocked browser audio and transport, with no model calls. For releasing these changes, follow the [deployment guide](deployment-guide.md).
