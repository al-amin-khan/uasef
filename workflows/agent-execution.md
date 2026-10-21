# Workflow: Agent Execution and Orchestration (v0.2)

1. Product/architecture agent approves scoped change and contract.
2. Orchestrator creates task with explicit role, skill, acceptance criteria and dependencies.
3. Context builder assembles approved instructions and referenced local documents; nothing is silently injected from another model's private memory.
4. Manual mode exports the prompt, or opt-in subprocess mode claims a lease and executes an external configured CLI.
5. Optional Git worktree isolates branch changes across workers.
6. External runner returns exit status and log; success means `awaiting_review`, never `completed`.
7. Independent reviewer checks actual changes, acceptance criteria, builds/security/test evidence and records evidence.
8. Human approval gate, if required, remains blocked until local declaration plus real external authorization controls.
9. Task becomes completed; dependents can then be dispatched.
10. Failure requires inspection and explicit retry; expired leases require recovery and orphan-process assessment.
