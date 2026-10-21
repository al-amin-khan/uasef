# Technology decision research prompts

## Platform
Browser SPA, server-rendered web, mobile native, cross-platform, CLI, API, batch/data pipeline, embedded or mixed?

## Quality attributes
Data integrity; strong consistency; memory/CPU efficiency; cold starts; portability; compliance; throughput, latency, SLA; realtime/offline; cost and staffing.

## Stack alternatives
For web frontends compare client-only React/Vite, full-stack React frameworks, other SSR solutions, or server-rendered UI only when applicable. For backends evaluate the feasible ecosystem based on developer availability and NFRs (e.g. TS/Node, Java/JVM, C#/.NET, Go, Python, Rust), not by prestige. For DB compare transaction/query patterns, data shape, consistency and ops; never assume NoSQL for large scale.

## Experiment protocol
State the question, comparable representative task/load, environment, resource ceiling, runtime versions, measure, reproducibility and rollback before running a PoC.

## Output
Option tables; MUST vs preference; unknowns and evidence; ADR with approved decision, trade-offs, consequences and revisiting triggers.
