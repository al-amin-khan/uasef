---
name: security-review
description: Threat-model an application and detect unsafe implementation or agent tool behavior.
---

# Security Review

## When to use
Threat-model an application and detect unsafe implementation or agent tool behavior.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Identify sensitive data, actors, trust boundaries, authn/authz, injection, secrets, supply chain and approval boundaries. Reference applicable current standards (e.g., OWASP ASVS/agent security). Classify severity, evidence, mitigation owner and residual risk. Never ship hardcoded credentials or permit unreviewed destructive actions.

## Expected artifacts
`docs/03-engineering/security-baseline.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

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
Read [the task reference](references/agent-trust-boundaries.md) when the decision needs more detailed evaluation.
