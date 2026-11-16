# Workflow: UI/UX preview before frontend implementation

**Trigger:** Any new screen or materially changed interface. A visual preview and owner review are the default before frontend implementation. The owner can explicitly waive the preview; trivial fixes with no meaningful visual or interaction change may skip it with a short reason.

## Purpose

Give the owner a concrete preview to evaluate before production frontend implementation. UASEF supplies role contracts, task sequencing and review guidance. The selected coding/design tool creates the mockup or prototype; UASEF does not itself launch a design application or guarantee a rendered preview.

## Sequence

1. **Scope the experience.** Product/UX roles read approved requirements, identify target users, key journeys, screens, content, data and permissions, and record unresolved decisions. Ask whether the owner prefers UX first, frontend first, or parallel exploration. If the backend contract is missing, document a provisional interface contract and mock data; do not invent production behavior.
2. **Inventory the project design stack.** Follow `.agents/skills/ux-design/references/ui-library-discovery.md`. Inspect manifests, lockfiles, existing components/tokens and configured integrations. Reuse an appropriate existing UI, styling, icon and animation system. Present new dependency/tool choices with current official evidence and trade-offs before installation.
3. **Create the design proposal.** UX documents flows, screen inventory, states, responsive behavior, accessibility, visual direction and motion. Use supplied brand references as inspiration for qualities; create an original interface. Include a clickable prototype or annotated visual mockup by default for new or materially changed screens. Prefer the existing app stack with mocked data when it can produce a fast, isolated preview. Otherwise use an available configured design tool or clearly mark the limitation and provide an annotated alternative.
4. **Review before implementation.** Show the owner how to open the preview and what is mocked or incomplete. Record accepted/rejected choices, requested changes and the design decision in project docs/memory. Do not treat an unreviewed draft as approved design.
5. **Implement the approved direction.** Frontend engineer follows the accepted design and library decisions, reuses existing primitives, and records deviations with reasons. Backend-first, frontend-first, or vertical-slice order is chosen from user preference and actual dependencies. A mocked contract is reconciled with the backend contract before integration.
6. **Verify the rendered experience.** Inspect real browser output at representative narrow and wide viewports; verify primary journeys, loading/error/empty/permission states, keyboard/focus behavior, reduced motion, console/build output, and applicable automated UI tests. Record exact evidence. A source-only review is not visual verification.

## Human review points

- Review the screen flow, visual direction and major library choices before implementation. Frontend implementation waits for this review unless the owner explicitly waives it.
- Review the browser-rendered result after implementation and before release.
- Get normal project approval before adding dependencies, buying assets/tools, or making production changes.

## Task handoff

For newly created frontend-engineer execution tasks, use --design-task UX-ID to require an existing ux-designer task created with --approval-required. UASEF automatically adds that task as a dependency and blocks dispatch until it is independently verified and owner-approved. For a trivial visual fix or explicit owner waiver, use --design-waiver with a specific reason. This execution gate prevents accidental bypass; local actor names are not authenticated. Existing tasks are preserved and are not retrofitted.

Save exported design mockup images in docs/02-design/previews/<TASK-ID>/mockups/ and implementation screenshots in docs/02-design/previews/<TASK-ID>/screenshots/. Include a README.md manifest listing page/screen, exact device or viewport dimensions, browser/OS for rendered screenshots, preview revision, asset/data assumptions and owner-review status. Do not label a screenshot pixel-perfect without comparing it against the approved reference at the same viewport and recording remaining differences.

Use an explicit UX task with role `ux-designer` and skill `ux-design`, then a frontend task with role `frontend-engineer` and an implementation/verification skill. Make frontend implementation depend on the reviewed design artifact when work is sequential. Configure separate runner profiles if separate models/tools should execute these tasks. Task creation and dispatch are explicit; UASEF does not autonomously spawn agents or guarantee that profiles can produce visual files.

For an independent exploration, UX and backend contract discovery may proceed in parallel. Keep frontend implementation blocked on the selected API contract and design review where those are necessary to avoid rework.

## Exit condition

The owner has reviewed a concrete mockup/prototype or accepted the documented limitation; the approved design decisions and tool choices are traceable; and frontend verification records rendered evidence and remaining gaps.

## Failure and recovery

If the project cannot render a prototype or no design tool is configured, preserve the design work, explain what is needed to preview it, and offer an annotated-wireframe fallback. Never report a prototype as rendered or user-approved unless that outcome was observed.
