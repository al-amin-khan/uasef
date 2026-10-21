---
name: agent-task-orchestration
description: Plan and schedule role-specific tasks using transactional dependency checks, audit trails and human approval gates.
---

# Agent Task Orchestration

## Purpose
Delegate bounded tasks to specialist roles without introducing conflicting changes.

## Workflow
1. Read `AGENTS.md`, approved requirements, ADRs and the active workflow.
2. Create `uasef task add` items with unique IDs, a role, one primary skill, explicit acceptance criteria and referenced documents.
3. Model prerequisites using repeated `--depends`. Only completed, reviewed and when applicable human-approved tasks unlock dependents.
4. Use `uasef task list` and `uasef dispatch-ready` to select independent work.
5. Use distinct Git worktrees for concurrent coding tasks; keep shared contracts approved before starting parallel implementation.
6. Inspect each run and review test/build evidence; a successful process exit means only the runner exited successfully.
7. Record explicit human approval for high-impact changes. Never claim model or tool permissions authenticate the approver.

## Stop conditions
Stop on missing prerequisites, contradictory source of truth, risky changes lacking approval, or exhausted retries.

## Deliverable
A dependency-aware task graph, reviewed evidence, audit records and accurate remaining work.
