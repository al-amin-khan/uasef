---
name: context-handoff
description: Transfer project knowledge between AI models without relying on private model context.
---

# Context Handoff

## When to use
Transfer project knowledge between AI models without relying on private model context.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Read authoritative specs, ADRs, current files, Git HEAD, task manifest, executed command evidence, blockers and approved state. Produce concise facts/assumptions/next action plus file paths/commit. Successor must reverify real state; do not transfer hidden reasoning or portray a summary as execution proof. Use `uasef handoff` for a starter state summary.

## Expected artifacts
`.uasef/handoff.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

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
Read [the task reference](references/handoff-contract.md) when the decision needs more detailed evaluation.
