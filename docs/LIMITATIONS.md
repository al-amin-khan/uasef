# Security, scope, and automation limitations

UASEF 0.1 is an **engineering-method starter repository** plus a working local inception state CLI. It does not autonomously ask questions, browse, run experiments, enforce policy within another product, manage real users, or test/deploy code.

## State and approval
- `.uasef/state.json` is a mutable text file; concurrent edits are unsafe.
- `approve` verifies note length and state, but does **not** authenticate a human. Require protected branches/environment approvals when connecting real deployments.
- `complete` performs superficial artifact presence/placeholder checks. It does not validate research truth, semantic coherence, OWASP compliance, or project readiness.
- External source research requires a suitable network-enabled research tool or human verification; answers must never fabricate it.
- Agent instruction discovery varies. Always verify tools actually loaded the requested role and skill.

## Future production enhancements
Transactional state store; idempotent workers and queues; task lease/timeout/retry semantics; evidence artifact signing; role-based identity/approval service; sandboxed coding runtime; budget/telemetry; Git/CI adapters; real traceability checks; tool-permission enforcement; evaluation harness for multi-model quality and recovery; secure secret broker.

## Safe deployment
Use least-privilege service credentials and stage environments. Never provide unrestricted shell/database/cloud tokens to unknown skills or autonomously initiated tasks. Require human approval for operations with financial, personal-data, destructive or production impact.
