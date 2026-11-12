# Coding standards and proportional complexity

Apply to implementation and code review in every stack. Follow the project's established conventions and approved requirements; choose the simplest design that meets correctness, security, accessibility and measured operational needs. Simplicity does not excuse missing safeguards.

## Implementation rules

- Read related code, contracts and tests first. Keep the change scoped; separate unrelated cleanup. Reuse suitable existing capabilities before adding dependencies.
- Use descriptive domain names, cohesive functions/modules and explicit inputs, outputs and side effects. Comments explain intent, constraints or surprising tradeoffs; remove dead code and misleading comments.
- Follow the configured formatter, linter and type checker. Do not suppress diagnostics or weaken types merely to pass checks; explain any necessary exception locally.
- Extract an abstraction for a concrete shared behavior or meaningful boundary. Small duplication can be preferable to coupling unrelated concepts. Do not add unused interfaces, generic repositories, plugin systems or configuration for hypothetical requirements. KISS, YAGNI, DRY and SOLID are decision aids, not quotas for classes or layers.
- Preserve API/data compatibility unless a change is approved. Validate untrusted input at boundaries, enforce authorization where access occurs, use parameterized data access, protect secrets and avoid sensitive logs. Use transactions or equivalent integrity controls where partial writes would violate business rules.
- Handle expected failures explicitly with useful errors and cleanup. Do not swallow failures or return fake success. For remote calls, consider bounded timeouts, cancellation and retries only where safe; account for idempotency before retrying writes.
- Prefer understandable algorithms and bounded data access. Avoid obvious N+1 queries and unbounded user-controlled workloads. Add caches, queues, parallelism or distributed services only for demonstrated requirements; record consistency, invalidation and operational costs where relevant.
- Test observable behavior, relevant failures and regressions. Select unit, integration or end-to-end checks by risk and boundaries; avoid implementation-mirroring tests, arbitrary coverage targets and extensive mocks that hide real behavior. A trivial documentation edit does not need a new test suite.
- Use established stack tooling rather than inventing a framework. Add dependencies only when their benefit outweighs maintenance, security, licensing and runtime costs. Record consequential tradeoffs and update affected contracts/docs.

## Complexity review

Record a short assessment in existing verification or PR notes; do not create a separate document for a trivial change.

1. Which approved behavior requires this change, and what is the simplest sufficient implementation?
2. Can any new layer, dependency, abstraction, configuration or state be removed without losing a requirement or safeguard?
3. Are responsibilities, error paths, data ownership and tests understandable to the next maintainer?
4. Are performance/scaling choices supported by a workload requirement or measurement? What would justify revisiting them?
5. Which checks actually ran, what failed or remains unverified, and what meaningful risks remain?

For a small CRUD feature, use existing routing, validation and data-access conventions with relevant tests. Do not automatically add an event bus or a generic service/repository hierarchy. A payment or concurrent stock update may need transactions, idempotency and audit evidence even when its UI is small.

Apply the constitution's proportional process: concise evidence for small work; design alternatives and ADRs for consequential architecture. These instructions guide agents and reviewers; configured tooling, CI and repository permissions provide executable enforcement.
