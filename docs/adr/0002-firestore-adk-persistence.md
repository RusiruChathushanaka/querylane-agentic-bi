# Persist ADK sessions in the named Firestore database

Application storage must remain in Firestore, and Python ADK does not supply a built-in Firestore session backend. A custom session adapter persists ordered events and state while checking the same fenced conversation lease used by the application. This avoids another application database or managed session service at the cost of maintaining and testing the adapter against the pinned ADK version.

Session revisions are attached to the exact loaded session object. Loading a newer object through the same adapter does not authorize an older object to overwrite state. Real Firestore validation uses independent clients, competing conversation turns, cross-client event reads, and a rejected stale session write.
