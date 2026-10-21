---
name: dependency-review
description: Review a proposed software library or service for adoption and supply-chain risk.
---

# Dependency Review

## When to use
Review a proposed software library or service for adoption and supply-chain risk.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Confirm package identity and authoritative registry; check compatible versions, release dates, license obligations, transitive dependencies, known advisories, maintainer activity and alternative suppliers. Test an isolated integration where relevant; never infer security from downloads or popularity. Record precise sources and a review date. Flag unresolved or disallowed licenses and vulnerabilities.

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
