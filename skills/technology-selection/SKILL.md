---
name: technology-selection
description: Compare languages, frameworks, databases and services from actual constraints.
---

# Technology Selection

## When to use
Compare languages, frameworks, databases and services from actual constraints.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Establish hard requirements and weights BEFORE scoring. Build a shortlist using present evidence. Consider skill, ecosystem, total ownership cost, ops, hiring, maintainability, portability, security, performance and exit cost. Use a time-boxed spike on uncertain high-impact decisions. Preserve rejected alternatives and triggers to revisit in an ADR. Acknowledge when keeping the current stack is best.

## Expected artifacts
`docs/03-engineering/technology-evaluation.md, docs/03-engineering/adr/ADR-001-stack.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

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
Read [the task reference](references/architecture-questions.md) when the decision needs more detailed evaluation.
