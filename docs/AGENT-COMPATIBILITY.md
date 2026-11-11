# Model and coding-agent compatibility

Agent Skills spec: https://agentskills.io/specification. Skills use exact directory matching and required YAML `name` and `description` frontmatter. Role contracts and global policies remain Markdown so adapters do not embed vendor-only commands.

- Canonical portable skills installed at `.agents/skills/<name>/SKILL.md`. Some coding agents natively discover this directory; otherwise instruct the agent to read these files explicitly.
- Claude Code supports project skills in `.claude/skills/<name>/SKILL.md`; UASEF copies to this path with `--adapter claude` or `all`.
- GitHub Copilot custom agents can use `.github/agents/<role>.agent.md` and project instructions at `.github/copilot-instructions.md`; UASEF generates these role profiles with `--adapter copilot` or `all`.
- Other models (local or hosted) can use the same role, skills and repo state when their application supports reading files and invoking appropriate tools.

Skill loading, tool permissions, prompt priority, subagents and execution semantics differ between providers. 'Model agnostic' means *portable documented work*, not identical tool capabilities or direct sharing of a model's private thoughts.

Known portability caveat: tooling may ignore portable skills without an enabled loader; file copies can become stale if edited in only one location. Review local files and avoid running unknown third-party skills with privileged tools.

- OpenCode discovers `.agents/skills` natively; `--adapter opencode` generates `.opencode/agents` role profiles. See [OPENCODE.md](OPENCODE.md) for opt-in runner integration and limitations.
