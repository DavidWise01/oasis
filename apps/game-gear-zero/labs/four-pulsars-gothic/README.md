# FOUR PULSARS — Gothic Ice-Cube Laser

Standalone, offline, zero-dependency HTML/Canvas2D viewer with an animated ASCII display.

**Run:** Open `index.html` in Chrome/Edge/Firefox (no server needed).

Four fictional space ice-cube pulsars: green (Tb), red (Eu), blue (Nd), purple (Er). Each node has a faceted cube, glowing orbital rings, rotating sweep beam, and packets converging into a recursive four-dot box `[.|.|.|.|]`. The center displays a glowing symbolic laser during FIRE.

## Controls

- PLAY / PAUSE: run continuous pulse cycles.
- STEP: advance one-sixteenth of a cycle, paused.
- PULSE: jump to FIRE.
- RESET: return to t=0 and pause.
- Four emitter buttons: toggle green/red/blue/purple, represented as a four-bit mask (2^4=16 combinations).
- SPEED and GLOW sliders: adjust animation time and effects.
- GRAPHICS / ASCII: switch representations of the same simulation state.
- PNG / TXT: export Canvas or text frame.
- Keyboard: space, right arrow, P, A, R.

## What it is (and isn't)

This is a **procedural sci-fi art simulation** of four fictional crystal pulsars. Real pulsars are rotating neutron stars; the geometric ice cubes are not actual pulsars and the beams do not model real laser coherence, rare-earth emission wavelengths, or physical RGB mixing.

The symbolic `. | . | . | . |` focus box preserves the user-defined four-dot grammar. Four independent emitters each have an on/off state, hence 16 masks; that is distinct from the earlier three-bit, eight-state RGB diffusion model.

The entire simulator is in `index.html`. No imports or downloaded assets, no frameworks, no user data sent anywhere.
