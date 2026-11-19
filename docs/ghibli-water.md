# Ghibli-style water: notes for the world build

Saved from Deby's reference (a Blender node recipe). Our sea is a three.js shader (`makeWater` in
`src/worlds/terminal.js`), not a Blender render, so the recipe is reproduced in GLSL; each step below says how.

## The look
- Flat painted colour: 2 to 4 hard colour bands, no realistic reflections
- Wobbly cell-like highlight lines (Voronoi, distance to edge)
- A thin, clean white foam line where the water meets rocks or shore, and an optional second ring that pulses
- Small white sparkles that blink
- Slow, gentle movement
- Colours: deep blue `#1F7FA8`, mid teal `#3BB3C3`, light turquoise shallows `#7FE0D6`, highlights `#E8FBFF`

## Steps, and how they map to our shader
1. **Shore mask** ("shore" = 0 at rocks/shore, 1 in open water). Blender: Geometry Proximity to the terrain,
   mapped over 0.5 m. Ours: we already know the sea depth (`seaDepth`) and the islets; bake a shore-distance map, or
   use depth as the mask.
2. **Colour bands**: a CONSTANT colour ramp on the mask (0 turquoise, 0.25 teal, 0.6 deep blue). GLSL: `step()`s.
3. **Cell highlight lines**: 4D Voronoi distance-to-edge, scale 6 to 12, W = time/150 (stretched in Y for a river);
   threshold at about 0.04 for thin lines; distort the input with a little noise (Linear Light, 0.15) so they look
   hand-drawn; multiply by a noise mask (cut at 0.45) so they aren't everywhere.
4. **Shore foam**: mask + small noise (scale 15, x0.05) thresholded at 0.06 for a thin wobbly line; an optional second
   ring at 0.10 to 0.12 that pulses with sin(time)·0.02; a thin dark-blue inked line just under the foam.
5. **Sparkles**: Voronoi F1 (scale 40, W = time/40) thresholded at 0.03, times a slow noise cut at 0.6, so tiny dots
   appear and disappear.
6. **Combine**: max(lines, foam, sparkles) mixes base colour to `#E8FBFF`; output unlit (emission) so the colours stay
   exactly as picked.
7. **Optional toon light**: shadows of trees and rocks fall on the water as hard two-step bands (our toon ramp).
8. **Optional see-through shallows**: near the shore, blend to transparent tinted `#9FF0E6` so the painted pebbles and
   rocks show underneath (this is what makes the new rail bed read under water).

## Finishing
- Floating leaves and lily pads: flat two-tone toon planes
- Sky: light blue to white gradient
- Keep it slow; if busy, slow the time divisors (150 to 300)
- Crisp lines; a little bloom on the highlights at most
