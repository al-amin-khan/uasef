# Workflow: model-handoff

**Trigger:** Model/provider change or context reset

## Procedure
Record current task status, commit, changed artifacts, evidence, blockers and next action; successor re-checks repository, policies and tools.

## Required controls
- Read `AGENTS.md`, policy files and the authoritative task/specification state.
- Before building, check existing project solutions and current library research.
- Do not fabricate external research or execution evidence.
- Escalate sensitive, costly, destructive or production changes for human authorization.
- Store decisions, traceable output artifacts, verification evidence and handoff notes.

## Exit condition
Successor independently verifies task continuity.

## Failure and recovery
If inputs are contradictory or a gate fails: mark BLOCKED in the task issue, preserve partial evidence, state the exact blocker, propose next safe action. Do not silently bypass gates.
