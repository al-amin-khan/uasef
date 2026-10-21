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

## 2. Manual mode — safe by default

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
