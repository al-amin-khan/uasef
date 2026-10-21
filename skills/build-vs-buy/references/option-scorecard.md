# Capability adoption scorecard

First reject any candidate failing hard constraints. Evaluate remaining options with predeclared weights, then conduct an integration spike for unknown risks.

| Dimension | Illustrative weight | Evidence |
|---|---:|---|
| Business requirement fit | 25 | requirements coverage matrix |
| Security/privacy/license | 20 | license verification, advisories, threat model |
| Maintenance maturity | 15 | source/issue/release evidence with dates |
| Integration complexity | 15 | actual prototype time and requirements |
| Total cost of ownership | 10 | development, hosting, vendor, migration costs |
| Portability and exit | 10 | adapter seams, data export, dependency coupling |
| Performance under workload | 5 | representative benchmark and constraints |

Scores are decision aids, not substitutes for expert review. Unverified claims must remain unknown; do not assign perfect values based on popularity.

Record `candidate`, `verified_version`, `license`, `sources`, `evaluated_on`, `hard_filters`, `weights`, `risks`, `revisit_trigger`, `decision`.
