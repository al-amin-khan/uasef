# Human authority and approval gates

A human product owner is accountable for: INIT-005 feasibility/go-no-go, INIT-006 MVP scope, INIT-011 stack choice and INIT-016 readiness. Significant spending, outside communications, production deployment, deleting data, schema rewrites, user data sharing, access-control changes, legal/compliance assumptions and secrets access also require separately documented human authorization.

The CLI's `uasef approve` records a declaration, not authenticated consent. Use protected branches, environment protection rules, human reviewers and least-privilege accounts in real environments. No agent may approve its own production change.

Approval evidence should contain identity (via trusted repository/workflow system), timestamp, decision, scope, rationale, risks and reference to artifact version/commit. Approved tasks are not proof that deliverable content is correct; independent review remains necessary.
