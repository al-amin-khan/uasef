# Evidence-driven evolution policy

Define SLOs/SLIs and workload assumptions before advocating large scale. Measure p50/p95/p99 latency, availability, errors, saturation, request volume, concurrency, cache behavior, data growth and running costs as applicable. Differentiate registered users, daily active users and concurrent users.

Work bottom-up: correct N+1/data modeling/indexing → tune queries and connections → add suitable caches/jobs/replicas → horizontal scale → selectively extract services only when measured needs justify complexity. Always evaluate consistency, failure handling, data migration, rollback, cost, security and operational staffing. Performance experiments must report test conditions and limitations.
