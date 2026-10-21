---
name: solution-research
description: Research market alternatives, existing implementations and trustworthy sources before new development.
---

# Solution Research

## When to use
Research market alternatives, existing implementations and trustworthy sources before new development.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Separate competitors, open-source libraries, commercial APIs and managed services. Search official docs, changelogs, issue trackers and license/security sources with dates; never fabricate live research. Record candidate/version/source/access date, requirements covered, weaknesses, uncertainty, exit strategy; favor reusable tested solutions when fit is proven.

## Expected artifacts
`docs/00-inception/market-alternatives.md, docs/03-engineering/solution-research.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

## Deliverable format
1. Confirmed facts and supporting source/evidence (with dates where relevant).
2. Open questions and assumptions, each labeled as such.
3. Alternatives and recommendation with trade-offs.
4. Artifacts changed and requirement/task IDs.
5. Actual verification conducted, or precise reason not conducted.
6. Risks, approvals required, and next handoff.

## Non-negotiable guardrails
Never fabricate research, package compatibility, tests, deployment, approvals, or user validation. Request human review for sensitive/destructive/production changes. Prefer narrowly scoped action and record decisions in project artifacts.
