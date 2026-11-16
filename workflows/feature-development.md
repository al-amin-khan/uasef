# Workflow: feature-development

**Trigger:** Approved feature requested

## Procedure
Identify/confirm REQ, create feature package, research reuse, contract-first design, implement a thin slice, run tests, independent review, release with approval.

For features with a new or materially changed UI, follow [UI/UX preview before frontend implementation](ui-ux-preview.md): inspect existing UI and motion libraries, create a reviewable mockup/prototype, wait for owner review unless the owner explicitly waives it, then implement and verify rendered behavior. Choose UX-first, frontend-first, or vertical-slice sequencing from the user's preference and actual contract dependencies.

## Required controls
- Read `AGENTS.md`, policy files and the authoritative task/specification state.
- Apply `.uasef/policies/coding-standards.md` before implementation and during review; justify added complexity in existing verification notes. Determine SEO applicability and follow `.uasef/policies/seo.md` for affected public pages.
- Before building, check existing project solutions and current library research.
- Do not fabricate external research or execution evidence.
- Escalate sensitive, costly, destructive or production changes for human authorization.
- Store decisions, traceable output artifacts, verification evidence and handoff notes.

## Exit condition
Traceable feature tests pass and required reviews are recorded.

## Failure and recovery
If inputs are contradictory or a gate fails: mark BLOCKED in the task issue, preserve partial evidence, state the exact blocker, propose next safe action. Do not silently bypass gates.
