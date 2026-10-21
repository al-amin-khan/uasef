---
name: feature-planning
description: Turn approved specifications into dependency-aware vertical slices and implementation tasks.
---

# Feature Planning

## When to use
Turn approved specifications into dependency-aware vertical slices and implementation tasks.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Identify a narrow demonstrable end-to-end slice. Record dependencies, task ownership, acceptance criteria, test tasks, estimated uncertainty, high-risk gates, and Definition of Done. Separate parallel from dependent work; choose smallest independently verifiable work. Link each task to its REQ and tests.

## Expected artifacts
`docs/04-delivery/feature-backlog.md, docs/04-delivery/implementation-plan.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

## Deliverable format
1. Confirmed facts and supporting source/evidence (with dates where relevant).
2. Open questions and assumptions, each labeled as such.
3. Alternatives and recommendation with trade-offs.
4. Artifacts changed and requirement/task IDs.
5. Actual verification conducted, or precise reason not conducted.
6. Risks, approvals required, and next handoff.

## Non-negotiable guardrails
Never fabricate research, package compatibility, tests, deployment, approvals, or user validation. Request human review for sensitive/destructive/production changes. Prefer narrowly scoped action and record decisions in project artifacts.
