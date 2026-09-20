# OaSIs Tattoo Studio v04

A second ground-up UI rebuild after studying current dashboard / responsive-layout tutorials and contemporary platform design guidance.

## Design direction

v04 is intentionally **not a dashboard**.

The primary experience is an image-first studio:

- central art wall
- three distinct directions visible at once
- selected direction larger and centered
- minimal floating prompt dock
- contextual inspector instead of permanent configuration forms
- progressive disclosure for references, placement, stencil, export, and history
- responsive layout that changes structure on small screens rather than merely shrinking

## Workflow

1. **Create** — prompt, style, placement, three directions
2. **Refine** — five useful visual forces in the contextual inspector
3. **Place** — local body photo, scale, rotation, opacity, blend
4. **Stencil** — clean linework, detail, line strength, print/SVG
5. **Deliver** — concept SVG/PNG, project JSON, artist brief
6. **History** — local browser saves

## Privacy

No automatic network calls. Reference images and body photos remain local to the browser.

## Generator

The current renderer is deterministic procedural SVG. The interface is intentionally structured so a future image-generation adapter can replace or augment the renderer without redesigning the product.

Open `OaSIs_Tattoo_Studio_v04.html` directly.