# Changelog

## 0.2.0 — Agent Execution and Orchestration

- Added SQLite-backed execution task DAG with atomic claims and audit history.
- Added configured external CLI runners: manual preview by default, explicit `--execute` for subprocess invocation.
- Added bounded timeouts, logs, optional Git worktrees, concurrency scheduler, leases, recovery and retries.
- Added independent review, evidence requirements, manual submission and explicit local approval gates.
- Added 3 Agent Skills, runtime docs, sample runner configuration and orchestration tests.
- No authenticated identities, hardened sandbox or automatic model provider access yet.


## 0.1.0 — 2026-10-15
- Added open-format, role-aware engineering skills and thirteen role contracts.
- Added 16 inception tasks with four approval gates, templates and policies.
- Added portable project scaffolding adapters and offline workflow CLI.
- Added task state, evidence paths, structural validation, feature scaffolds and model-handoff summaries.
- Added unit tests and CI; clarified limitations of non-autonomous execution.
