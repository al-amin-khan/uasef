# UI library and motion discovery

Use this checklist during UX/design planning and again before frontend implementation. The repository is the source of truth; a library mentioned in a prompt is not proof that the project has installed or configured it.

## Inspect before recommending

- Read the frontend package manifest and lockfile, framework/build configuration, and current component, styling, icon, and animation imports.
- Inspect existing design tokens, shared components, documented conventions, and any generated UI primitives. For source-owned component systems, inspect the actual checked-in components rather than assuming they match a remote catalog.
- Record what is already installed, what is already used, what is configured, and what would require a new dependency or external account.
- For a monorepo, inspect the package that owns the affected screen; do not assume a root dependency is available to every app.

## Choose the smallest suitable system

1. Reuse the existing UI/component system when it covers the interface and works with the project's framework and accessibility needs.
2. If no system exists or it cannot support a clear requirement, compare a small number of maintained, framework-compatible options using current official documentation. Consider accessibility behavior, theming, component coverage, bundle/runtime cost, licensing, maintenance signals and migration cost.
3. For utility CSS such as Tailwind CSS, use the project's installed version, configuration and conventions. Do not invent class names or assume setup from a package mention.
4. For component systems such as shadcn/ui, first inspect whether components are already generated and customized in the repository. Reuse and extend those local components; do not overwrite them with defaults.
5. Prefer the design system's components and tokens for routine controls. Add app-specific CSS for the product's distinctive composition and visual identity, not to recreate common controls the system already supplies.
6. Explain any proposed dependency addition and obtain the project's normal approval before changing manifests or installing packages. Keep the number of overlapping component or motion systems small.

## Motion and animation

- Inspect the project's existing animation libraries and patterns first. Reuse a compatible installed library for choreographed, scroll-linked, or multi-step motion when it materially helps the experience.
- For simple state transitions, use the existing design-system capability or a small CSS transition when that is the simplest reliable option. Do not add a large motion dependency for a hover fade.
- Describe each meaningful motion by trigger, purpose, duration/feel, reduced-motion alternative, and behavior on touch or low-powered devices. Avoid motion that delays navigation, blocks content, causes layout shifts, flashes, or runs continuously without user benefit.
- Respect `prefers-reduced-motion` and provide a usable static or reduced-motion experience. Preserve keyboard access, focus visibility, semantic HTML and screen-reader feedback regardless of animation.
- Treat examples from Apple, Nike or other brands as references for qualities, not instructions to reproduce protected assets, copy, layouts or signatures.

## Evidence in the design brief

Include a compact table with the tool/library, status (existing/configured/proposed), intended use, compatibility evidence, and decision. Link official documentation consulted. Mark unverified compatibility and open questions clearly. Do not claim a tool is available, current or tested without evidence.
