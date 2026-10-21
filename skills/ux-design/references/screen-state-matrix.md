# Screen specification matrix

For each screen record: goal, persona/permissions, entry points, primary and secondary actions, data sources, components and design tokens, keyboard navigation, mobile behavior, localization needs, and states:

| State | What to define |
|---|---|
| Initial / loading | skeleton, progress, timeouts |
| Empty | explanation and next action |
| Success | feedback, navigation, updates |
| Validation error | field-specific messages and recovery |
| Permission denied | safe messaging and redirection |
| Network/offline | retry and data persistence policy |
| Conflict | concurrency resolution and user guidance |
| Degraded | partial UI behavior, accessibility and support |

Keep content design and visual assets traceable to approved PRD/flows. Wireframes do not substitute for user testing.
