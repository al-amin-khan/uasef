# Architecture design checklist

- C4 context: actors, external systems, trust boundaries.
- Deployable components: code modules, data, background work, integrations.
- Runtime flows: happy and failure paths; retries, idempotency, ordering, transactions.
- Data: consistency, indexes, ownership, schema evolution, retention and backups.
- Security: authorization boundary, secret management, logging and sensitive data.
- Reliability: service targets, availability/recovery, alarms and degradation.
- Scale: explicit baseline and *measurement-driven* evolution thresholds.
- Costs: developer and operational maintenance, hosting, support, migration.
- Deploy: repeatable builds, config, CI, rollbacks and runbooks.
- ADR: why options were rejected and when to review.

Do not require every item to be elaborate for small prototypes: document deferrals and risks transparently.
