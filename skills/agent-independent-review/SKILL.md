---
name: agent-independent-review
description: Review execution evidence independently and gate completion on tests, acceptance criteria and explicit human approval where required.
---

# Agent Independent Review

## Purpose
Verify the work against acceptance criteria with independent evidence, not self-reported agent confidence.

## Procedure
1. Read the assigned task and `uasef task show TASK-ID`.
2. Inspect the actual working tree/branch, source changes and acceptance criteria.
3. Run relevant tests and analyze failures, security impacts and docs drift.
4. Save a local review report in the project with test commands/results and remaining risks.
5. If acceptable, call `uasef task verify TASK-ID --reviewer reviewer-id --evidence path`.
6. If approval-gated, await `uasef task approve ...` from a real authorized human.

## Boundaries
Runner exit code 0 does not prove correctness. CLI reviewer identity is a local self-declaration, not cryptographic authentication.
Use protected GitHub branches, mandatory reviewers and deployment protections for enforceable authorization.

## Deliverable
Written independent review with actual evidence and accurate task status.
