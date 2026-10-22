# OpenCode CLI integration (experimental, v0.3.x)

UASEF uses the **documented OpenCode CLI**, not a provider-specific model SDK.
The canonical Agent Skills in `.agents/skills/` are already discovered by OpenCode.
`--adapter opencode` (or `all`) also generates `.opencode/agents/*.md` from
UASEF role contracts. These agents are **subagents**, not authenticated principals.

Official references: https://opencode.ai/docs/cli/ and https://opencode.ai/docs/skills

## Requirements

- Install the OpenCode CLI separately and configure its authentication/model.
- Run `opencode run --help` to confirm support for `--file`, `--format`, and `--agent`.
- Install UASEF from its source checkout: `python -m pip install -e .`.
- Initialize a new project with `uasef init ./example --adapter opencode` or
  add missing agent definitions with `uasef upgrade --project ./example --adapter opencode`.
- Commit `.agents/skills`, `.opencode/agents`, `AGENTS.md` and other required project
  instructions before using `--worktree`. Uncommitted files are absent in Git worktrees.

## Configure

Copy the **profile contents**, not the whole file if you have existing profiles,
from `examples/runners.opencode.json` to the target project's `.uasef/runners.json`.

`argv` is the executable prefix (normally `["opencode"]`). UASEF appends
`run --format json --agent build --file <task-file> <instruction>`.
An optional `model` field accepts an OpenCode `provider/model` ID; omit it to use
OpenCode's configured default. An optional `env_allowlist` is an array of
provider-specific environment variable names such as `ANTHROPIC_API_KEY`.
The adapter deliberately passes only basic OS environment variables plus this
explicit allowlist, instead of forwarding all secrets in the parent environment.

```bash
uasef opencode doctor --project ./example
uasef task add API-001 --title "Add health endpoint" --role backend-engineer \
  --skill feature-implementation --acceptance "Health endpoint returns 200; tests pass" \
  --project ./example
uasef dispatch API-001 --profile opencode --project ./example
# Inspect the prompt, profile and OpenCode permissions first.
uasef dispatch API-001 --profile opencode --execute --project ./example
# For parallel tasks in a committed Git repository, add --worktree.
```

**Safety:** `--execute` launches an agent with the operating-system user's rights.
A Git worktree is not a security sandbox. OpenCode's own tool permissions and
provider credentials must be configured by the operator; UASEF does not silently
approve actions. `--file` supplies the full task prompt without shell argument
length limits. OpenCode's stdout NDJSON is saved in `runner.log`, stderr in
`runner.stderr.log`, and a basic summary in `opencode-summary.json`.

A zero exit code and nonempty JSON event stream move the task to
`awaiting_review` only. They do **not** verify changes, tests or safety. Error
events and empty streams mark the run failed. Use independent test evidence and
`uasef task verify` to finish. No automatic OpenCode session resume or model
availability probing is claimed in this version; UASEF Markdown session handoffs
still work. The `doctor` command does not contact a model.

**Live OpenCode execution has not been verified in the release test environment.**
Mock CLI contract tests cover argument delivery, attached prompt contents,
structured error handling, environment filtering, and UASEF state transitions.
