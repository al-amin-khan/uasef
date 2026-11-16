---
name: ux-design
description: Create user flows, application navigation, screen behavior, wireframe briefs and design direction.
---

# UX and UI Design

## When to use
Create user flows, application navigation, screen behavior, visual mockups or prototypes, and design direction before production UI implementation for every new or materially changed interface unless the owner explicitly waives the preview.

## Preconditions
- Read the target repository's `AGENTS.md` and `.uasef/policies/`.
- Inspect the assigned task, known approved project artifacts, and actual repository state.
- Do not mistake a request for research for approval to implement or deploy.

## Method
1. Start from approved actors, requirements and tasks. Record design references by exact page/element and the quality to learn from (for example, clear product storytelling, strong typography, confident imagery or expressive motion), plus what not to copy. Create an original design; do not copy another brand's protected assets or distinctive page wholesale.
2. Capture project-specific design inputs: primary audience and task, brand personality, target market/language, available approved copy and imagery, supported browsers/devices, and performance/legal constraints. Ask only high-impact questions; label assumptions and use clearly marked placeholders when inputs are missing.
3. Inspect the actual repository before recommending UI tools. Read package manifests and lockfiles, existing design tokens, components, framework conventions and any configured design-tool integrations. Distinguish installed and reusable tools from candidates that would need approval and installation.
4. Evaluate suitable existing component, styling, icon and motion libraries before proposing custom implementations. Prefer the project's current system when it meets the need. Reuse its primitives and patterns; use custom CSS only for product-specific layout, tokens or details the existing system cannot express cleanly. Do not rebuild common controls from scratch without a concrete reason.
5. Map user journeys, navigation, screens, permissions, data needs and decision branches. Specify loading, empty, success, validation, permission-denied, offline, conflict and degraded states where relevant. Define responsive behavior, accessibility, localization, content, visual tokens and motion behavior.
6. Produce a reviewable mockup/prototype at a fidelity suited to the decision for each new or materially changed interface. A multi-screen feature should show the primary flow across its key screens at agreed desktop and mobile viewports, including important states and interactions. Prefer an interactive prototype in the project's existing stack with clearly mocked data when available; otherwise create annotated wireframes or use a configured design tool. Keep prototypes isolated from production behavior and label assumptions. A written brief alone is not a visual preview.
7. Evaluate the proposal with the UI review rubric in references/ui-review-rubric.md. Present the preview, trade-offs, open questions and library choices for owner review. Frontend implementation waits for owner review unless the owner explicitly waives it; record approval, waiver, or requested changes before handoff. Prototype approval is not user research or accessibility certification.

## Expected artifacts
`docs/02-design/user-flows.md`, `docs/02-design/screen-inventory.md`, and `docs/02-design/design-brief.md`, plus a reviewable prototype or annotated mockup for each new or materially changed interface unless explicitly waived. Record the preview location, how to open it, library inventory and rationale, motion plan, design decision/approval/waiver state, and persistent task/requirement IDs. If visual prototyping is unavailable, explain the specific tool or environment limitation and provide the best reviewable alternative; do not claim a visual mockup exists when only written descriptions exist.

## Preview standard

Save exported mockup images under docs/02-design/previews/<TASK-ID>/mockups/ and browser captures under docs/02-design/previews/<TASK-ID>/screenshots/. For a remote design tool, export review images into the project folder too and record its source link. Add a README.md in that task folder listing the screen, image filename, exact viewport or device, browser/OS for rendered captures, preview revision, mocked content/assets and owner-review status. Use synthetic/demo content; never place private user or production data in a preview.

Record the preview path and revision, how to open it, the explicit device/viewport matrix, the core interaction path, important states, what is mocked, asset/source status, library choices, motion plan, rubric findings and the owner's decision. A written brief is not a visual preview. If a visual prototype cannot be produced, report why and use an annotated fallback; do not claim it was rendered or reviewed. "Pixel-perfect" applies only to the approved reference at the named viewport, browser and OS. Check every visible element in that scope and log mismatches; never promise identical rendering on devices or browsers that were not specified and inspected.

## Deliverable format
1. Confirmed facts and supporting source/evidence (with dates where relevant).
2. Open questions and assumptions, each labeled as such.
3. Alternatives and recommendation with trade-offs.
4. Artifacts changed and requirement/task IDs.
5. Actual verification conducted, or precise reason not conducted.
6. Risks, approvals required, and next handoff.

## Non-negotiable guardrails
Never fabricate research, package compatibility, tests, deployment, approvals, or user validation. Request human review for sensitive/destructive/production changes. Prefer narrowly scoped action and record decisions in project artifacts.

## Additional guidance
Read [the task reference](references/screen-state-matrix.md) for screen details and [UI library discovery](references/ui-library-discovery.md) before choosing components, styling or motion tools.
