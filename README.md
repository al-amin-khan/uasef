# UASEF — Universal AI Software Engineering Framework

**v0.3.0 + experimental OpenCode integration.** UASEF provides portable Agent Skills, specialist role contracts, evidence-based project inception, task orchestration, persistent handoffs, and human-controlled quality gates. It is **model-agnostic and technology-stack-agnostic**.

> **Starting with only an idea?** Follow [the complete zero-to-production walkthrough](#complete-walkthrough-from-zero-prompt-to-production). UASEF is a workflow coordinator, **not** an autonomous one-prompt software factory. An installed AI coding agent does the research and coding; you review important decisions and verify results.

## Table of contents

- [What UASEF can and cannot do](#what-uasef-can-and-cannot-do)
- [Install the framework and OpenCode](#install-the-framework-and-opencode)
- [Complete walkthrough: from zero prompt to production](#complete-walkthrough-from-zero-prompt-to-production)
  - [Phase 0 — Start with an idea](#phase-0--start-with-an-idea)
  - [Phase 1 — Discover, specify and approve](#phase-1--discover-specify-and-approve)
  - [Phase 2 — Prepare the engineering foundation](#phase-2--prepare-the-engineering-foundation)
  - [Phase 3 — Implement features in vertical slices](#phase-3--implement-features-in-vertical-slices)
  - [Phase 4 — Integrate, test and harden](#phase-4--integrate-test-and-harden)
  - [Phase 5 — Release to production](#phase-5--release-to-production)
  - [Phase 6 — Operate and improve](#phase-6--operate-and-improve)
- [Advanced orchestration](#advanced-orchestration)
- [Reusable agent prompts](#reusable-agent-prompts)
- [Troubleshooting, safety and limitations](#troubleshooting-safety-and-limitations)
- [Reference documentation](#reference-documentation)

## What UASEF can and cannot do

| Area | Implemented | Still requires human/external tooling |
| --- | --- | --- |
| Project initiation | 16 dependency-ordered tasks, templates, roles, approval records | Genuine discovery, sourced research, accurate specs |
| Architecture | Research and ADR skills, policies, NFR templates | Trade-off analysis and approval of a suitable stack |
| Coding | SQLite task DAG, runner profiles, scoped prompts, logs and retries | Installed coding agent and real implementation |
| OpenCode | Agent exporter, task-file runner, JSON log inspection | Provider authentication, model access, permission configuration |
| Multi-agent work | Role routing, delegation records, checkpoints and handoffs | Autonomous delegation, merge conflict resolution |
| Quality | Review and approval state transitions | Real tests, independent review, authenticated authorization |
| Operations | Deployment/security templates and workflow playbooks | CI/CD, hosting, monitoring, backups, real deployment |

**Boundaries:** UASEF does not automatically create a complete application from one prompt, validate research truth, authenticate approvers, guarantee secure agent isolation, merge Git worktrees, deploy to production, or resume native OpenCode sessions. OpenCode integration has mock-based tests but has **not** been validated against a real provider-backed model in this project's test environment.

## Install the framework and OpenCode

Requirements: **Python 3.10+**, Git, a terminal, and optionally a supported coding agent. The following commands target **Windows PowerShell**; equivalent Bash commands follow.

```powershell
py --version
git --version
opencode --version
git clone https://github.com/al-amin-khan/uasef.git
cd uasef
py -m pip install -e .
uasef --help
py -m unittest discover -s tests -v
```

Install and configure OpenCode separately using the [official OpenCode documentation](https://opencode.ai/docs/). `opencode --version` only confirms the executable is present; you must configure a working model and review its tool permissions.

**Linux/macOS:**

```bash
git clone https://github.com/al-amin-khan/uasef.git
cd uasef
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
```

UASEF currently requires a source checkout/editable install because the framework resource files are not yet bundled into a standalone published wheel. **Keep the framework checkout separate from each software project.**

## Complete walkthrough: from zero prompt to production

```text
IDEA -> Discovery -> Research -> Feasibility -> PRD/SRS -> UX
     -> Stack ADR -> Architecture/NFR -> Security/Test/Delivery Plan
     -> Human readiness approval -> Feature specs -> Task DAG
     -> AI implementation -> Tests -> Independent review -> Integration
     -> Staging -> Authorized production deployment -> Monitoring
     -> Feedback and next release
```

**Important: two different task systems.** The `uasef start/complete/approve INIT-...` commands manage **inception** in `.uasef/state.json`. The `uasef task add/dispatch/verify/approve` commands manage **implementation** in `.uasef/orchestration.sqlite3`. Completing inception does **not** automatically create implementation tasks or launch a coding agent.

### Phase 0 — Start with an idea

Suppose your only idea is:

> Build a secure, multi-tenant service-management application. Businesses manage customers, work orders, staff, approvals, invoices and reports. It needs mobile-friendly interfaces, an audit trail and a production deployment. I have not selected the technology stack.

**Step 0.1 — Initialize a new product project.** From the **UASEF checkout**:

```powershell
uasef init ..\service-platform --name "Service Platform" --idea "Multi-tenant service management: customers, work orders, staff, approvals, invoicing, reporting and audit trails" --adapter opencode
Copy-Item .\examples\runners.opencode.json ..\service-platform\.uasef\runners.json
cd ..\service-platform
uasef next
uasef status
uasef opencode doctor
```

For a **new** project the example runner replaces the manual-only default. If `.uasef/runners.json` already contains custom profiles, merge the OpenCode profile instead of overwriting it. To add UASEF to an existing nonempty project use `uasef init . --existing --adapter opencode`. For an **already initialized** UASEF project use `uasef upgrade --project . --adapter opencode`.

**Step 0.2 — Open OpenCode in the product directory:**

```powershell
opencode
```

**Paste this as your first prompt:**

> Act as my Product Manager and engineering coordinator. Read AGENTS.md, .uasef/state.json, the project-inception skill and the assigned role contract. Inspect `uasef next` and begin with the first eligible INIT task. Ask high-impact questions about users, workflows, roles, permissions, integrations, constraints, privacy, security, budget, scale and success criteria. Separate verified facts, assumptions and unknowns. Write only the required artifacts for the current task, with sources for external claims. Do not invent research, select a stack prematurely, skip dependencies, approve your own work or start coding. Show changed files, unresolved questions and the next human review action.

You can also ask OpenCode for a noninteractive first consultation:

```powershell
opencode run --agent build "Read AGENTS.md and .uasef/state.json. Explain the next eligible INIT task, missing questions and required artifacts. Do not implement or approve anything."
```

Inception requires conversation and decisions. **A single prompt is the beginning of the process, not an unattended end-to-end execution guarantee.**

### Phase 1 — Discover, specify and approve

**Step 1.1 — Work through the inception task sequence.**

```powershell
uasef next
uasef start INIT-001
# Collaborate with OpenCode to write and review the required task documents.
uasef complete INIT-001
uasef next
uasef start INIT-002
```

For **each** eligible INIT task, ask the agent to read its assigned role/skill and required output paths from [workflows/inception.json](workflows/inception.json), produce the documents, and list unanswered questions. You inspect and correct the documents, remove `TODO:` placeholders, then run `uasef complete INIT-XXX`. The CLI checks obvious unfinished templates; it does **not** judge research accuracy or architectural correctness.

| Task | Expected deliverable | Gate |
| --- | --- | --- |
| INIT-001 | Idea brief | — |
| INIT-002 | Problem discovery and assumptions | — |
| INIT-003 | User research | — |
| INIT-004 | Alternative/competitor analysis | — |
| INIT-005 | Feasibility and go/no-go | **Human approval** |
| INIT-006 | PRD and MVP scope | **Human approval** |
| INIT-007 | Detailed SRS | — |
| INIT-008 | User flows and screen inventory | — |
| INIT-009 | Visual design brief | — |
| INIT-010 | Existing solution and dependency research | — |
| INIT-011 | Technology evaluation and ADR | **Human approval** |
| INIT-012 | Architecture, data model, API contract | — |
| INIT-013 | NFR, security and deployment baseline | — |
| INIT-014 | Prioritized feature backlog and implementation plan | — |
| INIT-015 | Test strategy | — |
| INIT-016 | Independent readiness review | **Human approval** |

**Step 1.2 — Explicit approval gates.** For example, after reading the actual feasibility report:

```powershell
uasef complete INIT-005
uasef approve INIT-005 --note "Reviewed feasibility, costs and risks; approved the defined MVP direction"
```

Repeat the review and approval cycle for INIT-006, INIT-011 and INIT-016. These commands **record local declarations**; they do not authenticate an approver. Use protected branches, required reviewers and CI/CD approvals for real organizational authorization.

**Step 1.3 — Exit criteria.** Before coding, verify that the project has approved users and scope, workflows and permissions, researched alternatives, a justified stack ADR, data/API contracts, security/privacy and tenancy requirements, NFRs, migration/deployment/backup strategy, prioritized small features, and a test plan. Run:

```powershell
uasef status
uasef validate
uasef handoff
```

`validate` is structural only. Do not treat it as proof of a secure or production-ready architecture.

### Phase 2 — Prepare the engineering foundation

**Step 2.1 — Initialize the product's own Git history** (separate from UASEF):

```powershell
git init
git status
git add .
# Review staged files; remove any credentials, .env files or secrets.
git commit -m "chore: baseline approved product specifications"
```

**Step 2.2 — Establish engineering conventions.** Using approved requirements and ADRs, have the coding agent create source layout, lockfiles, formatting/linting/type checks, a test harness, safe `.env.example`, database migrations, CI, review rules, observability baseline and local setup instructions. Do not overengineer infrastructure before measuring actual needs.

**Step 2.3 — Configure OpenCode.** The example `.uasef/runners.json` profile is:

```json
{
  "profiles": {
    "manual": { "type": "manual" },
    "opencode": {
      "type": "opencode",
      "argv": ["opencode"],
      "agent": "build",
      "timeout_seconds": 900,
      "env_allowlist": []
    }
  },
  "routing": { "defaults": ["opencode"], "by_role": {} }
}
```

Configure model credentials and tool permissions **in OpenCode**. The optional `model` field accepts an OpenCode provider/model identifier. The optional `env_allowlist` should contain only necessary environment variable names; never store secret values in tracked files. `uasef opencode doctor` checks executable/CLI flags but **not** authentication or live model access.

### Phase 3 — Implement features in vertical slices

Build a **small usable workflow** end-to-end (UI, API, data and tests as applicable), rather than generating a huge backend and frontend separately with no integration.

**Step 3.1 — Specify a feature:**

```powershell
uasef feature work-order-management
```

The command creates `specs/features/work-order-management/` containing `proposal.md`, `requirements.md`, `design.md`, `tasks.md` and `verification.md`. Ask the agent to fill these from the **approved** PRD/SRS, architecture and contracts. Include happy paths, error paths, permissions, tenant boundaries, concurrency and measurable acceptance criteria. Review before coding.

**Step 3.2 — Create dependency-aware engineering tasks:**

```powershell
uasef task add DATA-001 --title "Work order schema and persistence" --role backend-engineer --skill feature-implementation --context specs/features/work-order-management/requirements.md --acceptance "Approved migration, validation and persistence tests pass"
uasef task add API-001 --title "Work order REST API" --role backend-engineer --skill feature-implementation --depends DATA-001 --context specs/features/work-order-management/design.md --acceptance "API contract, authorization and integration tests pass"
uasef task add UI-001 --title "Work order UI flow" --role frontend-engineer --skill feature-implementation --depends API-001 --acceptance "Accessible create/list/edit flows, error states and UI tests pass"
uasef task list
uasef task tree
```

Context files must exist; role and skill names must match installed project files. Dependent tasks wait until prerequisites have been **completed after review**, not merely until a model exits.

**Step 3.3 — Preview and run an agent:**

```powershell
uasef route --task DATA-001
uasef dispatch DATA-001 --profile opencode
# Inspect the scoped prompt, runner config and permissions.
uasef dispatch DATA-001 --profile opencode --execute
uasef task show DATA-001
```

UASEF attaches the full task prompt to `opencode run` and records logs and JSON event summaries. A successful run becomes `awaiting_review`, **not** `completed`. A real independent review is required. OpenCode live model execution has not yet been validated by this repository's CI.

**Manual alternative:** `uasef dispatch DATA-001 --profile manual` writes a prompt without executing anything. After doing the work and saving a real report, submit:

```powershell
uasef task submit DATA-001 --actor "developer" --evidence docs/evidence/data-001-implementation.md
```

**Step 3.4 — Independently verify.** Have someone other than the implementing runner inspect the diff, run relevant tests, check negative authorization and failure cases, and write an evidence report with exact commands, outcomes, commit/branch and remaining risks. Then:

```powershell
uasef task verify DATA-001 --reviewer "qa-reviewer" --evidence docs/evidence/data-001-review.md
uasef task list
```

For a task created with `--approval-required`, verification moves it to `awaiting_approval`, then a real owner can record:

```powershell
uasef task approve DATA-001 --actor "Project Owner" --note "Reviewed code, test evidence and residual risks"
```

If execution fails, inspect `uasef task show DATA-001` and run logs before `uasef task retry DATA-001`. Repeat **spec → implement → test → review → integrate** for API-001, UI-001 and every subsequent vertical slice. **Never fabricate evidence just to satisfy a state transition.**

### Phase 4 — Integrate, test and harden

Integrate each feature through reviewed pull requests. Execute the **product's real commands** in CI and locally; UASEF cannot infer build/test commands for every stack.

| Layer | What to verify |
| --- | --- |
| Static quality | Formatting, linting, type checking, dependencies, secret scans |
| Unit tests | Business rules, edge cases, validation and errors |
| Integration | Database, API contracts, auth, external services, migrations |
| End-to-end | Critical user journeys and accessible UI |
| Security | Server-side authorization, tenant isolation, injection, secret handling |
| Data safety | Backup/restore, migration correctness, retention |
| Reliability | Idempotency, timeouts, retries, concurrency, recovery |
| Performance | Real measured latency, throughput and resource use vs NFRs |
| Operations | Logs, health checks, monitoring, alerts, runbooks |

For complex software, add realistic fixtures, negative authorization tests, contract compatibility tests, race-condition tests and external-service failure simulations. Link each important requirement to a test or documented manual acceptance procedure. **Exit:** no release-blocking defects; security/data risks reviewed; staging candidate reproducible from a known commit.

### Phase 5 — Release to production

**UASEF does not deploy your application automatically.** Use the approved deployment plan and your project's CI/CD/infrastructure.

1. Provision separate dev/staging/production environments with least-privilege identities and managed secrets.
2. Build an immutable release candidate from a reviewed commit; pin dependencies and run CI/security checks.
3. Test staging using realistic configuration and safe test data; run smoke, integration and E2E checks.
4. Rehearse migrations, backup/restore and rollback or roll-forward recovery.
5. Prepare monitoring, alerts, SLOs, incident contacts, runbooks, capacity and cost controls.
6. Obtain **explicit authorized human approval** for the release, change window and rollback criteria.
7. Deploy with health checks and a suitable rolling/blue-green/canary strategy where justified.
8. Verify production user journeys, authorization, error rates, latency, database health and alerts.
9. Record the deployed commit/tag, migration versions, release notes, known issues and follow-up actions.

**Example release checklist** (save in your product repository):

```markdown
# Release readiness — VERSION
- [ ] Approved scope and acceptance results
- [ ] CI build, unit, integration and E2E checks pass on release commit
- [ ] Security review, dependency and secret scans complete
- [ ] Database migrations and restore/rollback rehearsed
- [ ] Staging acceptance passed
- [ ] Production configuration, monitoring and alerts ready
- [ ] Runbook, support owner and incident contacts confirmed
- [ ] Authorized human deployment approval recorded
- [ ] Production smoke tests and metrics verified
- [ ] Release notes and residual risks documented
```

Do **not** grant an autonomous agent unrestricted production credentials. Enforce approvals through protected source-control branches and deployment environments, not just UASEF's local text fields.

### Phase 6 — Operate and improve

Track real user feedback, incidents, error budgets, security events, performance and costs. Prioritize new work from evidence, not hypothetical future scale. For each enhancement run `uasef feature new-feature-slug`, create scoped tasks, test/review them and ship a new approved release. For incidents, stabilize the system, preserve evidence, recover safely, document root cause and add regression tests. Use `uasef handoff` when switching models; verify the actual repository state when resuming.

## Advanced orchestration

**Parallel workers:** once the product Git repository has a committed baseline, independent ready tasks can run in separate worktrees:

```powershell
uasef dispatch-ready --profile opencode --execute --limit 2 --jobs 2 --worktree
```

UASEF does **not** merge or clean up worktrees. Review and integrate branches manually, and avoid simultaneous edits to shared schemas/contracts. Worktrees are **not** security sandboxes.

**Persistent checkpoints and handoffs:**

```powershell
uasef session start --task API-001 --name "Work order API implementation"
uasef session list
# Replace SESSION_ID with the 32-character ID printed above.
uasef session checkpoint SESSION_ID --message "Reviewed approved API contract; tests pending" --evidence docs/03-engineering/api-contract.yaml
uasef session handoff SESSION_ID
uasef dispatch API-001 --profile opencode --session SESSION_ID
```

The handoff contains explicit notes and references, **not** OpenCode's private conversation or native session resumption. Add `--execute` only after previewing the scoped prompt.

**Delegation:**

```powershell
uasef task delegate API-TEST-001 --parent API-001 --title "Verify API and access controls" --role qa-engineer --skill quality-verification --acceptance "Integration and negative authorization tests pass"
uasef task tree
```

Delegation creates a child task; it does **not** automatically spawn an agent. A parent cannot pass review while delegated children remain incomplete.

**Role-aware routing:** set `routing.by_role` in `.uasef/runners.json`, then run `uasef route --task API-001` and `uasef dispatch API-001 --profile auto`. Routing selects configured profiles; it does not prove a provider/model is available.

## Reusable agent prompts

Paste these into a compatible coding assistant, **not** the UASEF CLI:

**Discovery:** “Read AGENTS.md, the current INIT task and project-inception skill. Act as Product Manager/Business Analyst. Ask only high-impact unanswered questions. Separate confirmed facts, assumptions and sourced research. Write the required task documents and ask for my review. Do not choose a stack or self-approve.”

**Architecture:** “Read approved PRD/SRS and NFRs. Act as Software Architect. Compare 2–4 feasible stacks and architectures against cost, security, team skills, deployment and maintenance. Produce a documented ADR, data/API contracts and migration plan. Prefer the simplest justified solution. Stop at the approval gate.”

**Implementation:** “Read AGENTS.md, approved specifications, relevant ADRs and the current feature package. Implement only the assigned vertical slice. Inspect existing code, use vetted libraries, add validation, authorization, error handling, observability and tests. Run real checks and report exact commands/results, changed files and remaining risks. Do not self-approve.”

**Independent QA:** “Review the actual diff and approved requirements, not the implementer's summary. Run tests; check negative inputs, access control, tenant isolation, concurrency, secrets and failure handling. Record reproducible evidence and severity-ranked findings. Never invent passing tests.”

**Release:** “Review release commit, CI results, staging, security, migrations, backups, rollback, monitoring and runbooks. Produce a go/no-go report and deployment steps. Do not deploy without authorized human approval.”

## Troubleshooting, safety and limitations

| Symptom | Resolution |
| --- | --- |
| `uasef` missing | Check Python environment; install from the UASEF checkout using `python -m pip install -e .` |
| OpenCode unavailable | Install OpenCode, check `opencode --version`, then `uasef opencode doctor` |
| Doctor passes, execution fails | Check model authentication, tool permissions and `.uasef/runs/` logs; doctor does not invoke a model |
| Missing runner profile | Inspect `.uasef/runners.json` and choose `--profile opencode` |
| INIT task blocked | Run `uasef next`; complete prerequisites and human gates |
| Template rejected | Replace `TODO:`/placeholders with substantive reviewed content |
| Engineering task blocked | `uasef task list`; prerequisites must be `completed`, not `awaiting_review` |
| Runner exit 0 but not completed | Expected: `uasef task verify` requires independent evidence |
| Failed run | Inspect `uasef task show TASK-ID`, logs and workspace before retry |
| Interrupted worker | `uasef task recover` marks expired leases failed; stop orphan processes before retrying |
| Worktree lacks new files | Commit project instructions and source before creating worktrees |
| Worktree changes not in product root | Review/merge its branch manually |
| Switching models | Export `uasef handoff` or `uasef session handoff SESSION_ID`; verify actual files and commits |

**Security:** never commit secrets, use least-privilege provider credentials, review agent tool permissions, restrict sensitive logs, do not treat worktrees as sandboxes, independently test changes, and use authenticated source-control/deployment approvals for consequential actions.

## Reference documentation

- [OpenCode integration](docs/OPENCODE.md)
- [Inception task definitions](docs/INITIATION.md) and [workflow manifest](workflows/inception.json)
- [Feature delivery walkthrough](docs/USAGE.md)
- [Execution, review and recovery](docs/ORCHESTRATION.md)
- [Sessions, delegation and routing](docs/SESSIONS-AND-ROUTING.md)
- [Agent compatibility](docs/AGENT-COMPATIBILITY.md)
- [Known limitations](docs/LIMITATIONS.md)
- [Skills](skills/) · [Role contracts](agents/) · [Policies](policies/) · [Workflows](workflows/)
- [Changelog](CHANGELOG.md) · [MIT License](LICENSE)

**Repository layout:** `skills/` holds portable Agent Skills; `agents/` defines roles; `workflows/` and `policies/` define engineering processes; `templates/` contains project documents; `src/uasef/` implements the CLI, orchestration, sessions and OpenCode adapter; `tests/` holds framework tests.

**Lifecycle:** `idea → research → approved requirements → architecture → vertical slices → tests → independent review → staging → approved production release → monitoring → improvement`.
