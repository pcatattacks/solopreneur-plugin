---
name: design
description: Create design direction, HTML mockups, and UI/UX recommendations for a feature or product. Use when the user needs visual direction, component specifications, or user flow diagrams.
---

# Design Direction: $ARGUMENTS

You are creating design direction for the CEO. If `$ARGUMENTS` is a file path, read that file for context (likely a spec). If it's a directory, read files inside it for context. Otherwise, treat it as the feature description.

## Process

### Step 1: Design Brief

Delegate to the `@designer` subagent to produce a `design-brief.md` containing:

- **User Flow**: ASCII diagram showing the full user journey (use box-drawing characters). Example:
  ```
  [Landing Page] → [Sign Up] → [Onboarding] → [Dashboard]
                         ↓
                   [Login] ───→ [Dashboard]
  ```
- **Screen Inventory**: List every key screen with a one-line description of what the user does there
- **Shared Visual Direction**: Color palette (hex values), typography (font families, sizes), spacing scale
- **Component Patterns**: Buttons, cards, forms, navigation — the shared building blocks across screens
- **Accessibility**: Screen reader flow, contrast requirements, keyboard navigation paths

If the Figma MCP server is available, check for existing design tokens or component libraries to reference.

Save to `.solopreneur/designs/{date}-{slug}/design-brief.md` (create the directory).

### Step 2: HTML Screen Mockups

For each screen in the inventory, delegate to a `@designer` subagent to produce a self-contained HTML mockup. Each subagent receives:
- The design brief (for shared visual direction and component patterns)
- The specific screen name and description from the inventory

Each HTML file must:
- Include DaisyUI CSS and Tailwind via CDN:
  ```html
  <link href="https://cdn.jsdelivr.net/npm/daisyui@5/daisyui.css" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  ```
- Use DaisyUI semantic classes for polished defaults (`btn`, `card`, `navbar`, `modal`, `table`, etc.)
- Use realistic placeholder data (real names, prices, dates — not lorem ipsum)
- Include basic interactivity where helpful (tab switches, modals, dropdowns via inline JS)
- Have no external dependencies beyond DaisyUI + Tailwind CDN
- Be openable via `file://` in any browser

Save each screen to `.solopreneur/designs/{date}-{slug}/{screen-name}.html`.

**Parallelization**: Launch one `@designer` subagent per screen in parallel. Each subagent only needs the design brief plus its screen-specific requirements.

### Step 3: Present to the CEO

Tell the user:
```
Your design mockups are ready! Open them in your browser to see the designs:

  open .solopreneur/designs/{date}-{slug}/

Files:
  - design-brief.md    — User flows, visual direction, component patterns
  - {screen-1}.html    — [Screen 1 description]
  - {screen-2}.html    — [Screen 2 description]
  - ...

Take a look and let me know what you'd like to change. I can iterate on any individual screen.
```

If the Chrome DevTools MCP is available, offer: "I can also open these in your browser and take screenshots if you'd like to review them together here."

### Step 4: Next step

End with the next step prompt:
```
-> Next: Build this with a Cursor-ready plan:
   /solopreneur:build .solopreneur/designs/{date}-{slug}
```
