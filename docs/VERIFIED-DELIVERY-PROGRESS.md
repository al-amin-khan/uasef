# Verified Delivery progress

Milestone: **CORE-VD-001**. Overall status: **in progress**. Updated 2026-11-17.
This record distinguishes completed integration from individual implemented fixes
and remaining acceptance work. The full milestone is not complete.

| Phase | Status | Evidence / next action |
|---|---|---|
| VD-00 Consolidation | Complete | PR #8 merged; all 10 CI jobs passed at 87f9eb2 |
| VD-01 Coordinator correctness | Implemented; final CI pending | Failure/cycle fixes in PR #9; readiness in PR #10; managed execution, retry and output controls under final validation |
| VD-02 Required verification | Planned | Extend integrated commit receipts with named checks, acceptance/task binding and promotion-time freshness |
| VD-03 Protected CI | Planned | Required repository checks and application CI profile |
| VD-04 Release path | Planned | Select reference stack and staging target; prove release and recovery |
| VD-05 Operations | Planned | Alert/restore drills, atomic state writes, instruction reconciliation and data lifecycle |
| VD-06 Web quality | Planned | Conditional executable SEO, accessibility and performance checks |
| VD-07 Usability / final demonstration | Planned | Resumable intake and full reference-application acceptance |

## Completed baseline

[PR #8](https://github.com/al-amin-khan/uasef/pull/8) integrates PR #7, guided
initialization, the milestone plan, UI/UX gates and project-local workflow copying.
The main merge commit is 44cb05bcd08b69406d2d4ba2e73d5be179c7a58e.

[CI evidence](https://github.com/al-amin-khan/uasef/actions/runs/43861522709)
for source 87f9eb290a125448b79264b59dd530b46afeb575: full unit/integration tests
and isolated sdist-built-wheel checks on Windows/Linux with Python 3.10/3.12,
plus live Git-tool integration on both operating systems. Packaging now exercises
the guided interview, portable release workflow and customized-file preservation.
A separate legacy-schema memory-export regression also passed locally.

## First VD-01 increment: audit F01 and F03

- Dispatch now separates the message from its exit status. Runner failure, timeout
  or launch failure produces CLI exit 1, with the original exit retained in the run.
- Bulk dispatch attempts every independently selected task and reports the maximum
  outcome code; configuration/eligibility errors return 2 instead of false success.
- Combined dependency/delegation validation catches direct and transitive cycles.
  Validation, insertion and audit writes share a SQLite write transaction.
- Local command: `python -m unittest discover -s tests -p test_coordinator_regressions.py -v`.
  Initial result: 8 passed on Windows/Python 3.12; a ninth test covers large-prompt timeout and stdin delivery. Cases include real shell failure, serial
  and parallel mixed batches, timeouts, missing executables, blocked dispatch,
  rejected ancestor cycles, atomic rejection and valid sibling ordering.
- Windows/Python 3.10 CI exposed a blocking stdin-pipe write that could bypass the timeout. Generic runners now receive the prompt file directly as stdin; a large unread prompt must time out and a reader must still receive its complete contents.
- Existing OpenCode-error and failed-run tests now assert nonzero CLI results.
  Cross-platform CI must pass before merging this increment.

## Next VD-01 increment

1. Connect applicable inception readiness to implementation dispatch and manual
   submission, with a scoped, recorded feasibility-spike exception.
2. Define cancellation ownership and process-tree cleanup on supported platforms;
   prevent retries while an earlier managed worker may still be active.
3. Harmonize runner environment restrictions and bounded attempts/output retention.

No production rollout, paid provider call, repository-protection mutation or
stable release tag is implied by these changes. Real-provider acceptance remains
pending a configured model; backup scope remains UASEF state, not production data.


## Readiness increment

Implementation gates now check all canonical inception steps, approval notes and
artifact availability. Planning tasks may target an eligible inception step;
a feasibility exception records its scope/reason, expires within seven days and
allows one attempt. Existing task statuses/history survive the additive migration.
Regression coverage includes real inception CLI transitions, malformed state,
missing approvals/artifacts, blocked claims/manual submissions, spike expiry and
attempt limits, delegation isolation and migration. Cross-platform checks are
required before integration. Cancellation and runner restrictions remain pending.


## Managed execution increment and VD-01 acceptance

PR #10 merged readiness after all 10 CI jobs passed (91 tests in each test job):
https://github.com/al-amin-khan/uasef/actions/runs/44017952632 .

The final VD-01 increment implements cancellation, Windows Job Object/POSIX group
cleanup, worker ownership locks, audited inspection before uncertain recovery,
shared runner environment restrictions, bounded attempts and retained output.
Seven initial runtime regressions passed locally, including real descendant timeout,
normal-exit cleanup, cancellation ownership, output and environment limits. Final
cross-platform CI must pass before integration; only then is VD-01 accepted.

Remaining limitations are explicit in ORCHESTRATION.md: no OS sandbox, no rollback
of external effects, and interrupted POSIX workers/deliberately detached processes
require operator inspection. VD-02 required verification is the next phase.
