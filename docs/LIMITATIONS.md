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

## Consolidated capabilities and remaining limits

The guided `init --interactive` interview gathers a fixed set of answers and
requires review before writing project files; it is not an autonomous discovery
agent. Workflow guides are installed into generated projects without replacing
customized copies. Frontend design gates are local workflow controls, not
identity-authenticated approvals.

State backup/restore and commit-bound verification are described in
[Roadmap delivery](ROADMAP-DELIVERY.md). Backups do not include the full application
or its production database. Verification receipts remain local assertions and do
not enforce required CI checks or authorize deployment. Indexed memory conflicts
are structural/heuristic findings, not proven semantic contradictions.

Coordinator failure reporting and combined dependency-cycle checks are enforced
by code. Inception readiness, managed process cleanup, cancellation and bounded
retry/output controls are implemented under VD-01. These are local controls, not
a sandbox: detached POSIX processes and abrupt worker death require operator
inspection, and external side effects cannot be rolled back automatically. See the
[delivery progress record](VERIFIED-DELIVERY-PROGRESS.md).
