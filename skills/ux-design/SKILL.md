---
name: ux-design
description: Create user flows, application navigation, screen behavior, wireframe briefs and design direction.
---

# Ux Design

## When to use
Create user flows, application navigation, screen behavior, wireframe briefs and design direction.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Start from actors and tasks; model navigation and decision branches, empty/loading/error/permission states; inventory screens and variants. Specify accessibility, localization, responsive constraints, visual tokens, component reuse and design review questions. Do not confuse wireframe descriptions with tested design prototypes.

## Expected artifacts
`docs/02-design/user-flows.md, docs/02-design/screen-inventory.md, docs/02-design/design-brief.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

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
Read [the task reference](references/screen-state-matrix.md) when the decision needs more detailed evaluation.
