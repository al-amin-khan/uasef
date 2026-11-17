# Agent Execution and Orchestration — v0.2

UASEF v0.2 introduces a **local transactional execution layer**. It uses SQLite for task leases, dependency checks and an append-only audit history; works with any authorized external CLI that accepts its prompt on **stdin**; and deliberately separates runner success from independent verification and human approvals.

## Install

Requires Python 3.10+, Git for worktree mode, and any external coding CLI you choose to configure.

```bash
python -m pip install -e .
uasef init ../sample-app --name "Sample App" --idea "Create a simple internal app"
cd ../sample-app
uasef runners
```

`uasef` is installed from the local source checkout. No external model provider is needed for task planning/manual mode.

## 1. Create a scoped task

```bash
uasef task add API-001 \
  --title "Implement health endpoint" \
  --role backend-engineer \
  --skill feature-implementation \
  --acceptance "Health endpoint returns 200; tests demonstrate expected behavior"
uasef task list
```

Tasks may depend on other completed tasks (`--depends API-001`), point to existing safe project documents (`--context docs/01-product/prd.md`), or require approval (`--approval-required`).

Newly created tasks with role frontend-engineer must use --design-task UX-ID or --design-waiver REASON. The design task must have role ux-designer and require approval; UASEF automatically adds it as a dependency and blocks frontend dispatch until it is verified and approved. A waiver reason is stored on the task and included in its agent prompt. The additive database migration leaves existing tasks ungated to preserve their current work. Actor names remain unauthenticated local assertions.

## 2. Manual mode - safe by default

```bash
uasef dispatch API-001 --profile manual
```

The prompt is written to `.uasef/runs/manual-api-001/prompt.md`. Nothing is executed and task status remains `queued`. Copy the prompt into your coding agent, then save its report in the project:

```bash
uasef task submit API-001 --actor "manual-coding-agent" --evidence docs/evidence/implementation.md
```

This moves the task to `awaiting_review`, **not** `completed`.

## 3. Configure a real runner (explicit opt-in)

Edit `.uasef/runners.json` (generated manual-only). An illustrative profile:

```json
{
  "profiles": {
    "manual": {"type": "manual"},
    "my-agent": {
      "type": "subprocess",
      "argv": ["my-agent-cli", "--headless"],
      "timeout_seconds": 600
    }
  }
}
```

**The external command must accept the task prompt on standard input.** Verify your chosen agent CLI's current syntax and interactive/tool approval behavior first. No shell expansion or dynamic command interpolation is performed. UASEF passes the prompt through stdin and sets `UASEF_TASK_ID` and `UASEF_PROMPT_FILE` environment variables.

```bash
uasef dispatch API-001 --profile my-agent           # preview: only writes prompt
uasef dispatch API-001 --profile my-agent --execute # executes as your OS user
uasef dispatch API-001 --profile my-agent --execute --worktree
```

`--worktree` requires a Git repository with an initial commit; it creates a new worktree and branch `uasef/<task>/<run>`. Your model can modify its own branch without colliding with another worker. It does **not** provide an OS sandbox and does **not** automatically merge or delete worktrees. Inspect and review the branch before integration.

Review logs, diff and changed files before completion. Successful subprocess exit produces `awaiting_review`; failure produces `failed`.

## 4. Review and approval

After running tests and writing a real review report:

```bash
uasef task verify API-001 --reviewer "qa-reviewer" --evidence docs/evidence/review.md
```

If `--approval-required` was set at task creation, the task transitions to `awaiting_approval`. Record a local human declaration:

```bash
uasef task approve API-001 --actor "Project Owner" --note "Reviewed the change and test evidence"
```

This CLI does not authenticate users or enforce real human identity. Use GitHub branch protections, required reviewers and environment restrictions for actual authorization controls. A reviewer name matching the execution profile is rejected, but this is not a security boundary.

## 5. Dependency-aware dispatch and recovery

```bash
uasef dispatch-ready --profile my-agent --execute --limit 5 --jobs 2 --worktree
uasef task show API-001
uasef task recover
uasef task retry API-001
```

`dispatch-ready` selects only tasks whose dependencies are **completed**. With more than one concurrent worker, Git worktrees are mandatory. SQLite `BEGIN IMMEDIATE` prevents two workers claiming the same ready task simultaneously. A lease extends beyond the configured runner timeout; a crashed launcher may leave a stale lease. `recover` marks expired leases `failed`. Inspect and stop orphaned subprocesses before retrying.

