---
name: quality-verification
description: Independently verify requirements with unit, integration, end-to-end and security checks.
---

# Quality Verification

## When to use
Independently verify requirements with unit, integration, end-to-end and security checks.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Map each acceptance criterion to a check or justified manual review; test permissions, negative cases, data integrity, concurrency, accessibility where applicable, and regressions. Execute real commands in isolated environments; record environment/commit/outputs and failures. Do not trust self-reported pass claims. Block release on unaccepted critical defects.

## Expected artifacts
`docs/04-delivery/test-strategy.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

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
Read [the task reference](references/verification-matrix.md) when the decision needs more detailed evaluation.
