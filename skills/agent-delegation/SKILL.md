---
name: agent-delegation
description: Decompose a parent task into scoped children using explicit reviewer and completion barriers.
---

# Agent Delegation

Review parent acceptance criteria, identify independently verifiable subtask. Delegate using uasef task delegate CHILD --parent PARENT --title "..." --role ... --skill ... --acceptance "...". Avoid duplicate work and enforce depth limit. A parent cannot complete review or approval while children remain incomplete. Run uasef task tree and record handoffs; never delegate uncontrolled production permissions.
