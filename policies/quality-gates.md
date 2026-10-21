# Quality gates / evidence rules

Minimum for code: requirements traceability; type/build/lint where supported; deterministic relevant tests; dependency/security review; independent review for substantive changes; merge through protected CI. For data changes add migration rollback/recovery, backup and integrity checks. For UIs add loading/error/empty/permission/accessibility tests. For performance-critical changes include reproducible benchmark or measurement.

Report exact command, environment, commit SHA, exit status, known test omissions and output link. If checks cannot run, mark NOT RUN with reason; never mark PASS based on expectation.

Definition of Done is acceptance tests verified, defects triaged, documentation aligned, operational implications reviewed, release/approval gate satisfied.
