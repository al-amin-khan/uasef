# Reliability and memory roadmap delivery

This change implements the remaining local tooling for the proposed v0.5-v0.7
milestones. Those labels are roadmap targets, not a claim that stable releases
were published. The provider-backed agent test remains a separate acceptance gate.

## v0.5: state backup, restore and migrations

```powershell
uasef backup ../project-state.zip --project .
uasef restore ../project-state.zip ../restored-state
uasef upgrade --project ../restored-state
```

Stop workers and other writers first. Backups contain inception state, a consistent
SQLite snapshot (tasks, sessions, events and audit), and project-memory records.
They deliberately exclude source code, Git history, runner credentials/configuration,
raw logs, generated session files, custom policies/skills and other documents.
Keep those files in Git or your normal project backup. This is a state backup,
not a full project backup. State and memory text can still contain private material:
archives are not encrypted; protect them and do not commit them publicly.

Restores require a new nonexistent directory, validate checksums, paths, schema and
database integrity before publishing the directory, and clear execution leases.
They do not execute archive contents or imported runner configuration. Review the
restored state, copy it into a matching source checkout deliberately, regenerate
default framework files with upgrade, and reconfigure runners before dispatching.
References to evidence/logs not included in the archive may need reconstruction.
Checksums detect accidental corruption, not an adversary replacing the archive.
The supported archive format is schema 1, up to 20,000 files and 100 MiB uncompressed.
Backup refuses running tasks; file-change detection cannot replace stopping writers.

Tests cover supported inception upgrades, migration of the pre-parent-column task
schema, repeated upgrades, session/history round trips and corrupt/unsafe archives.

## v0.6: verification and interruption recovery

```powershell
uasef verification run --project . --timeout 300 -- python -m unittest discover -s tests
uasef verification check VER-ID --project .
uasef task verify API-001 --reviewer qa --evidence docs/review.md --verification VER-ID
uasef task recover --actor owner
```

Verification requires a clean Git repository root and records the exact commit,
command arguments, times, exit code and whether HEAD/working-tree state remained
unchanged. Receipt output excludes command stdout/stderr. Never put credentials
in command arguments. Commands run with your privileges and may modify files or
contact networks; use only commands you authorize. Timeouts may leave child
processes; inspect workers before retrying. Passing a command is not proof that
its assertions adequately cover requirements.

Create `.uasef/verification-policy.json` with `{"required":true}` and commit it
to require a current passing receipt at task verification. Legacy projects remain
compatible without that policy. Receipts in `.uasef/verification/` are local and
ignored by Git; they are not signed or authenticated. A changed commit, dirty
working tree, failed check or missing required receipt blocks verification.
The gate applies when task review is recorded; use protected CI for merge/release
enforcement. Later memory exports can dirty the tree, requiring a new checkpoint
and verification before another gated review.

Recovery already marks expired running leases failed instead of silently rerunning
work. Tests now exercise abrupt process exit, repeated recovery, rejecting stale
worker completion and issuing a new lease on retry. Inspect workers/worktrees
before retrying; recovery does not kill processes or merge worktrees.

Run a real agent acceptance test with an explicit configured model:

```powershell
python scripts/live_agent.py --model provider/model --execute
```

This invokes the real OpenCode adapter in a disposable directory and independently
checks the resulting JSON artifact. Global agent permissions/configuration apply;
the directory is not an OS sandbox and provider charges can apply. Pass provider
environment variable names with `--env NAME` only when necessary. Authentication
and permission errors fail the test; mock tests do not count as provider success.
No model ID was supplied during implementation, so this acceptance gate is pending.

## v0.7: history inspection and indexed retrieval

```powershell
uasef memory timeline --limit 100 --offset 0
uasef memory conflicts
uasef memory search "storage latency" --limit 10
uasef memory search "storage" --rebuild
```

The chronological timeline includes original ideas, requirements, decisions,
preferences and verification declarations, links, authors, claim types and whether
a record was superseded. Conflicts report missing references, revision cycles,
competing successors and different active records sharing a title/task. These are
structural or heuristic findings for human review, not semantic contradiction
proof. Nothing resolves or deletes decisions automatically.

Search uses a disposable SQLite FTS5 cache with ranked bounded excerpts, indexes
changed files and removes deleted records. Each query stats the source files;
unchanged documents avoid JSON parsing and full-text scans. This is not constant
time indexing or semantic retrieval. Timestamp/size-preserving edits require
`--rebuild`; authoritative records remain the JSON files. Search can include
superseded decisions; inspect the timeline/record before using one as current.
If FTS5 is unavailable use `memory list --search`. Do not share the derived cache.

Commit messages use Conventional Commit scopes and `Roadmap-Targets` trailers.
No stable v0.6/v0.7 release tag should imply the pending live-agent gate passed.
