# Workflow: feature-development

**Trigger:** Approved feature requested

## Procedure
Identify/confirm REQ, create feature package, research reuse, contract-first design, implement a thin slice, run tests, independent review, release with approval.

## Required controls
- Read `AGENTS.md`, policy files and the authoritative task/specification state.
- Before building, check existing project solutions and current library research.
- Do not fabricate external research or execution evidence.
- Escalate sensitive, costly, destructive or production changes for human authorization.
- Store decisions, traceable output artifacts, verification evidence and handoff notes.

## Exit condition
Traceable feature tests pass and required reviews are recorded.

## Failure and recovery
If inputs are contradictory or a gate fails: mark BLOCKED in the task issue, preserve partial evidence, state the exact blocker, propose next safe action. Do not silently bypass gates.
