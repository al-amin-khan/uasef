---
name: incident-response
description: Handle incidents with safe triage, impact assessment and recovery-first operational decisions.
---

# Incident Response

## When to use
Handle incidents with safe triage, impact assessment and recovery-first operational decisions.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
Describe symptoms, timeline, impact and confirmed evidence. Protect data; collect logs/metrics before destructive steps; choose mitigation and safe rollback. Escalate production access and data changes. After recovery, write an evidence-based postmortem and preventative actions without blame.

## Expected artifacts
`docs/05-operations/incident-runbook.md`. Reference actual files and persistent task IDs. If a relevant artifact is not yet required, explicitly mark it deferred instead of inventing completeness.

## Deliverable format
1. Confirmed facts and supporting source/evidence (with dates where relevant).
2. Open questions and assumptions, each labeled as such.
3. Alternatives and recommendation with trade-offs.
4. Artifacts changed and requirement/task IDs.
5. Actual verification conducted, or precise reason not conducted.
6. Risks, approvals required, and next handoff.

## Non-negotiable guardrails
Never fabricate research, package compatibility, tests, deployment, approvals, or user validation. Request human review for sensitive/destructive/production changes. Prefer narrowly scoped action and record decisions in project artifacts.
