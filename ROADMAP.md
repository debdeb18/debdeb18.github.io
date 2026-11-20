# Roadmap

Every area follows the same loop: concept render, feedback, split into pieces, build in the website, **extra details pass**, feedback.

## 0. Foundations
- [x] Walkable website with four worlds, panels, cutscene, mobile controls
- [x] Text content from the resume
- [x] Blender pipeline (script, `.blend`, render, `.glb`)
- [x] Style: A's shapes, slightly crooked; D's light for dusk and night
- [x] Load Blender models (`.glb`) into the website (optimized: 18 MB to 3 MB)
- [x] First painted pass: toon shading, rim light, brush-stroke filter (desktop)
- [x] Hand-painted textures, step 1: ground (grass, sand, concrete, gravel, wood decking, stone)
- [x] Hand-painted textures, step 2: buildings (plaster, roof tiles, painted timber)
- [x] Hand-painted textures, step 3: trees as painted leaf clusters that flutter in the wind; painted bark
- [x] Bushes, planter shrubs and potted plants as leaf clusters
- [x] Painted cumulus clouds (towers of puffs, flat cream and lavender shading)
- [x] 3D grass on the islets that sways in the wind and bends away as you walk through
- [x] Walkable islets behind the station: plank ramp from the deck, wading between islets with ripples
- [x] Camera pulls in instead of passing through the station building and canopy
- [x] Light shafts through the trees (follow the sun, fade with cloud and at night)

## 1. Terminal: a station above the water
Design in Blender
- [x] Chair, suitcase, station sign
- [x] Train, leafy tree, pine
- [x] Whole-station concept, day and dusk
- [x] Water that is clear in the shallows and darker with depth; rails just under the surface; train wake
- [x] Islet details: footbridge, shrine, jetty, swing, hammock, picnic, lantern posts, reeds, rocks, flowers
- [x] Split into pieces: 47 models and a layout file in `models/terminal/`
- [x] Train: judpro's Sketchfab model in maroon and golden cream
- [x] Mirror water that stirs where things pass; ballast-bank railway; poles and wires removed; trees reshaped
- [ ] Review, then fixes
- [x] Rowing boat with a proper hull: varnished wood, clinker planks, oars resting on the seats (`blender/assets/boat.py`, style A)

Porch v2 (on the ruin), assets in `blender/assets/halt.py`, `heron.py`, `fish.py`
- [x] Ruin pier, tower with arched windows, tall wall, front and back stairs from the porch's courses, seats, posters on the wall, crossing signal in the water, deck hooked over the back edge
- [x] Mooring post: twin posts with a rope figure-of-eight (option E)
- [ ] Revisit the stone blocks at the end of the phase
- [ ] Put the porch into the world (simplify the model on export)
- [ ] New rail (`blender/assets/rail.py`) replaces the v1 causeway
- [ ] Ghibli-style water after `docs/ghibli-water.md` (bands, cell lines, thin shore foam, sparkles, see-through shallows)
- [ ] The cat asleep in the tower nook: design still to settle (`cat_sleep.py` is the work in progress; the nook is empty for now)
- [ ] Hide the cat when it rains or the weather is bad
- [x] Low-poly heron standing (`heron.py`) and flying (`heron_flying.py`, wings flap)
- [ ] Heron on the rocks in the shallows by the tower (the 'heron_spot' empty), only when sunny; swap to the flying model to take off: flies off when a train passes, comes back while it stays sunny
- [ ] Low-poly orange fish (`fish.py`) by the back stairs; in rain only one or two, under the deck

Sea (v2)
- [x] Sea floor chosen (flat strip under the rail, gentle uneven floor both sides)
- [x] Water chosen: the Ghibli painted water, with living foam and tides by the moon
- [ ] Sea floor details: more shaped slopes, moss, sea grass, rocks and the like

Build in the website
- [x] Assemble the station, with walkable areas and collisions
- [x] Trilingual name on the sign (어딘가 / Somewhere / Entah di mana)
- [x] Animated water: ripples, reflections, depth colour
- [x] Train with splash and wake that scale with its speed; a train passes every 35-55 s
- [x] Clouds drifting with the wind; trees swaying; gulls
- [x] Sun, sky and shadows following the visitor's real local time (`?time=HH` to try other hours)
- [x] The dimension-crack cutscene in the new station
- [x] Hotspots: chair, timetable, vending machine, station sign, cat
- [ ] Extra details pass

## 2. Character (take it slow, aim high; easiest first)
References in `docs/refs/character/`: a soft blob with headphones (simple, matte, very rounded), a block-headed guy
(one bold shape, few details), a chibi girl in a coat (big head, soft rounded forms, big glossy eyes, chunky scarf and
boots). What they share: smooth, rounded, toy-like shapes, soft matte materials, gentle light, small dot or big
expressive eyes, few but well-placed details. The red-cardigan girl is dropped. Start with the easiest, the soft blob,
and work up; each step shown for approval before the next.
- [ ] The soft blob: shape, dot eyes, headphones; soft matte look (sketch, then Blender)
- [ ] Move and animate it: idle bob, walk (a waddle or hop), sit, look around
- [ ] Replace the current code-built character with it
- [ ] Later, if wanted: the block-headed guy, then the chibi girl in the coat
- [ ] Extra details pass (expressions, small gestures, accessories)

## 3. Home in space
- [ ] Concept render
- [ ] Pieces: the studio, dome, furniture, telescope, easel, shelves, photo wall
- [ ] Build in the website; photos and "about me" content
- [ ] Extra details pass

## 4. Office
- [ ] Concept render
- [ ] Pieces: building, dev room, archive, meeting room, pantry, arcade machine
- [ ] Build in the website; project content per room
- [ ] Extra details pass

## 5. Night market
- [ ] Concept render
- [ ] Pieces: stalls, food truck, goods shop, collab hub, lanterns, stall-keepers
- [ ] Build in the website; hobbies, side projects, writing
- [ ] Extra details pass

## 6. Content (needs Deby)
- [ ] Pictures: self, travel, hobbies, art
- [ ] Answers: games, art, food, collections, writing
- [ ] Check the wording of work and "how I work"
- [ ] Decide whether the email goes on the site

## 7. Polish and launch
- [ ] Sound and music
- [ ] Loading screen
- [ ] Speed on phones and older laptops
- [ ] Test on real devices
- [x] Automatic test and publish on every push to `main` (GitHub Actions)
- [x] Switch GitHub Pages to the `main` workflow so the new site goes live
