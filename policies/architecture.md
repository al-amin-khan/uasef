# Architecture policy

Start by defining quality attributes, team capability, deployment boundaries, external integrations, data sensitivity, consistency rules, throughput/concurrency and failure handling. Prefer simple modular boundaries. Do not introduce microservices, distributed transactions, event streams or orchestration infrastructure merely for hypothetical million-user growth.

For significant designs provide system context, container/deployment boundaries, data flows, trust boundaries, failure modes, API/interface contracts, backup and recovery assumptions, operational costs and ADRs. Define measurable evolution triggers (SLO breaches, error budgets, sustained capacity constraints, distinct scaling or deployment needs).

Separate architectural invariants from interchangeable technology implementation details. Review architecture when material product requirements or real metrics change.
