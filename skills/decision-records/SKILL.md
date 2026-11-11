---
name: decision-records
description: Maintain durable Architecture Decision Records and track superseded choices.
---

# Decision Records

## When to use
Maintain durable Architecture Decision Records and track superseded choices.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
For consequential choices document situation, constraints, considered alternatives, dated evidence, hard filters, decision, owner, approval, consequences, triggers to revisit. Never rewrite accepted historical reasons; supersede by adding a new ADR and linking the earlier one. Keep project state consistent.

## Expected artifacts
`docs/03-engineering/adr/`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

## Deliverable format
1. Confirmed facts and supporting source/evidence (with dates where relevant).
2. Open questions and assumptions, each labeled as such.
3. Alternatives and recommendation with trade-offs.
4. Artifacts changed and requirement/task IDs.
5. Actual verification conducted, or precise reason not conducted.
6. Risks, approvals required, and next handoff.

## Non-negotiable guardrails
Never fabricate research, package compatibility, tests, deployment, approvals, or user validation. Request human review for sensitive/destructive/production changes. Prefer narrowly scoped action and record decisions in project artifacts.
