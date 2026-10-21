# Technology selection policy

Do not select React, Rust, TypeScript, Java, Next.js, PostgreSQL, Kubernetes or any other tool as a default without context.

### Selection sequence
1. Establish problem, workflows, runtime/platform needs, developer capacity and nonfunctional constraints.
2. Enumerate must-haves (legal/privacy, compatibility, uptime, data consistency, hosting limitations, cost ceiling) as hard filters.
3. Choose 2–4 credible alternatives and verify supported versions using current authoritative docs.
4. Declare scoring weights in advance: requirements fit, delivery time, maintainability, ecosystem, security, operating cost, portability, performance and migration/exit cost.
5. Evaluate irreversible/high-cost uncertainties with a narrow, representative time-boxed spike.
6. Record weighted comparisons AND caveats in ADR; disclose uncertainty and conflicts of interest.
7. Obtain human approval for material stack choices; specify revisit conditions and a rollback/migration outline.

An existing working choice is often preferable to a framework migration. Benchmarks must be representative, reproducible, documented, and not treated as general truths.
