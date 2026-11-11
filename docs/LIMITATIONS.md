# Security, scope, and automation limitations

UASEF 0.2 is an engineering-method starter plus a local task orchestration engine. It can dispatch external CLI agents via explicit subprocess opt-in, but does not autonomously ask discovery questions, browse, enforce security policies inside other agents, authenticate real users, validate engineering correctness, or deploy applications. See `docs/ORCHESTRATION.md`.

## State and approval
- `.uasef/state.json` is a mutable text file; concurrent edits are unsafe.
- `approve` verifies note length and state, but does **not** authenticate a human. Require protected branches/environment approvals when connecting real deployments.
- `complete` performs superficial artifact presence/placeholder checks. It does not validate research truth, semantic coherence, OWASP compliance, or project readiness.
- External source research requires a suitable network-enabled research tool or human verification; answers must never fabricate it.
- Agent instruction discovery varies. Always verify tools actually loaded the requested role and skill.

## Future production enhancements
Distributed worker queue and job heartbeats; hardened sandbox execution; evidence artifact signing; role-based identity/approval service; sandboxed coding runtime; budget/telemetry; Git/CI adapters; real traceability checks; tool-permission enforcement; evaluation harness for multi-model quality and recovery; secure secret broker.

## Safe deployment
Use least-privilege service credentials and stage environments. Never provide unrestricted shell/database/cloud tokens to unknown skills or autonomously initiated tasks. Require human approval for operations with financial, personal-data, destructive or production impact.
