---
name: agent-session-memory
description: Persist bounded session checkpoints so another model can resume a task without prior conversation.
---

# Agent Session Memory

Begin with uasef session start --task ID --name "...". Record factual checkpoints with uasef session checkpoint ID --message "..." --evidence path. Use uasef session handoff ID to generate a portable Markdown document. For model switches, verify the repo HEAD, task state, evidence files and any open approvals. Sessions do not capture hidden model reasoning and are not authoritative over verified source or tests.
