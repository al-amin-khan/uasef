---
name: feature-implementation
description: Implement an approved scoped feature while reusing suitable packages and providing test evidence.
---

# Feature Implementation

## When to use
Implement an approved scoped feature while reusing suitable packages and providing test evidence.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Read task ID, requirements, codebase, policies, contracts and ADRs. Check existing behavior and dependencies. Prefer reuse over rewriting generic auth/crypto/calendar/queue mechanisms. Implement the smallest vertical slice and associated tests; run actual checks, fix regressions, disclose commands/results. Never silently expand scope or claim unrun tests. Open review with evidence.

## Expected artifacts
`specs/features/<slug>/verification.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

## Deliverable format
1. Confirmed facts and supporting source/evidence (with dates where relevant).
2. Open questions and assumptions, each labeled as such.
3. Alternatives and recommendation with trade-offs.
4. Artifacts changed and requirement/task IDs.
5. Actual verification conducted, or precise reason not conducted.
6. Risks, approvals required, and next handoff.

## Non-negotiable guardrails
Never fabricate research, package compatibility, tests, deployment, approvals, or user validation. Request human review for sensitive/destructive/production changes. Prefer narrowly scoped action and record decisions in project artifacts.