## Audit and state

- `.uasef/orchestration.sqlite3`: transactional tasks, runs and audit events. Project-local, not checked into Git by default.
- `.uasef/runs/<run-id>/prompt.md` and `runner.log`: local context and potentially sensitive output; Git-ignored.
- `.uasef/worktrees/`: local Git worktrees; Git-ignored. Clean up manually after merging/reviewing.
- `.uasef/runners.json`: user-reviewed runner definitions. **Do not put credentials in argv or files committed to Git.**
- `.uasef/state.json`: separate v0.1 inception task state; not combined or migrated into SQLite.

## Important limitations

This is a **single-machine coordinator**, not an always-on service, authenticated approval platform or hardened sandbox. It does not automatically ask discovery questions, search packages, instantiate cloud agents or evaluate code correctness. External AI execution requires an installed/authorized CLI; Git worktrees are only repository isolation. `--worktree` preserves branches for explicit review instead of auto-merging. Every subprocess executes with your account's permissions and may access the network, secrets or files outside the workspace according to its own tools and configuration.

Always inspect the profile, use the coding CLI's own sandbox/approval options, and avoid production credentials. Run real tests independently before marking work verified.
## Dispatch result contract

`uasef dispatch` returns 0 for a prepared preview/manual prompt or a successful
runner exit (still awaiting review), 1 when a runner fails, times out or cannot
launch, and 2 for invalid arguments or blocked dispatch. The run record preserves
the original process exit code. A CLI zero is never a claim of verified completion.

`dispatch-ready` reports every selected task and returns the highest result code:
0 when all attempts succeed, 1 when any execution fails, or 2 when any dispatch is
blocked. Other independent selected tasks are still attempted. No ready tasks is
a successful no-op. Parallel execution still requires worktrees.

Task creation validates explicit dependencies together with the requirement that
parents wait for their children. Direct, ancestor and transitive dependency cycles
are rejected atomically, without leaving a partial task or delegation audit entry.
Existing tasks are not automatically rewritten to repair old cycles.


## Inception readiness before implementation (VD-01)

Execution tasks default to implementation work. Before dispatch (including prompt
preparation), claim or manual submission, all canonical inception steps must be
completed, required approvals must have meaningful recorded notes, and their
artifacts must still exist and pass the basic unfinished-template check. Missing,
malformed or incomplete state blocks execution. This is a local structural check,
not independent content verification or authenticated approval.

Use `uasef next` to progress inception, and `uasef task list` to see why execution
is blocked. `dispatch-ready` returns 2 when no task can run because of readiness,
with the blocking reason; an ordinary empty ready queue still returns 0.

Agents can help with inception itself. Bind planning work to an eligible step;
its role must match that step and its skill must be a supported planning skill:

```sh
uasef task add PLAN-001 --title "Clarify the idea" --role product-manager --skill project-inception --acceptance "Write a reviewed idea brief" --inception-step INIT-001
uasef dispatch PLAN-001
```

Completing that execution task does not automatically complete or approve the
inception step. Continue to use `start`, `complete` and `approve` for inception.
The step's prerequisites must already be complete before creating its planning task.

An early feasibility experiment needs both a reason and a bounded scope:

```sh
uasef task add SPIKE-001 --title "Check API feasibility" --role backend-engineer --skill feature-implementation --acceptance "Report measured API behavior and discard experimental code" --spike-reason "Measure whether the integration is technically feasible" --spike-scope "Disposable local prototype using synthetic data; no production writes" --spike-hours 24
```

Each reason/scope is 15-500 characters. Eligibility lasts 1-168 hours (default 24)
from task creation and allows one claimed run or manual submission. Retry cannot
reuse the exception; create a new scoped experiment if needed. Child tasks require
their own scope. Exceptions are persisted in the task, audit, memory export and
runner prompt, and do not waive design/dependency gates. They are declarations,
not filesystem isolation or authorization for production access.

Upgrade behavior: existing execution tasks receive the normal implementation
gate, without changing their status, run history or inception approvals. Already
running work is not interrupted by this gate. Previously queued tasks may now be
blocked until inception is finished. There is no blanket project bypass.
