# Git workflow and optional commit tools

Use `uasef init ../product --git-hooks` or `uasef upgrade --git-hooks` to copy
the configuration into a project. Existing `lefthook.yml` files are preserved.
Install binaries and run `lefthook install` separately after reviewing existing hooks.
CI now runs `scripts/live_git_tools.py` with real Lefthook 2.2.2 and Cocogitto 7.0.0
on Windows and Linux. It tests valid and invalid commits, whitespace rejection,
memory checkpoints, unrelated staging preservation, history validation and upgrades.

UASEF supports isolated Git worktrees, explicit memory checkpoints, commit SHA
references, and evidence hashes. It does not automatically install binaries,
activate hooks, push, merge, protect branches, or publish releases.

This repository includes an optional `lefthook.yml`: pre-commit checks staged
whitespace errors; commit-msg invokes `cog verify --file` on the proposed message.
Lefthook manages hooks and Cocogitto validates Conventional Commits. Configuration
alone does not activate either tool. They are optional external dependencies.

1. Install Lefthook and Cocogitto using their official installation guides.
2. Confirm `lefthook version` and `cog --version` work in the shell used by Git.
3. Inspect `git config --get core.hooksPath` and existing Git hooks. Lefthook can
   replace existing hooks with backups; those backups are not executed. Reconcile
   existing hook logic before installing; do not blindly force installation.
4. For a generated project, copy this repository's `lefthook.yml` only if it has
   no hook configuration, or merge these commands into its existing configuration.
5. Run `lefthook install` explicitly in the intended repository.
6. Test a temporary message file with `cog verify --file message.txt`. A message
   such as `feat(memory): preserve task checkpoints` should pass; `updated stuff`
   should fail. Then check a real commit in a disposable branch.

Memory checkpoints use ordinary `git commit` and therefore run installed hooks.
If a hook fails, no checkpoint commit is created; inspect the index before retry.
Use messages such as `docs(memory): record storage decision`. UASEF leaves your
Git identity and signing configuration to Git and does not bypass hooks.

For normal implementation work, review `git diff`, stage selected changes, run
project-specific tests, and commit code, tests, evidence and related memory
together. Use feature branches and reviewed pull requests. Configure required
CI checks and branch protection on the hosting service. Local hooks can be
bypassed and are not a security boundary. The whitespace hook is not a test,
formatter, secret scanner, or security audit.

`cog check` checks commit history; `cog check --from-latest-tag` can limit checking
to history after the latest tag. Choose a migration boundary for repositories
with older nonconforming commits. Cocogitto release/version automation requires
separate project-specific configuration; this change does not enable releases.

Official references:
- https://lefthook.dev/usage/commands/install.html
- https://github.com/evilmartians/lefthook/blob/master/docs/examples/commitlint.md
- https://github.com/cocogitto/cocogitto/blob/main/website/guide/verify.md
- https://github.com/cocogitto/cocogitto/blob/main/website/guide/check.md
