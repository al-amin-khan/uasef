---
name: data-modeling
description: Specify relational or nonrelational data models, constraints, migration and consistency rules.
---

# Data Modeling

## When to use
Specify relational or nonrelational data models, constraints, migration and consistency rules.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Translate domain terms into entities and invariant checks; compare relevant data storage options; document relationships, constraints, tenancy, indexing, retention, backup and migration. Plan safe rollbacks and concurrency tests. Treat billing, identity and transactional data as high-risk. Do not generate destructive migrations without approval.

## Expected artifacts
`docs/03-engineering/data-model.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

## Deliverable format
1. Confirmed facts and supporting source/evidence (with dates where relevant).
2. Open questions and assumptions, each labeled as such.
3. Alternatives and recommendation with trade-offs.
4. Artifacts changed and requirement/task IDs.
5. Actual verification conducted, or precise reason not conducted.
6. Risks, approvals required, and next handoff.

## Non-negotiable guardrails
Never fabricate research, package compatibility, tests, deployment, approvals, or user validation. Request human review for sensitive/destructive/production changes. Prefer narrowly scoped action and record decisions in project artifacts.
