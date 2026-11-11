# Inception tasks and exit gates

The machine-readable canonical workflow is `workflows/inception.json`. The CLI enforces ordering and local state for INIT-001..016, while the invoked AI/human creates the required documents. Each file starts with TODO-marked prompts, not assumed facts.

## Stages
- 001 idea verbatim; 002 problem/assumptions; 003 user research; 004 current alternatives.
- **005 feasibility, GO/REVISE/STOP gate**: human decides whether investment is warranted.
- **006 product/MVP scope gate**: user outcomes, MVP boundaries, measurable metrics and explicit non-goals.
- 007 detailed requirements, 008 user flows, 009 design direction.
- 010 candidate services/libraries and build/buy/adopt analysis.
- **011 technology and ADR gate**: compare alternatives against *hard constraints*, verify evidence and obtain approval.
- 012 architecture/data/API, 013 security/NFR/deployment, 014 backlog and milestones, 015 quality strategy.
- **016 readiness gate**: independent critique, cross-document contradiction check, approved next vertical slice.

## Traceability
Use stable `OBJ-*`, `USR-*`, `REQ-*`, `ADR-*`, `FEAT-*`, and `TEST-*` identifiers. Before closing readiness make a matrix linking each in-scope requirement to an implementation task and at least one executable test or explicitly accepted manual verification.

## Document depth
**Small:** concise sections and focused docs. **Moderate:** full detailed feature contracts and diagrams. **Critical:** legal/privacy and security review, migration/runbooks, disaster recovery and independent approvals. Mark future features deferred; avoid speculative 100-page plans.

## Human responsibilities
Confirm facts and decisions, explicitly review approval gates, provide legal/compliance expertise where needed, authorize cost/access/data/production changes. Agent responsibility includes surfacing unknowns rather than filling them with guesses.
