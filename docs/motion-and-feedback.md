# Motion and feedback

Querylane uses Framer Motion through the `motion` package and free beUI components installed with the shadcn CLI. The existing shadcn/Radix controls, chart results, SQL, and public conversation model remain the foundation of the interface.

## Motion behavior

- The welcome screen introduces its heading, source path, and suggested questions in a short sequence. Suggested-question buttons provide hover and press feedback.
- Conversation changes, new messages, results, and voice panels use short opacity/transform transitions. Existing messages do not replay their entrance when public history refreshes.
- The analysis indicator follows the actual schema, query, relationship, and answer events. Its track indicates the current stage, not elapsed time or a predicted completion percentage.
- Charts and tables fade between views. beUI animated numbers settle to their final values in KPI cards and the settings preview; screen readers receive the final formatted value rather than a stream of intermediate numbers. Stored data and narrative answers are unchanged.
- The beUI color selector has native radio keyboard navigation, a moving selection ring, visible color names, and a checkmark. Settings navigation glides between selected sections.
- Voice level bars use transforms rather than repeatedly changing layout height. Under reduced motion they remain static.

The shared hook `Frontend/src/hooks/use-app-motion.ts` combines the device's reduced-motion preference with Querylane's **Settings → Reduce motion** preference. `MotionConfig` and the adapted beUI components use the same decision; CSS alone cannot stop JavaScript springs and counters. Reduced motion applies immediately, including to animations already in progress. Server-rendered page content remains visible before hydration.

Following new answers handles delayed result rendering through a ResizeObserver. Scrolling back or interacting with earlier content releases automatic following; returning to the bottom or asking a new question resumes it. The browser's saved follow-new-answers setting still controls the feature.

## Sonner notifications

One themed Toaster serves the app. Notifications appear below the header, away from the composer, have close buttons, and are limited to three visible messages. Repeated preference and visualization changes update a stable toast ID instead of stacking identical confirmations. Field values and persistent inline errors remain the primary record of the current state.

Analysis notifications update from loading to completion or error based on actual run events. A stop request stays pending until the run confirms cancellation. Leaving a conversation dismisses its loading notification; completed answers can still be reopened from public history.

Other notifications cover conversation forks, copy actions, selected sources, schema/connection errors, voice connection and microphone changes, voice permission failure, visualization changes, and browser preference updates/reset. Settings updates distinguish successful persistence from browser-storage fallback. Background history refreshes and streaming transcript fragments do not generate toasts.

## Source attribution and validation

Adapted beUI sources live in `Frontend/src/components/motion/animated-number.tsx`, `color-selector.tsx`, and `Frontend/src/lib/ease.ts`. Keep [the upstream MIT notice](../Frontend/licenses/beui-MIT.txt) with those sources. They retain the local `cn` utility and semantic theme tokens.

Local verification covers deterministic retail results, native radio keyboard navigation, toast deduplication/dismissal, analysis success/error/cancellation with isolated browser transport fixtures, microphone-denial recovery, reduced motion from both sources, reader-aware scrolling, and mobile layouts. Transport fixtures are used only by the test browser and are not part of the application. See [the UI evaluation record](evaluation/motion-and-feedback.json). Real microphone hardware is a separate manual acceptance check.

Run `npm test`, `npm run lint`, `npx tsc --noEmit`, and `npm run build` in `Frontend/`. Use the [deployment guide](deployment-guide.md) when releasing the changes.
