---
name: build-vs-buy
description: Decide reuse, adopt, extend, buy or build for a feature using evidence.
---

# Build Vs Buy

## When to use
Decide reuse, adopt, extend, buy or build for a feature using evidence.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Check repo capabilities first. Compare reuse, open-source package, service and bespoke implementation. Filter hard blockers (license, security, compatibility, privacy, deployment). Score functionality, maturity, maintenance, integration cost, reliability, reversibility; spike critical uncertainties. Document why not custom-code commodity infrastructure, and why domain behavior remains custom.

## Expected artifacts
`docs/03-engineering/solution-research.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

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
Read [the task reference](references/option-scorecard.md) when the decision needs more detailed evaluation.
