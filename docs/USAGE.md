# Walkthrough: From idea to first feature

## 1. Initialize
```bash
python -m pip install -e .
uasef init ../inventory-concept --name 'Inventory Concept' --idea 'Small retailers need stock visibility and reorder suggestions.' --adapter all
cd ../inventory-concept
```

## 2. Ask a compatible AI coding assistant
> Read AGENTS.md, role product-manager, and skill project-inception. Use the current task from `uasef next`, extract known facts, ask only missing high-impact questions, do not choose any stack or silently invent market evidence. Write the required docs and list assumptions distinctly.

## 3. Complete tasks
```bash
uasef next
uasef start INIT-001
# Human/AI writes the draft under docs/00-inception/idea-brief.md.
# The CLI refuses completion while TODO template sections remain.
uasef complete INIT-001
uasef start INIT-002
```

At each task consult the listed `role` and activate its relevant skill(s). Supply browse/terminal tools to an agent if external verification or code execution is required. Actual file edits and research come from the agent you use, not the CLI.

## 4. Capture real approval at gates
Gate IDs are 005, 006, 011, 016. The owner reviews the underlying artifacts and then records their approval; in a team setting, keep signed PR reviews separate.

## 5. Create first feature package
```bash
uasef feature stock-adjustment
```

A folder `specs/features/stock-adjustment/` contains proposal, requirements, design, tasks, verification. Complete it with relevant role skills. For subsequent changes use `workflows/feature-development.md`.

## 6. Switch models
```bash
uasef handoff
```

Give the successor agent `.uasef/handoff.md`, the repo and the relevant specs. Require independent branch/commit and test verification. Do not send secrets.

## 7. Evolve
Gather real traffic/latency/error/SLO metrics and trigger `production-evolution` only when evidence warrants architectural changes. Do not plan hypothetical microservices because of aspirational user counts.

## Common problems
- **Target not empty:** pass `--existing` (never automatically overwrites files).
- **Task blocked:** finish dependency first; `uasef next` explains.
- **Unfinished template:** replace each `TODO:` with substantive, source-backed information. Mark unknowns explicitly.
- **Approval pending:** request real owner review; `uasef approve --note ...` is bookkeeping only.
- **Skills not detected:** confirm your coding tool's skill search location and availability; see compatibility guide.
