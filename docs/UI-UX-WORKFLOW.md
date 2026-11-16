# UI/UX preview and library-first frontend workflow

UASEF can guide an AI coding tool through a visual design review before production UI implementation. It provides portable UX/frontend role instructions, library-discovery guidance, task sequencing, and project-local workflow files. The configured AI tool creates the mockup or prototype; UASEF does not itself provide a Figma account, launch a design application, or guarantee that every model can render a visual preview.

**Default:** create and review a visual preview before implementing every new screen or materially changed interface. The owner can explicitly waive this for a task; trivial fixes with no meaningful visual or interaction change can skip it with a short reason.

## Set up a project

For a new project, `uasef init` installs the UX skill, role contracts, and Markdown workflow guides under `.agents/skills/ux-design/` and `.uasef/workflows/`. For an existing UASEF project, install the updated framework and run:

```powershell
uasef upgrade --project .
```

Upgrade adds missing workflow files under `.uasef/workflows/` and does not overwrite existing project-specific versions. Existing customized role contracts are also preserved; compare and merge new frontend/UX role guidance if needed. Check that the coding agent you use can read the project's `.agents/skills/` directory and create the kind of preview you want.

No separate design service is required. A design-capable coding agent can create an annotated wireframe or a temporary clickable prototype in the existing frontend stack using mock data. If you prefer Figma or another tool, configure that tool and give the selected agent access through its supported integration. UASEF does not configure credentials or integrations for you.

## Tell UASEF what you want to review

Include the product goal, target users, important journeys, required pages, content/assets, existing brand rules, and examples of visual qualities you like. For references such as Apple or Nike, say what qualities you mean—such as editorial storytelling, bold product imagery, typography, strong contrast, or motion—and ask for an original design. State whether you want UX first, frontend exploration first, or a complete clickable prototype before implementation.

If your request is broad, the UX role should ask only high-impact questions and mark remaining assumptions. It should not invent product features, copy another site's distinctive layout/assets, or claim that a preview was reviewed when it was not.

## Discover and reuse the actual UI stack

Before design or coding decisions, agents inspect the affected app's package manifest and lockfile, framework configuration, local components, design tokens and existing animation patterns. The report separates tools already installed/configured from tools that are only candidates.

Agents should reuse a suitable project system—for example, the project's configured Tailwind utilities, checked-in shadcn/ui components, or current motion library. They should extend customized local components instead of overwriting them with generator defaults. Custom CSS remains appropriate for product-specific tokens, layouts and details, while common controls should come from the existing component system when suitable.

If an existing tool cannot meet a documented need, the UX/frontend roles compare a small number of compatible options using current official documentation and explain accessibility, maintenance, performance, framework compatibility and migration trade-offs. New dependencies or paid/external tools follow the project's normal approval process. Avoid adding several libraries that solve the same problem.

Use an animation library already present when the design calls for sequenced, scroll-linked or coordinated motion. For a simple transition, use the existing design-system feature or a small CSS transition. Every meaningful animation needs a purpose and a reduced-motion experience; it should not block content or essential actions, harm keyboard access, or make the page slow or disorienting.

## Create and review the preview

The UX task should produce:

- user flows, route/navigation map, screen inventory and relevant screen states;
- visual direction, typography/color/token guidance, responsive behavior, accessibility expectations and motion notes;
- an inventory of existing UI/motion tools and a reasoned choice for each;
- a clickable prototype or annotated visual mockup, with a precise path and instructions to open it;
- explicit notes for mocked data, unfinished states, assumptions and questions for the owner.

The project owner reviews the actual preview and gives corrections before frontend implementation begins, unless the owner explicitly waives the preview. UASEF's task approval records a workflow decision; it does not prove usability or substitute for user testing. If the chosen agent cannot make a visual preview, it must say so and provide an annotated wireframe or another reviewable alternative rather than claiming a prototype exists.

### Minimum preview evidence

Maintain a project-specific device/browser/OS matrix based on intended users and available usage data. If no data exists, have the UX role propose a small representative matrix and get it approved. Include each supported breakpoint plus representative physical devices; do not interpret "each device" as every device that exists.

For a new page or material redesign, the preview must show the page purpose and primary action, approved or clearly marked sample content, the key screens in the main flow, every agreed viewport/device, and important interactive/error/empty states. Export mockup images under docs/02-design/previews/<TASK-ID>/mockups/ and implementation screenshots under docs/02-design/previews/<TASK-ID>/screenshots/. If the design is made in Figma or another remote tool, export review images to this folder too and record the source link. Include a README.md manifest in that task folder with screen, exact device/viewport dimensions, browser/OS, revision, image filename, mocked data/assets and review status. Use synthetic/demo content only. For a small visual change, show the affected component in context at each target viewport.

