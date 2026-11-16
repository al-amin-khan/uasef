# Core milestone: Verified Delivery

**ID:** CORE-VD-001  
**Status:** Planned — scope accepted; implementation and acceptance pending  
**Established:** 2026-11-16  
**Accountable owner:** Project maintainer  
**Release version:** Unassigned; completion evidence determines release readiness

## Outcome

UASEF can guide one reference application from an approved requirement through
implementation, independent verification, protected integration, staging deployment,
operational observation and a rehearsed recovery. Each promotion is tied to the
actual code, acceptance criteria, required checks and artifact being promoted.

This is a core engineering milestone, not a claim that these capabilities already
exist. Planning approval does not authorize production deployment, paid services,
credential use or changes to repository protection settings. Implementation work
must follow the applicable project authorization and review requirements.

Source: [engineering audit, 16 November 2026](https://chatgpt.com/library?file_id=libfile_f36fdebcd37c8191823b0674a842bf68&account_id=personal).
The audit is a dated baseline; recheck repository and branch state before starting.

## Existing work to reuse

- [PR #7](https://github.com/al-amin-khan/uasef/pull/7) contains state backup/restore,
  commit-bound command receipts, recovery/migration tests, indexed search, timelines
  and structural conflict inspection. At the audit it was open with passing CI;
  provider-backed acceptance remained pending. Review and integrate rather than
  reimplementing it.
- `feat/guided-project-init` contains the guided initialization interview. Its
  existence on a branch does not mean it is integrated into the default branch.
- Local UI/UX changes include design gates and portable workflow installation.
  Preserve and review those changes before integration.
- Existing coding standards, SEO guidance, packaging tests, memory and execution
  safeguards are foundations. Add executable enforcement where it is missing.

## Delivery phases and dependencies

All phase statuses start as **planned**. A phase becomes complete only when its
acceptance evidence has been reviewed. Existing implementation may satisfy part
of a phase but does not automatically close it.

| Phase | Scope | Depends on | Responsible role | Exit criteria |
|---|---|---|---|---|
| VD-00 | Consolidate existing work and establish a reproducible baseline | None | Maintainer | Intended branches integrated without losing customization; documentation/version claims agree; clean-wheel installation and existing tests pass |
| VD-01 | Coordinator correctness, failure reporting and lifecycle readiness | VD-00 | Backend engineer + independent QA | Failed single/batch runs return nonzero; combined dependency/delegation cycles are rejected; implementation readiness and scoped spike exceptions are explicit |
| VD-02 | Required verification bound to actual work | VD-01 | Backend engineer + QA/security reviewer | Required named checks bind task, acceptance revision, configuration and commit; missing/failed/stale evidence blocks promotion; independent review remains distinct |
| VD-03 | Protected integration and application CI | VD-02 | DevOps + maintainer | Required checks block ordinary merge; bypass policy is explicit; one selected application stack receives working CI and useful failure evidence |
| VD-04 | One reproducible release/deployment path | VD-03 | DevOps + database engineer | Build artifact identity is preserved through staging; configuration and migrations are validated; smoke checks and failed-rollout recovery are demonstrated |
| VD-05 | Operational readiness, data safety and maintenance | VD-04 | DevOps/SRE + security/database reviewers | Alert and restore drills pass; ownership, data handling, recovery targets and costs are recorded; state and instruction drift can be detected and reconciled |
| VD-06 | Conditional web quality | VD-03 | Frontend/UX + QA | Applicable SEO, accessibility and performance checks execute; manual limitations and production follow-up are explicit |
| VD-07 | Usable setup and complete acceptance demonstration | VD-05, VD-06 | Maintainer + independent QA | Intake can resume and edit specific answers; applicability is clear; the end-to-end reference demonstration and failure cases pass |

VD-06 may proceed alongside deployment work after VD-03. For non-web projects,
record an explicit not-applicable decision instead of manufacturing SEO work.

## Required work packages

### VD-00 — Consolidation

- Inventory current branches, PRs, local modifications and test results.
- Integrate approved roadmap, guided-init and UI/UX work with regression checks.
- Ensure installed instructions can resolve required workflow references without
  needing the framework source checkout.
- Keep a capability matrix that distinguishes implemented, integrated, verified,
  optional, not applicable and pending behavior.

### VD-01 — Correctness and safe execution

- Propagate actual failure outcomes through single and bulk dispatch exit codes.
- Validate explicit dependencies together with parent-completion relationships.
- Connect inception readiness to implementation eligibility; record bounded
  feasibility-spike exceptions with scope and reasons.
- Define cancellation, timeout and retry semantics, including managed process-tree
  termination on supported platforms and inspection of ambiguous side effects.
- Apply consistent environment restrictions to runners; bound attempts and output
  retention. Worktrees must never be represented as an OS security sandbox.

### VD-02 — Verification contract

- Extend PR #7 receipts with named required checks and task/acceptance/configuration
  binding. A successful arbitrary command must not satisfy unrelated requirements.
- Reject empty or missing evidence where substantive review is required.
- Check evidence freshness at review and again at merge/release promotion.
- Define invalidation for changed code, acceptance criteria or required-check policy.
- Keep sanitized diagnostic output and record NOT RUN with a reason; never convert
  missing checks into PASS. Local receipts remain distinguishable from CI evidence.
- Add real-agent acceptance using an explicitly configured provider/model when
  authorized; independently inspect the produced artifact.

### VD-03 — CI and repository governance

- Provide a small application-check manifest mapped to existing stack tooling:
  build, formatting/lint, types, relevant unit/integration/browser tests and security.
- Configure required repository checks with an explicit solo-maintainer-compatible
  review/bypass policy; verify the settings rather than merely documenting them.
- Set least-privilege workflow permissions, dependency integrity verification,
  bounded execution and appropriate dependency/secret/code scanning.
- Verify downloaded Git-tool checksums and maintain immutable workflow dependency
  resolution with a reviewed update process.
- Record failures and artifacts in a form a maintainer can diagnose.

### VD-04 — Release and deployment

- Select one reference stack and deployment target before implementing adapters;
  reuse normal platform tooling and avoid a universal cloud abstraction.
- Record commit, artifact digest, environment, configuration revision, migration
  state, authorization, rollout outcome and recovery result in a release manifest.
- Build once and promote the same artifact. Serialize deployments per environment.
- Validate required configuration and secret references without retaining values.
- Rehearse database compatibility and recovery; distinguish reversible code rollback
  from destructive migrations that require restoration or a forward fix.
- Verify a real user journey after staging deployment and exercise a failed rollout.
- Define versioning and distribution/publishing evidence for UASEF itself; do not
  create stable release claims while required acceptance gates remain unresolved.

### VD-05 — Operations and maintenance

- Define user-relevant reliability indicators, targets, alert routing and ownership.
- Supply appropriate health checks, structured logs, error visibility and runbooks.
- Measure recovery point/time objectives with a restore drill; distinguish source
  control, UASEF-state archives and application/database backups.
- Make inception-state writes atomic and guard concurrent updates; exercise migrations.
- Track installed resource versions/hashes and offer reviewed reconciliation of
  changed policies/skills without overwriting project customization.
- Identify personal data, retention/deletion/export needs, access boundaries and
  safe test data. Review applicable obligations separately; do not claim compliance.
- Record operating costs, resource limits and preview-environment cleanup ownership.

### VD-06 — Public web, UI and performance

- For public pages, maintain route indexability/canonical expectations and test
  metadata, response codes, redirects, rendered links/content and environment mistakes.
- Validate sitemap, structured data and language variants only when applicable.
- Assign post-deployment search/indexing follow-up; unavailable external checks
  remain NOT RUN. Do not equate local checks with indexing or ranking guarantees.
- Use an agreed browser/viewport matrix, automated accessibility checks and relevant
  manual keyboard/focus/zoom checks. Visual approval alone is insufficient.
- Set workload and performance budgets; distinguish lab measurements from field data.

### VD-07 — Usability and acceptance

- Add resumable intake, targeted answer editing and questions conditional on project
  type and risk. Keep small projects proportional while preserving essential controls.
- Make blockers, next actions, owners, evidence and deferred work easy to inspect.
- Demonstrate requirement-to-task-to-commit-to-check-to-release traceability using
  one reference application, including its operational and recovery evidence.

## Milestone acceptance gate

The maintainer and an independent reviewer must examine a versioned evidence
package containing all of the following:

1. Exact framework/application revisions, environment, commands and check results.
2. A working reference application deployed to a designated staging environment.
3. Traceability from one approved requirement to code, required checks, review and
   the exact deployed artifact.
4. Negative demonstrations: failed runner, mixed-result batch, dependency cycle,
   missing/empty evidence, changed commit/requirements and failing required CI.
5. Successful cancellation/recovery behavior and no silent retry of ambiguous work.
6. A rehearsed bad rollout, database/state restore and actionable alert drill.
7. Applicable SEO/accessibility/performance results and honest manual/field limitations.
8. Real-provider acceptance evidence, or an explicitly narrowed release scope that
   excludes unverified provider-compatibility claims.
9. Reconciled documentation, installation/upgrade checks and known limitations.

Do not mark the entire milestone complete while a required gate is pending.
Any scope change, exclusion or deferral needs a recorded reason and owner review.
Production rollout is a separate authorized action, not required to demonstrate
this staging-based milestone.

## Evidence and change tracking

Use the stable VD phase IDs in issues/tasks and Conventional Commit scopes where
helpful. For each work package record status, owner, linked requirement/audit finding,
commit, test command, actual result, evidence location and remaining risks. Dates
are estimates until explicitly agreed; no deadline is invented by this milestone.

Audit mapping: F01/F03/F05/F09 -> VD-01; F02 -> VD-02; F04/F07/F11 -> VD-03;
F08 -> VD-04; F10 -> VD-05; F06 -> VD-00. Conditional web quality and usability
extend the audit coverage matrix through VD-06 and VD-07.

## Explicit non-goals

No mandatory Kubernetes, distributed scheduler, custom identity platform, vector
database, all-cloud deployment framework or automatic provider fallback. Do not
promise identical pixels on every device, SEO rankings or security certification.
Prefer small adapters and existing project/platform tools. No runtime behavior,
approval enforcement or implementation is created merely by recording this plan.
