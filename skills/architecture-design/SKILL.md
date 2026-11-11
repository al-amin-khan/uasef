---
name: architecture-design
description: Select evolutionary software architecture and define bounded technical interfaces.
---

# Architecture Design

## When to use
Select evolutionary software architecture and define bounded technical interfaces.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Capture critical quality attributes and constraints, draw system context and deployment boundaries; compare monolith/modular monolith/distributed architecture with operational costs. Define modules, interactions, API/data contracts, trust boundaries, failure modes, observability and scaling triggers. Avoid premature microservices or speculative queues. Record unresolved risks and ADRs.

## Expected artifacts
`docs/03-engineering/architecture.md, docs/03-engineering/nfr.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

## Deliverable format
1. Confirmed facts and supporting source/evidence (with dates where relevant).
2. Open questions and assumptions, each labeled as such.
3. Alternatives and recommendation with trade-offs.
4. Artifacts changed and requirement/task IDs.
5. Actual verification conducted, or precise reason not conducted.
6. Risks, approvals required, and next handoff.

## Non-negotiable guardrails
Never fabricate research, package compatibility, tests, deployment, approvals, or user validation. Request human review for sensitive/destructive/production changes. Prefer narrowly scoped action and record decisions in project artifacts.

## Additional guidance
Read [the task reference](references/design-checklist.md) when the decision needs more detailed evaluation.
