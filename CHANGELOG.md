# Changelog

## 0.3.0 — Session Memory, Delegation, and Model Routing

- Added persistent task-linked sessions, checkpoints, event history and portable handoff exports.
- Added explicit parent/child task delegation with depth limits and parent review/approval barriers.
- Added deterministic, explainable role/skill-aware routing across installed external CLI profiles.
- Preserved opt-in execution, verification gates, SQLite audit history, and v0.2 task migrations.
- Added routing, session, and delegation skills, user guide and regression tests.
- No direct cloud model SDK, authenticated human approval, hardened sandbox or automatic provider fallback.


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
