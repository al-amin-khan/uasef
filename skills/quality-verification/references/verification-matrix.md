# Requirement-driven verification

| Test class | Evidence expected |
|---|---|
| Business rule | REQ ID + executable case and output |
| Failure/edge case | negative, timeout, missing, conflicting inputs |
| Authentication/authorization | no privilege escalation; least privilege |
| Data integrity | transactions, constraints, concurrent requests |
| UI | empty/loading/error, keyboard and screen reader where applicable |
| Integration | representative external dependency behavior |
| Performance | baseline workload, environment, result and limits |
| Security | tooling and risk-ranked human findings |
| Deployment | environment, commit and smoke/rollback evidence |

Every check says PASS, FAIL, or NOT RUN with actual command/environment. Avoid meaningless coverage percentages without meaningful assertions.
