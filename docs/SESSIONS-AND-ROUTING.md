# v0.3 — Sessions, delegation and model routing

UASEF is a **local CLI coordinator**. It does not provision provider accounts, exchange hidden model memory, authenticate identities, or guarantee agent isolation. Configured CLI subprocesses run as your user. All executions remain opt-in.

## 1. Persistent task sessions

```bash
uasef task add API-001 --title "An endpoint" --role backend-engineer --skill feature-implementation --acceptance "An integration test verifies the API"
uasef session start --task API-001 --name "API investigation"
uasef session list
uasef session checkpoint <session-id> --message "Discovered approved API contract v2" --evidence docs/03-engineering/api-contract.yaml
uasef session handoff <session-id>
uasef dispatch API-001 --profile manual --session <session-id>
```

Sessions are stored in `.uasef/orchestration.sqlite3`, with append-only events. Handoff Markdown lives in `.uasef/sessions/<id>/handoff.md` and is Git-ignored. Do not record secrets or sensitive personal information in checkpoints. A checkpoint records agent assertions; verify actual files, commits and tests when resuming. You may continue with another configured `--profile` against the same session. `--session` is supported for single-task dispatch, not bulk dispatch.

## 2. Delegation

```bash
uasef task delegate API-TEST-001 --parent API-001 --title "Test endpoint" --role qa-engineer --skill quality-verification --acceptance "Tests cover success and failure"
uasef task tree
```

Child tasks carry a parent ID and are audited. Parent review and approval are blocked until all direct children complete, and descendants are transitively blocked. Delegation depth is bounded. No autonomous subagent is spawned automatically: task creation and external CLI dispatch are separate.

## 3. Model/profile routing

Example `.uasef/runners.json`:

```json
{
  "profiles": {
    "manual": {"type": "manual"},
    "local-code": {"type": "subprocess", "argv": ["your-installed-cli", "--headless"], "roles": ["backend-engineer"], "enabled": true, "timeout_seconds": 600},
    "cloud-review": {"type": "subprocess", "argv": ["your-reviewed-cli", "--noninteractive"], "roles": ["qa-engineer"], "enabled": true, "timeout_seconds": 600}
  },
  "routing": {
    "defaults": [],
    "by_role": {"backend-engineer": ["local-code"], "qa-engineer": ["cloud-review"]}
  }
}
```

These are **illustrative commands**, not verified vendor CLI syntax. `uasef route --task API-001` explains candidates and reasons. `uasef dispatch API-001 --profile auto` selects the first matching enabled subprocess without launching it. Add `--execute` only after reviewing its permissions, worktree policy, and the actual CLI's command-line contract. If a command exits unsuccessfully, UASEF does not silently execute a different provider: ambiguous side effects require human examination.

`runners.json` is not intended to contain credentials. Use provider-specific secret management. Git worktrees isolate Git changes, not the OS, process permissions, network or secrets. CI and protected branches remain the real verification/authorization layers.

## 4. v0.2 migration

Run `uasef upgrade --project /path/to/existing-project --adapter all`. Opening the project execution database applies an additive `parent_id` schema migration; original tasks and run evidence remain. The project-specific `.uasef/runners.json` is **not overwritten**, so add routing manually. Existing agent files are also not overwritten; review changes explicitly.
