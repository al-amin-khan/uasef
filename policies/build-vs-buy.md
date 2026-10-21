# Build / buy / adopt / extend policy

For each nontrivial feature: (1) inspect existing repo or platform capabilities; (2) search established open-source libraries, commercial APIs, managed solutions and standard patterns; (3) identify which domain rules remain custom; (4) assess hard blockers (license, privacy, security, compatibility); (5) evaluate maintenance, stability, integration complexity, lock-in, recurring cost, operational burden, exit plan; (6) prototype uncertain candidate integrations; (7) record a recommendation with source URLs, access dates, versions, and known uncertainty.

Decision precedence: reuse established internal capability when adequate → adopt a vetted dependency/service when lifecycle value is favorable → extend through stable interfaces when necessary → build custom implementations for distinct business logic or demonstrably unsuitable alternatives. This is a heuristic, not a blanket prohibition of custom code.

Never implement authentication protocols, cryptographic primitives, card-data processing or other sensitive commodity mechanisms from scratch as a shortcut. Require specialist review for exceptions.
