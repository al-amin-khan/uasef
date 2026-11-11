# Scaling decision triggers

Collect production measurements first. Define acceptable p95 latency, errors, saturation, expected peak RPS, data growth, recovery objectives and monthly operational cost. Differentiate simultaneous sessions from total user count.

**Escalation order:** profile and fix incorrect queries; indexes/connection pooling; optimize hot routes; appropriate caching or asynchronous jobs; horizontal scale/replicas; data partitioning; service extraction only with strong domain/operational justification.

Measure before-and-after under comparable conditions; include data integrity, failure impact, cost and rollback. Changes need an ADR and an observability plan.