For implementation review, capture each screen at the same dimensions/browser/OS as the approved reference. Compare all visible elements—type, spacing, alignment, colors, borders, icons, imagery, states and motion—and save before/after images or an overlay when the browser tooling supports it. Check both sides of each responsive breakpoint. Record every mismatch and its reason before calling the result pixel-perfect for that target. This process gives evidence for named targets; it cannot guarantee identical rendering on unspecified devices or operating systems.

Define the supported device/browser/OS matrix per project from the intended audience and available usage data. Do not interpret "each device" as every device that exists. For each named target, capture the approved mockup and implemented browser view at matching dimensions and compare every visible element, including typography, spacing, alignment, color, borders, images, controls and motion states. Record differences and their causes; browser/OS font rendering can differ, so do not claim universal pixel identity beyond tested targets.

Use the UI proposal review rubric at ../skills/ux-design/references/ui-review-rubric.md before approval. A screenshot helps assess composition but cannot demonstrate navigation or state transitions; use a clickable prototype for those. Record blocking feedback, revise the preview, and have the owner review the revised version.

## Project details that improve the result

No single style input is required for UASEF setup. For each product, the UX role should discover or ask about the primary audience and task, desired brand personality, reference sites and what you like/dislike about them, supported languages and markets, available product images/copy, target devices/browsers, and any legal or business constraints. If you do not know, the agent should label assumptions and show a small number of meaningfully different directions for your review.

The project should name its accessibility target. For web work, WCAG 2.2 Level AA is a useful default; W3C defines Level AA as meeting all Level A and AA success criteria, and advises using the current version. A target is not proof of conformance, so agents must report the actual checks and gaps. See the [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/wcag/).

## Sequence with UASEF tasks

Create a UX task and require owner approval for its reviewed design. Backend/API work can proceed independently when it does not depend on unresolved UX choices. Frontend implementation should depend on the reviewed design and the API contract it will consume. If you want frontend exploration before the backend is ready, use a documented provisional contract and mock data, then reconcile it before integration.

Example after the feature documents exist:

```powershell
uasef task add UX-001 --title "Create reviewed UI prototype and design brief" --role ux-designer --skill ux-design --context docs/01-product/prd.md --context docs/02-design/user-flows.md --acceptance "Owner reviews mockup images in docs/02-design/previews/UX-001/mockups; device matrix, libraries, motion, states, assumptions and feedback are recorded" --approval-required
uasef task add API-001 --title "Agree on feature API contract" --role backend-engineer --skill feature-implementation --context specs/features/example/design.md --acceptance "Request and response shapes, permissions, errors and examples are reviewed"
uasef task add UI-001 --title "Implement approved feature interface" --role frontend-engineer --skill feature-implementation --design-task UX-001 --depends API-001 --context docs/02-design/design-brief.md --context specs/features/example/design.md --acceptance "Approved screens and states are implemented, responsive, accessible and verified in a browser"
uasef task tree
```

Adjust context paths to real project files. New frontend-engineer tasks must provide --design-task UX-ID, which must be an approval-gated ux-designer task and is automatically added as a dependency, or use --design-waiver with a specific 15-500 character reason. The runner blocks frontend execution until the UX task is verified and approved. For frontend-first exploration, use mock data and still review the UX preview before production implementation; a trivial fix can use a documented waiver. If the UX and frontend work use different models, configure runner profiles and dispatch them separately. Task creation does not automatically launch agents, and an agent's successful exit does not equal review or approval.

To run the sequence with an enabled profile, inspect the candidate and prompt before opting in to execution:

```powershell
uasef route --task UX-001
uasef dispatch UX-001 --profile opencode
# Review the task prompt, profile command and permissions before execution.
uasef dispatch UX-001 --profile opencode --execute
uasef task show UX-001
```

Review the preview itself and the task evidence. Only after it is independently reviewed and the owner accepts the direction should the approval-gated UX task be approved; the frontend task then becomes eligible because its design-task dependency is complete. UASEF records local actor names and does not authenticate the owner's identity, so this gate prevents accidental dispatch but is not a security boundary. Use the same profile or configure another model for each role. The actual agent CLI's ability to create and render a preview depends on its tools and permissions.

## Verify the implemented experience

The frontend/QA handoff records the actual browser checks: representative narrow and wide viewports, important user journeys, loading/empty/error/permission states, keyboard/focus behavior, reduced-motion behavior, console/build output, and automated UI tests that exist for the project. Include screenshots or a preview URL/path where the environment permits. Distinguish checks that ran from ones that were not available; a source-code-only inspection is not a rendered UI review.
