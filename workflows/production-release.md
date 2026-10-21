# Workflow: production-release

**Trigger:** Release candidate prepared

## Procedure
Validate reproducibility, required tests, security and migration impact, backup/rollback, staging smoke tests, explicit human authorization and post-release observation.

## Required controls
- Read `AGENTS.md`, policy files and the authoritative task/specification state.
- Before building, check existing project solutions and current library research.
- Do not fabricate external research or execution evidence.
- Escalate sensitive, costly, destructive or production changes for human authorization.
- Store decisions, traceable output artifacts, verification evidence and handoff notes.

## Exit condition
Authorized release and verified rollout, or safe rollback.

## Failure and recovery
If inputs are contradictory or a gate fails: mark BLOCKED in the task issue, preserve partial evidence, state the exact blocker, propose next safe action. Do not silently bypass gates.
