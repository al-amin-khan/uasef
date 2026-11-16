# UI proposal review rubric

Use this rubric on a design preview before frontend implementation. Judge the experience against approved product requirements and target users, not personal taste alone. Record each item as **ready**, **revise**, or **not applicable**, with a preview location or rationale. A polished screenshot does not prove usability, accessibility or technical quality.

| Area | Review questions | Evidence to record |
| --- | --- | --- |
| User and task clarity | Is the audience clear? Can the intended user understand the page purpose and next action? Does the primary flow solve the stated need without invented features? | Requirement IDs, flow and unresolved assumptions |
| Visual hierarchy | Are the most important content and actions easy to find? Do typography, spacing, color, imagery and composition support the intended brand personality? Is the result distinctive rather than an unmodified library demo? | Annotated screen or prototype location |
| Content and assets | Is realistic copy present? Are placeholders clearly marked? Are image, font and icon sources approved, original, licensed, or otherwise authorized for the project? | Asset/source list and missing content |
| Consistency and components | Does the preview reuse the project's existing tokens and components appropriately? Are repeated patterns consistent? Are custom styles limited to genuine product needs? | Existing library/component inventory and justified exceptions |
| Flow and states | Are navigation, forms and feedback clear? Are relevant loading, empty, success, validation, permission, offline and failure states shown? Can users recover from errors? | Click path and state inventory |
| Responsive and visual fidelity | Is every agreed device/browser/OS and exact viewport represented? Do content, navigation, controls and imagery reflow without clipping or loss of function? For implementation review, does each visible element match the approved image at that exact viewport? | Device matrix, exact viewport sizes, reference and rendered screenshots, mismatch notes |
| Accessibility | Is the project target recorded? Check semantic structure, keyboard path, visible focus, contrast, labels/errors, touch use, reduced motion and available assistive-technology checks. Report untested criteria; do not infer conformance from the mockup. | Checklist results and gaps; distinguish design inspection from implementation tests |
| Motion | Does each animation explain or support an action/story beat? Does it preserve control, reading and navigation? Is reduced motion usable? Are timing and mobile behavior specified? | Trigger, purpose, reduced-motion alternative and open questions |
| Performance and trust | Do images, video and motion fit the product and stated performance needs? Are pricing, security, privacy and other trust claims substantiated in content? | Known budgets/constraints, optimization assumptions and claims needing evidence |
| Owner review | Has the owner seen the actual preview and recorded changes or approval? Is the approved revision identifiable? | Preview version/path, decision, date/actor and follow-up |

## Decision

- **Ready for implementation:** critical user flow, visual direction, library choices, content/asset assumptions, responsive views and owner review are recorded; no blocking issue remains.
- **Revise:** list blocking changes as concrete items, update the preview, and ask the owner to review the revised version.
- **Waived:** record the owner's explicit waiver and why; for trivial UI changes, record why the change has no meaningful visual/interaction effect. UASEF task approval names are local assertions and are not authenticated identity.

For high-impact or unfamiliar workflows, recommend formative review with representative users before release. Owner approval of a prototype is not user validation.
