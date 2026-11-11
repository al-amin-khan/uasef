# Workflow: incident-response

**Trigger:** Service instability or production incident

## Procedure
Assess severity, preserve logs and data, mitigate with least-risk action, obtain approval for destructive steps, communicate and write blameless postmortem.

## Required controls
- Read `AGENTS.md`, policy files and the authoritative task/specification state.
- Before building, check existing project solutions and current library research.
- Do not fabricate external research or execution evidence.
- Escalate sensitive, costly, destructive or production changes for human authorization.
- Store decisions, traceable output artifacts, verification evidence and handoff notes.

## Exit condition
Stabilized system, documented cause or uncertainty and prevention tasks.

## Failure and recovery
If inputs are contradictory or a gate fails: mark BLOCKED in the task issue, preserve partial evidence, state the exact blocker, propose next safe action. Do not silently bypass gates.
