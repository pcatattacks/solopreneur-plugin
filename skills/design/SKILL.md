---
name: design
description: Create design direction, wireframe descriptions, and UI/UX recommendations for a feature or product. Use when the user needs visual direction, component specifications, or user flow diagrams.
---

# Design Direction: $ARGUMENTS

You are creating design direction for the CEO. If `$ARGUMENTS` is a file path, read that file for context (likely a spec). Otherwise, treat it as the feature description.

## Process

1. Delegate to the `@designer` subagent to produce:
   - **User Flow**: ASCII diagram showing the full user journey (use box-drawing characters)
   - **Key Screens**: For each screen, describe the layout, key elements, and user actions
   - **Component List**: All UI components needed (buttons, forms, cards, modals, etc.)
   - **Visual Direction**: Color palette, typography, spacing recommendations
   - **Accessibility**: Screen reader considerations, contrast ratios, keyboard navigation

2. If the Figma MCP server is available, check for existing design tokens or component libraries to reference.

3. For each key screen, include a simple ASCII wireframe:
   ```
   +---------------------------+
   |  Logo    [Nav] [Nav] [CTA]|
   +---------------------------+
   |                           |
   |    Hero Headline          |
   |    Subtext here           |
   |    [Primary Button]       |
   |                           |
   +---------------------------+
   ```

4. Save to `.solopreneur/designs/{date}-{slug}.md` (create the directory if needed).

5. End with the next step prompt:
   ```
   -> Next: Build this with a Cursor-ready plan:
      /solopreneur:build .solopreneur/designs/{filename}
   ```
