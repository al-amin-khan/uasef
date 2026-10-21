# UASEF — Universal AI Software Engineering Framework

**Version 0.2.0 · role-based Agent Skills + project inception + transactional local orchestration**

UASEF starts with an idea, coordinates role-specific AI work through portable skills and versioned specifications, evaluates buy/adopt/build and technology choices, and moves from MVP delivery toward evidence-based production evolution. It intentionally does **not** impose JavaScript, Rust, React, SQL or any other stack.

**What is implemented now:** 23 open-format Agent Skills, 13 specialist role contracts, 16 project-initiation tasks with 4 human-recorded approvals, 10 additional workflow playbooks, project-ready document templates, decision/quality/security policies, a cross-provider adapter exporter, CLI state machine, handoff generator and unit tests.

**What is not implemented:** authenticated approvals, autonomous third-party research, managed cloud deployments, built-in AI model SDKs, hardened process sandboxing or semantic validation of generated documents. v0.2 executes user-configured external AI CLIs, optionally in Git worktrees, and separates runner success from verified completion. Hook these into your chosen coding agent and CI/hosting environment. A generated readiness file does not prove a system is safe or production ready.

## Quick start (Windows PowerShell, Linux, macOS)

Python **3.10+** required. From this **extracted repository**:

```bash
python -m pip install -e .
uasef init ../my-product --name "My Product" --idea "I want to..." --adapter all
cd ../my-product
uasef next
uasef start INIT-001
```

Open the listed draft document(s), work through discovery with an AI agent using the `project-inception` skill and `product-manager` role, replace the `TODO:` sections with actual evidence and identified unknowns, then:

```bash
uasef complete INIT-001
uasef next
uasef start INIT-002
# ... continue each step ...
```

For human-gated tasks 005, 006, 011 and 016, `complete` moves to `awaiting_approval`:

```bash
uasef approve INIT-005 --note "Reviewed feasibility report and accepted disclosed risks"
```

Approval is a **local state declaration**. Use GitHub protected branches/reviewers and deployment environment controls for meaningful authorization.

Other commands:

```bash
uasef status                     # full inception state
uasef validate                   # structural checks; not content correctness
uasef handoff                    # cross-model handoff summary
uasef feature booking-workflow   # feature-spec package after inception
uasef init . --existing          # safely add to existing project; no clobber
```

You can execute the CLI from any directory using `--project /path/to/project`.


## v0.2: Agent Execution and Orchestration

New commands add **transactional SQLite task state**, DAG dependencies, review/approval gates, audit events, run logs, time-limited leases and recovery. Default `manual` mode prepares prompts only; actual execution requires configuring an external CLI and passing `--execute`. **A model does not automatically get shell or deployment access.**

```bash
# After initialization, inside a UASEF project
uasef task add API-001 --title "Health endpoint" --role backend-engineer \
  --skill feature-implementation --acceptance "Endpoint returns 200 and tests pass"
uasef task list
uasef dispatch API-001 --profile manual
# Optional, once a reviewed subprocess runner has been configured:
uasef dispatch API-001 --profile my-agent --execute --worktree
# After actual code/test review and a saved evidence report:
uasef task verify API-001 --reviewer qa-reviewer --evidence docs/evidence/review.md
```

For projects already initialized with v0.1, use `uasef upgrade --project /path/to/project --adapter all` to install missing v0.2 files without overwriting customizations.

Read **[docs/ORCHESTRATION.md](docs/ORCHESTRATION.md)** for runner configuration, independent review, parallel dispatch, approval and recovery. A successful CLI exit does not prove correctness or replace your permission controls.

## Using with different AI tools

| Tool | Generated location | Notes |
|---|---|---|
| Codex and Agent Skills-compatible tools | `.agents/skills/<skill>/SKILL.md` | Role contracts at `.uasef/roles/`; read `AGENTS.md`. |
| Claude Code | `.claude/skills/<skill>/SKILL.md`, `CLAUDE.md` | Native skills discovered by skill metadata; activate desired role in your prompt. |
| GitHub Copilot / VS Code | `.github/agents/<role>.agent.md`, `.github/copilot-instructions.md` | Exposes explicit custom agent role profiles; skills may need supported VS Code configuration. |
| Other agents/models | `.agents/skills/`, `.uasef/roles/`, `AGENTS.md` | Load files explicitly; no shared hidden model memory assumed. |

The `--adapter all` option *copies* skills into each tool's discovery path for portability. These copies can diverge after edits: edit canonical skills in the framework and review updates manually. The CLI deliberately avoids overwriting local customized files.

## Start a session with your agent

> Read AGENTS.md and `.uasef/state.json`. Act as the Product Manager using the `project-inception` skill. Inspect `uasef next`, start the next eligible INIT task and guide discovery. Save the authoritative document; distinguish verified facts from assumptions; do not choose a stack early and do not self-approve gates.

For a technology decision ask: **"Act as Software Architect, use technology-selection and decision-records, evaluate hard constraints and 2–4 candidates using current documentation, record an ADR, and wait for approval."**

For a new feature ask: **"Use feature-planning, build-vs-buy, and feature-implementation; check existing packages and actual project capabilities before new code, and verify acceptance criteria."**

## Repository map

- `skills/`: portable Agent Skills-standard `SKILL.md` manifests.
- `agents/`: role mandates, inputs, decision limits and handoffs.
- `workflows/inception.json`: task graph, role assignment, output files, approval flags.
- `workflows/*.md`: continuous delivery / operational playbooks.
- `policies/`: engineering constitution, architecture, research, security and gates.
- `templates/`: starter documents copied to each new project.
- `src/uasef/cli.py`: local CLI + JSON state transitions.
- `tests/`: unit tests and safety cases.
- `docs/`: operational, extensibility and limitation guides.

## Project lifecycle

`idea → discovery → research → feasibility → MVP PRD/SRS → UX → technology evaluation → architecture/NFR → backlog/test strategy → independent readiness approval → feature slices → releases → measured evolution`

Full INIT-001 to INIT-016 definitions are in `workflows/inception.json` and `docs/INITIATION.md`. Keep this framework **versioned separately** from project code; any project can make its own architectural decisions.

## Design decisions and security

- Everything works offline for framework and local task management. External research itself requires enabled web access from the chosen agent and must cite evidence.
- Inception state remains a mutable JSON file (do not edit concurrently); execution tasks use transactional SQLite with task leases, dependencies and audit records.
- Skills are *instructions* and not security sandboxes. Never grant autonomous production credentials merely because an agent role sounds trustworthy.
- Template completeness is checked structurally (`TODO:` detection), **not semantically**. Human/agent peer review and runnable tests remain mandatory.
- Editable install or running from the source checkout is required; this repository does not yet publish a standalone wheel with bundled resource data.

## Run tests

```bash
python -m unittest discover -s tests -v
```

See `docs/USAGE.md` for a full walkthrough, `docs/AGENT-COMPATIBILITY.md` for adapter details, and `docs/LIMITATIONS.md` for the exact automation boundary.

License: MIT. See `LICENSE`.

## Publishing to GitHub

This distribution is Git-ready but has no remote by default. Follow [docs/GITHUB-PUBLISH.md](docs/GITHUB-PUBLISH.md) to create an empty repository and push safely. Never push a project to an unrelated existing repository.
