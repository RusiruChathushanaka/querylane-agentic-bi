# Five-minute competition demonstration

[Open the deployed application](https://agentic-bi-frontend-wekihucn7q-as.a.run.app). The public history currently includes validation conversations; use the credentialed reset command before a clean rehearsal if desired.

1. **Open the workspace — 30 seconds.** Explain that conversations are public, data is synthetic, and source access is read-only. Open a source schema from the sidebar.
2. **Ask a warehouse question — 45 seconds.** “Show monthly revenue as a line chart.” Switch the result to a table. Open SQL & evidence and identify the executed SQL, row counts, timestamps, and source.
3. **Combine sources — 75 seconds.** Start another exploration: “Compare regional revenue with targets.” Explain that warehouse actuals and operational targets are queried independently. Show the inferred relationship, coverage, and cardinality checks.
4. **Follow up — 45 seconds.** “Only September 2026.” Explain that the conversation preserves the analytical context and narrows both source windows.
5. **Speak — 60 seconds.** Start live voice: “Which customer segment generated the most revenue?” Let the tool produce a visual result and spoken explanation. Interrupt with a follow-up, demonstrate mute, then stop.
6. **Share and fork — 30 seconds.** Copy the public conversation link and fork the chat. Explain that existing result references remain immutable.
7. **Close — 15 seconds.** Show the evaluation report and the boundary between a model's hypothesis and the application's execution checks.

Use production for the final demonstration. Local fixture mode supports a smaller documented set of deterministic questions and is visibly labeled. `app.cloud_preview` provides real Gemini text and voice over synthetic fixtures if cloud deployment is awaiting permissions; disclose that distinction.

Before presenting: run readiness checks, confirm model availability, verify microphone permission and HTTPS, reset only demo history if needed, rehearse the questions, and record a backup using the same deployed application.
