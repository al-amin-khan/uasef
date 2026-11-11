# Workflow: scaling-review

**Trigger:** Measured performance or reliability issue

## Procedure
Collect workload/SLO baseline, localize bottleneck, consider low-cost optimization first, model and test options, write ADR and rollback.

## Required controls
- Read `AGENTS.md`, policy files and the authoritative task/specification state.
- Before building, check existing project solutions and current library research.
- Do not fabricate external research or execution evidence.
- Escalate sensitive, costly, destructive or production changes for human authorization.
- Store decisions, traceable output artifacts, verification evidence and handoff notes.

## Exit condition
Measured improvement with accepted operational risk.

## Failure and recovery
If inputs are contradictory or a gate fails: mark BLOCKED in the task issue, preserve partial evidence, state the exact blocker, propose next safe action. Do not silently bypass gates.
