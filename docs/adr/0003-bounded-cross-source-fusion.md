# Infer relationships but execute only typed bounded fusion

The demo must explore unfamiliar cross-database relationships automatically. Gemini proposes keys and business assumptions, while a trusted compiler permits only typed relational operations on bounded source results in an isolated DuckDB process. Unexpected fan-out and incomplete inputs fail explicitly; this trades unrestricted computation for reviewable SQL, cardinality diagnostics, and reproducible results.
