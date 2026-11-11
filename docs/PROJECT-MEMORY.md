# Project memory and Git traceability

UASEF 0.4 records how a project develops from its initial idea. Every initialized
project gets `docs/project-memory/`, containing `project.json`, a starting guide,
and one JSON file per record in `records/`. Commit this directory with your work.
No hosted model, database server, embedding service, or additional dependency is
required. Records can be read directly by any coding assistant.

## Start a new project or upgrade an existing one

```powershell
uasef init ../inventory --idea "Help stores reconcile inventory"
cd ../inventory
uasef memory brief
```

For an existing UASEF project, install the updated source checkout and run:

```powershell
uasef upgrade --project .
uasef memory brief
```

Upgrade preserves customized AGENTS.md, existing task state, and old memory
records. It adds `.uasef/PROJECT-MEMORY.md` as a discovery note; add its session
instructions to customized agent entry points yourself. `uasef memory init`
can enable memory independently on an older initialized project.
Earlier task/session declarations are imported when their local state is
available. Missing conversations or earlier unrecorded reasons cannot be recovered.

## Preserve the evolution of your thinking

Store what was actually said or decided, including the reason, alternatives,
constraints, and what to do next. Supported user record kinds are `idea`,
`requirement`, `decision`, `preference`, `finding`, `verification`, and `brief`.

```powershell
uasef memory add requirement --title "Fast updates" --text "Inventory updates must appear within five seconds; staff compare two screens."
```

The command prints a stable `MEM-...` ID. Use the returned IDs below; placeholder
values are not real IDs. A decision can link to several requirements with repeated
`--link` arguments. `--task` must identify an existing or historically captured task.

```powershell
uasef memory add decision --title "Queue updates" --text "Use a queue to absorb peak bursts. Alternative considered: synchronous writes, which blocked operators." --link MEM-REQUIREMENT_ID --task API-001 --actor owner
uasef memory add preference --title "Possible preference" --text "The owner appears to prefer small incremental changes." --claim inferred --actor model-A
uasef memory add brief --title "Current state and next steps" --text "API contract agreed. Queue implementation underway. Next: measure peak latency. Open question: retention period."
```

`declared` is the default claim. Use `inferred` for a model interpretation.
`confirmed` should represent an explicit confirmation from the named source; it
is an unauthenticated label, not a permission or approval mechanism. UASEF does
not infer a personality, train a model, capture hidden reasoning, or read chat
histories. A model's interpretation must not silently become an owner preference.

To change a decision, append another record of the same kind:

```powershell
uasef memory add decision --title "Batch queue writes" --text "Peak testing showed disk contention. Batch queued writes while preserving the latency target." --supersedes MEM-OLD_DECISION_ID --link MEM-REQUIREMENT_ID --task API-001
```

The earlier decision remains unchanged. The current brief excludes superseded
records, while list/show/trace preserve them. Conflicting replacements from
parallel branches remain visible; reconcile them with a new decision instead of
silently rewriting history.

## Connect requirements to code and verification

The intended chain is requirement -> decision -> task -> commit -> verification.
Stable memory IDs, `--link`, and `--task` connect the records. Capture a code commit
after it exists, using its SHA rather than a mutable branch name:

```powershell
uasef memory add verification --title "Peak latency result" --text "Measured four seconds under the documented load; see test report for limits." --link MEM-DECISION_ID --task API-001 --commit COMMIT_SHA --evidence docs/verification/peak-test.md --actor reviewer
uasef memory trace MEM-REQUIREMENT_ID
uasef memory trace API-001
uasef memory validate
```

`--commit` verifies and stores an existing commit SHA. Every record also captures
the observed HEAD, branch and dirty status when available; that observed HEAD is
context, not a claim that the record's implementation is in that commit.
Evidence includes a project-relative path and SHA-256 of its bytes at capture.
`memory validate` checks links and flags missing or changed evidence; it does not
rerun tests or certify a test result. Commit evidence files with related code.
Restricted evidence paths such as `.env`, private keys, and paths outside the
project are rejected. Free-text records and session messages still require care:
never put credentials, secrets, or raw private conversations into them.

## Automatic capture and model handoffs

Project initialization records the initial idea. Inception state saves and
orchestration database context exits export task snapshots, audit declarations,
and explicit session notes/checkpoints. Repeated syncs do not duplicate records.
Run outcomes and independent-review declarations remain distinct from proof that
tests passed. Raw runner logs, database lease tokens, environment variables, and
provider credentials are not copied into memory. Automatic audit entries preserve
declared evidence paths; use a verification record for evidence hashes and an
explicit implementation commit link.

```powershell
uasef memory sync
uasef memory brief
uasef memory brief --task API-001 --limit 12
uasef memory list --kind decision
uasef memory list --search "disk contention"
uasef memory show MEM-RECORD_ID
uasef handoff
```

Scoped task prompts, project handoffs, and exported session handoffs include a
bounded memory brief. It prioritizes task-related declarations and current briefs,
marks claim types, shows recent task state, and tells the successor how to retrieve
omitted history. Long texts are excerpts, not complete records. Agents still need
to read linked records and actual files before acting. Initial idea, declarations,
and explicit session checkpoints should be recorded as work proceeds; UASEF cannot
capture a discussion that happens entirely outside its commands.

SQLite is still authoritative for current execution state, and `.uasef/state.json`
for inception state. Memory is an exported history, not a second scheduler. A
clone retains committed history even without the ignored SQLite database; it does
not reconstruct runnable tasks, leases, or sessions from memory. Imported older
events retain their original timestamps, while Git context reflects import time.

## Git checkpoints

Memory files are ordinary versioned files. Commit them alongside implementation
changes using your regular review workflow, or make a separate memory checkpoint:

```powershell
git config user.name "Your Name"
git config user.email "you@example.com"
uasef memory checkpoint --init-git --message "docs: preserve project inception"
uasef memory checkpoint --message "docs: record current decisions"
```

Git initialization requires the explicit `--init-git` flag. Checkpoints require
the project itself to be the repository root and refuse a parent repository.
They stage and commit only `docs/project-memory/`, preserving unrelated staged
work. They never push, merge, create PRs, or change Git identity. An unchanged
memory produces no new commit. Existing ignore rules are respected; ignored
memory must be reconciled before checkpointing.

Records are append-only through the CLI and stored separately to reduce parallel
write conflicts. They are not tamper-proof: someone with filesystem/Git access can
edit them. Git review, backup, and remote branch protection remain your controls.
File scanning and synchronization are proportional to recorded history; there is
no semantic retrieval service or distributed merge coordinator in this version.
