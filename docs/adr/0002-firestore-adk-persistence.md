# Persist ADK sessions in the named Firestore database

Application storage must remain in Firestore, and Python ADK does not supply a built-in Firestore session backend. A custom session adapter persists ordered events and state while checking the same fenced conversation lease used by the application. This avoids another application database or managed session service at the cost of maintaining and testing the adapter against the pinned ADK version.

Session revisions are attached to the exact loaded session object. Loading a newer object through the same adapter does not authorize an older object to overwrite state. Real Firestore validation uses independent clients, competing conversation turns, cross-client event reads, and a rejected stale session write.

The pinned Python SDK retries aborted commits but lets a read-phase `Aborted` escape its transactional callback. The document adapter retries that read/modify/write operation in a fresh transaction at most three times with short jitter. This lets a losing conversation request observe the winner and return `conversation_busy`. Exhausted contention returns HTTP 409 `transaction_busy`; SDK commit exhaustion is translated without multiplying its retry budget. Other callback errors propagate. Callbacks remain retry-safe and contain no model calls or source SQL execution. Regression tests use the real SDK decorator with injected read aborts.

A stream reads ordered events and then run status. Completion can commit between those reads, so a terminal stream drains through the run’s persisted sequence before closing. Regression tests cover success, failure, cancellation, and cursor replay without duplicates.

Voice author interviews reuse the adapter with an explicit `skill_author_sessions` lease collection. Existing analytics leases still default to `conversations`. Every author socket gets a fresh ADK generation reconstructed from committed requirements, draft, and recent transcript; SDK transport resumption is scoped within that generation. Publication is a separate atomic HTTP action, outside model tools.
