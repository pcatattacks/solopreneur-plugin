---
name: design-system
user-invocable: false
description: DaisyUI + Tailwind CDN design system spec. Preloaded into design-related agents and referenced by design skills.
---

# Design System

## Stack

Self-contained HTML mockups using DaisyUI + Tailwind via CDN (no build step, no setup):

```html
<link href="https://cdn.jsdelivr.net/npm/daisyui@5/daisyui.css" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
```

## Rules

- Use DaisyUI semantic classes for polished defaults: `btn`, `card`, `navbar`, `modal`, `badge`, `alert`, `table`, etc.
- Layer Tailwind utility classes on top for customization (spacing, colors, responsive breakpoints)
- Use realistic placeholder data (real names, prices, dates — not lorem ipsum)
- Add basic interactivity where it helps communicate the design (tab switches, modal open/close, dropdown toggles via inline JS)
- No external dependencies beyond DaisyUI + Tailwind CDN
- Structure each file as a complete HTML document: `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`
- Be openable via `file://` in any browser
