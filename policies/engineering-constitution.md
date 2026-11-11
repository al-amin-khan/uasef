# Engineering constitution

## Non-negotiable rules
1. Establish user/business outcome before choosing technology.
2. Separate confirmed facts, assumptions, options, unknowns and approved decisions.
3. Check existing repository capabilities; investigate adoption before writing commodity code.
4. No claims about current package releases, vulnerabilities, benchmarks, licenses, standards or prices without dated source evidence.
5. Prefer the simplest reversible design meeting measured/approved NFRs; do not adopt speculative infrastructure for imagined scale.
6. Specifications and implementation must be traceable through requirement IDs, task IDs, tests and commits.
7. Human approval is mandatory for paid services, security-sensitive changes, irreversible migrations, material architectural pivots and production rollout.
8. Never fake test results, review, research, signoff, release or recovered memory.
9. Keep context portable across models in versioned artifacts; avoid mutable chat as a source of truth.
10. Investigate disagreements between requirements, code, tests and deployed behavior; do not silently choose one.

## Authority
Human product owner decides outcomes, scope, risks, budgets, and consequential approvals. Agents may research and recommend; the task-tracking CLI is not identity or permission management. CI/repository permissions provide real enforcement.

## Proportional process
Trivial: small targeted change and evidence. Medium: requirements, reuse scan, test plan, review. Major: evidence-backed options and ADR, explicit approval, rollback. Critical: least privilege, backup, rehearsal, independent signoff.
