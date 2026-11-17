# Changelog

## Unreleased - Coordinator correctness (VD-01, first increment)

- Return nonzero CLI results for failed/blocked single and bulk dispatch while preserving original runner outcomes.
- Feed generic runners from the prompt file so unread stdin pipes cannot bypass Windows subprocess timeouts.
- Reject combined dependency/delegation cycles atomically, including transitive parent/child deadlocks.
- Add real-process regression coverage for failures, timeouts, missing programs, mixed-result batches and valid sibling ordering.
- Readiness gates and managed process-tree cancellation remain planned; this is not completion of all VD-01 work.

## Unreleased - UI/UX preview and library-first frontend workflow

- Add a review gate and workflow for clickable prototypes or annotated mockups before UI implementation.
- Require inspection and documented reuse of installed component, styling and motion systems before custom UI code or new dependencies.
- Add guidance for purposeful animation, reduced motion, responsive/accessibility states, owner feedback and rendered-browser verification.
- Connect the workflow to UX/frontend role contracts, design templates, project charter and routing documentation.
- Require newly created frontend execution tasks to depend on an approval-gated UX task or record an explicit waiver; preserve existing tasks during additive migration.
- Standardize exported mockups and screenshots under docs/02-design/previews/<TASK-ID>/ and define named-device visual comparison evidence.


## Unreleased — Core milestone planning

- Establish CORE-VD-001 (Verified Delivery) as the next core engineering milestone.
- Define phases, dependencies, owners, acceptance evidence and audit-finding traceability across verification, CI/CD, deployment, operations and conditional web quality.
- Register the milestone in framework metadata and link its plan from the README; no runtime behavior or release version changes.

## Unreleased - v0.5-v0.7 roadmap foundations

- Add versioned UASEF-state backup/restore with checksums, path validation and SQLite snapshots.
- Exercise inception/database migrations and abrupt worker interruption recovery.
- Add explicit commit-bound verification commands and an opt-in required review gate.
- Add chronological memory timelines, structural conflict reports and incremental FTS5 search.
- Provide an explicit real OpenCode artifact test; provider-backed acceptance remains pending a configured model.

## Unreleased - Coding standards and SEO

- Add practical coding standards and a proportional complexity review for maintainable, reliable implementation without speculative abstractions.
- Add conditional public-web SEO guidance with official sources and verifiable checks.
- Connect policies to the project charter, engineering/QA roles and feature review; document preservation of existing instructions during upgrade.

## Unreleased - Standalone packaging

- Bundle canonical framework resources in wheels and source distributions.
- Resolve installed resources independently of the source checkout or working directory.
- Exercise isolated installations on Windows/Linux with Python 3.10/3.12 in CI.

## Unreleased - Doctor diagnostics

- Add local setup, project-state and effective Git hook inspection with JSON output.
- Add explicit OpenCode authentication configuration and model connectivity probes.
- Keep credential configuration separate from verified access; suppress raw agent output.

## 0.4.0 - Git-backed project memory

- Record ideas, requirements, decisions, preferences, findings, verification and current briefs as portable append-only JSON history.
- Link records to each other, task IDs, existing commit SHAs and evidence hashes; preserve superseded decisions and distinguish declared, inferred and confirmed claims.
- Automatically export inception/execution task history and explicit session checkpoints without runner logs or credentials.
- Include bounded project memory in scoped prompts and project/session handoffs.
- Add memory search, trace, evidence validation and explicit scoped Git checkpoint commands.
- Upgrade existing projects without replacing customized agent instructions or older records.

## Unreleased — OpenCode CLI integration

- Native opt-in OpenCode subprocess adapter using documented `run --file --format json` interface.
- OpenCode role exporter, diagnostics, explicit environment allowlist, NDJSON event/error summary.
- Mock integration tests and OpenCode usage/security documentation; live CLI/model execution not verified.


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

### Guided initialization
- Added `uasef init --interactive` (`-i`) with a plain-language intake, editable review, and cancellation before creating files.
- Captured answers carry into inception without automatically completing tasks or approving architecture; existing scripted initialization remains supported.
