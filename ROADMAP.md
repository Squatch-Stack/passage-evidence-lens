# Roadmap and acceptance gates

This is an independent proposal. The Codex Sinaiticus partners set their own priorities and may choose a different implementation or no integration.

| Gate | Work | Proof before advancing |
| --- | --- | --- |
| 0 · Public prototype | Original responsive UI, link-only source navigation, tests, rights documentation | Desktop and 390 px end-to-end checks pass; no XML/image bytes in the public package |
| 1 · User study | Review three journeys with manuscript scholars, students and mobile readers | Document task completion, keyboard/screen-reader findings, and changes requested by users |
| 2 · Upstream contract | Agree on institution-approved IIIF canvas, Web Annotation IDs, rights fields and source version semantics | Host-supplied fixtures exercise corrections, omitted/damaged text, multiple hands, and denied display |
| 3 · Integration | Contribute a component or interaction pattern to the institution's preferred repository | CI, accessibility and security gates run in their pipeline; no duplicate search/image infrastructure |
| 4 · Maintenance | Fixes, dependency review, source-version migrations and issue response | Published releases state exactly which upstream version and rights decision each adapter supports |

The [integration contract](INTEGRATION.md) and [data policy](DATA_POLICY.md) are designed for review before any institution-dependent development. Gate 0 is implemented in this repository. Later gates require an institutional contributor path and approved data fixtures.
