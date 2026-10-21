---
name: agent-routing
description: Select configured coding profiles for scoped tasks; inspect role/skill allowlists and never execute without opt-in.
---

# Agent Routing

Read .uasef/runners.json and run uasef route --task ID. Compare candidate models for required capabilities; role and skill permissions must match. Use uasef dispatch ID --profile auto to preview. Only use --execute with explicit operator authorization. No automatic runner fallback after a command begins or fails: review failure and potential side effects before retry.
