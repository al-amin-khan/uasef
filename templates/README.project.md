# New software project

This workspace is initialized with **UASEF**, a model-agnostic project inception method.

The project idea and task state are in `.uasef/state.json`. Authoritative specifications and decisions are in `docs/`, while reusable agent skills are in `.agents/skills/` (also `.claude/skills/` when configured). Read `AGENTS.md` first.

Recommended commands (after installing UASEF from its source checkout):

```bash
uasef next
uasef start INIT-001
# Write the document listed in required outputs and replace all TODO sections.
uasef complete INIT-001
uasef status
```

Do not claim automatic execution: the connected agent or human authors and checks the documents. Human approvals are explicit. See the framework README for the complete process.
