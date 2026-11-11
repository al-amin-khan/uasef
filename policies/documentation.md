# Documentation and traceability policy

Documents must have an owner, status, last-reviewed date, requirement IDs where relevant, evidence and known unknowns. Create docs proportional to complexity. Consolidate related notes instead of maintaining duplicate contradictory specifications. Keep current behavior distinct from proposed changes.

Recommended trace: business objective → user story → REQ-ID → screen/API/data design → implementation task → test → release evidence. For an unimplemented interface, label it proposed. For current code, verify commit. Keep real diagrams and contracts in text-first portable formats where practical.

Change requests update the smallest affected artifacts and record the reason; do not blindly regenerate all docs.
