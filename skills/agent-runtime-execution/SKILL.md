---
name: agent-runtime-execution
description: Dispatch a task to a configured external CLI agent with bounded execution, opt-in permissions and reviewable run artifacts.
---

# Agent Runtime Execution

## Purpose
Execute one approved scoped task through a configured runner; preserve model portability.

## Preconditions
- Inspect `.uasef/runners.json`, `uasef runners`, task acceptance criteria, and project permissions.
- Do not add secrets to profile argv or prompt context. Verify the installed CLI and its policy before enabling execution.
- An opt-in subprocess is not a sandbox. A Git worktree isolates Git changes, not OS access.

## Procedure
1. `uasef dispatch TASK-ID --profile manual` writes a prompt; no process runs and task stays queued.
2. Review a subprocess runner profile before `--execute`.
3. Prefer `--worktree` for coding agents; use `--jobs N --worktree` for concurrency.
4. Inspect `.uasef/runs/<run-id>/runner.log` locally; it may contain sensitive content.
5. If exit code is zero, send the work to independent review; if nonzero, inspect before `uasef task retry`.
6. On interrupted tasks, use `uasef task recover` only after verifying the worker is stopped.

## Human approval
Sensitive tools, credentials, network use and production actions remain subject to separate human authorization.

## Deliverable
Scoped prompt, run metadata, workspace and audit, plus honest test evidence and next steps.
