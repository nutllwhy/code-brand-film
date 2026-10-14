# Quality bar — the numbers a film has to clear

"Make it premium" is not an instruction an agent can check. These numbers are.
They come from comparing two accepted 15s films against a rejected one that was
built from the same skill and looked, in the user's word, "simple".

Run `scripts/film_audit.py film/index.html` before every render. It checks most
of this automatically; the rest is on the shot list.

## What "simple" looked like

The rejected film had: white background → words drifting → words gather into a
ring → a hand-drawn circle "logo" on dark navy → tagline → brand name. Its
`index.html` was 9 KB with 18 tweens. Every scene change was an opacity
crossfade. Its logo was a circle drawn in SVG rather than the brand's file. Its
fonts were `local()` system fonts, so the render fell back to whatever the
headless browser had. Its tagline was invented — it was not in the brief.

None of that is a bug. Every frame was clean, lint was green. It was simply
under-built, and the skill had not said how much is enough. Now it does.

## The numbers (15-second film; scale linearly for other lengths)

Measured with `scripts/film_audit.py` on the three real films:

| Measure | Rejected | Accepted A | Accepted B | **Floor** |
| --- | --- | --- | --- | --- |
| Tweens in the timeline (loops expanded; grain/rail/chapter tweens and yoyo breathing beyond 3 excluded) | 18 | 102 | 97 | **≥ 90** |
| Distinct entrance mechanics (see list below) | 1 | 9 | 12 | **≥ 8** |
| Non-crossfade act transitions | 0 | 2 | 4 | **≥ 2; plain crossfades ≤ 1** |
| Distinct eases | 6 | 17 | 19 | **≥ 8** |
| Camera moves (tweens on `#camN`) | 1 | 8 | 12 | **≥ 8** |
| Timed events per act (0–3 / 3–6 / 6–9.5 / 9.5–12.5 / 12.5–15) | 3/0/5/5/4 | 21/11/12/12/6 | 17/7/21/11/11 | **≥ 5 every act** |
| Page counter / progress bar / corner labels | — | — | — | **none** (reads as PPT) |
| Fonts as embedded files | 0 (system `local()`) | 2 | 4 | **every face on screen** |
| Real brand logo | — | inline official SVG path | official icon file | **the real, current file, checked** (`assets.md`) |
| Official images besides the logo | 0 | 3 | 0 (a gap, not a model) | **≥ 2**, one showing the product |
| Acts that depict the product actually working | 0 | 2 | 4 | **≥ 2** (shot list) |
| Copy lines traceable to the brief / product page | 0 | all | all | **all** (shot list) |
| A persistent element that crosses an act boundary | no | the logo hole | the input bar | **≥ 1** (shot list); a corner logo does not count and fails the layout gate |

The last three rows are checked through two files that `film_audit.py` requires
next to `film/`: `shot-list.md` (filled in before any HTML) and `copy.md` (every
on-screen line with its source — the audit fails on any visible text missing from
it). See `examples/office-agent/` for both.

## Footage-led films use different floors

When ≥ 2 official clips are on screen for ≥ 40% of the film, `film_audit.py`
switches to footage-led floors (≥ 60 tweens, ≥ 5 mechanics, ≥ 6 eases, ≥ 5
camera moves, no grain over studio-ground footage, stage = sampled ground,
a signature transition on ≥ 3 exits). An accepted footage film failed six of
the UI-film floors, and a rejected one passed all of them by decorating still
photos — details and rules in [footage-led.md](footage-led.md).

## Floors are not targets — the second failure

After the floors above were published, another agent built a film that cleared
every one of them *exactly*: 70 tweens, 8 mechanics. It still looked thin. How:

- Its count included the progress rail, the grain, the chapter number, and seven
  yoyo "breathing" tweens on headlines and shapes. Those are now excluded from
  the count (yoyos beyond the first three) — it scores 59.
- The idea was abstract (a drop of ink → lines → a box → the logo). Not one frame
  showed the product doing anything; it could have been an ad for a pen.
- The frame was nearly empty: content covered **3%** of the frame on median. A
  short line of type and one small shape, on a flat ground, for fifteen seconds.
- It skipped the shot list entirely, and its tagline was invented.

So there is now a second gate that cannot be padded, because it measures pixels.

## The rendered-frame gate

Placement is checked separately by `node scripts/layout_audit.mjs film/index.html`
(text hidden under boxes, text on text, clipped text, 48 px title safe, cards
parked half off-frame) — rules in [layout.md](layout.md).

Run `scripts/frame_audit.py renders/silent.mp4` after the first render. It
samples 10 frames a second and measures:

| Measure | Rejected films | Accepted films | **Floor** |
| --- | --- | --- | --- |
| Median coverage (share of frame that is not bare ground) | 0.007 – 0.056 | 0.069 – 0.43 | **≥ 0.065** |
| Median detail (share of pixels on a visible edge) | 0.008 – 0.063 | 0.069 – 0.10 | **≥ 0.065** |
| Median motion (share of frame changing per 0.1 s) | 0.000 – 0.020 | 0.03 – 0.05 | **≥ 0.025** |
| Thinnest act (median coverage of the emptiest act) | 0.000 – 0.019 | 0.05 – 0.09 | **≥ 0.04** |
| Longest near-still stretch | up to 6.2 s | ≤ 2.1 s | **≤ 2.5 s** |

If it fails, the fix is never "make the text bigger". It is: put the product on
screen (an interface, a document, a device, real data), add the background and
foreground depth layers, keep a persistent object alive across the cut.

## Compare with the reference before delivering

`examples/office-agent/reference-sheet.jpg` is the reference film's contact sheet
(2 fps, 30 frames). Make yours the same way
(`ffmpeg -i silent.mp4 -vf "fps=2,scale=384:-1,tile=6x5:padding=4:color=white" -frames:v 1 sheet.jpg`)
and look at the two side by side. Answer in writing, in the delivery notes:

1. In how many of my 30 frames can you tell what the product does? In how many of the reference's? (the reference shows it in roughly half; the hook and sign-off are allowed to be sparse)
2. How many of my frames are mostly empty ground, outside the sign-off?
3. Which of my acts is thinnest, and what would the reference put there?

If your answers are clearly worse than the reference, you are not done.

`index.html` size is a symptom, not a target, but a 15s film under ~20 KB is
almost certainly under-built.

## Entrance mechanics — count how many distinct ones you use

A film where everything fades up and slides 40px is one animation repeated.
Pick at least eight of these, and never use the same one for two consecutive
elements of the same kind:

1. **Line mask reveal** — text rises from behind an `overflow:hidden` line box (`yPercent: 105 → 0`)
2. **Character typing** — one span per character, `tl.set(opacity:1)` on its own micro-time
3. **Letter scatter** — each letter flies off with its own `x / y / rotation`
4. **Number count-up** — a proxy object tweened, `onUpdate` writes `Math.round(v)`
5. **Stroke draw** — SVG path `stroke-dashoffset: len → 0`
6. **3D card fly-in** — `rotationY / rotationX / z` from off-axis to near-flat, in a `perspective` parent
7. **Hard slam** — `scale: 2.4 → 1`, `power4.in`, 0.25s, followed by a 3-step camera shake
8. **Scale pop** — `scale: 0 → 1` with `back.out(2–3)`, for dots and badges
9. **Blur-in** — `filter: blur(10px) → 0` with a small x offset, for wordmarks
10. **Iris** — `clip-path: circle(0 → 1150px)` revealing a whole new layer
11. **Bar/fill growth** — `scaleY` or `scaleX` from 0 with a `transform-origin` on one edge, staggered
12. **Pulse ring** — a ring `scale 0.6 → 3.2, opacity 0.9 → 0`, for a "sent" or "clicked" moment
13. **Ticker roll** — a column of words translated by one row per beat
14. **Lateral push-in** — the whole camera layer enters from `x: 760` with `expo.out`
15. **3D hinge** — `rotationX: 0 → -90` on an element with `transform-origin: 50% 100%` (a lid closing, a card flipping)
16. **Yoyo breathe** — `repeat: 3, yoyo: true` on a dot or glow, to show "working"

Copyable code for each is in `recipes.md`.

## Transitions — never more than one plain crossfade

Opacity crossfades are the default for a reason: they never break. That is
exactly why a film built from them reads as a slideshow. Use at least three of:

- **Persistent hand-off** — an element from act N stays on screen and docks into
  a new position while act N+1 builds around it (the input bar that shrinks to
  the top-left). This is the strongest transition there is.
- **Zoom-through** — scale act N's camera to 3× while translating toward an
  object (a screen, a window); act N+1 starts at 0.88× and settles to 1.0.
- **Portal / logo dive** — a clip-path circle bound to a logo's scale; the
  logo grows past the frame and its interior becomes the next act.
- **Iris** — act N+1 is revealed by a growing `clip-path: circle()`, with a ring
  that scales out at the same rate to hide the clip edge.
- **Lateral whip** — act N exits `x: -700` with `power3.in`; act N+1 enters from
  `x: 760` with `expo.out`, overlapping by 0.25s so there is no empty frame.
- **Collapse to point** — every object in act N scales to 0.2 toward one spot
  where act N+1's key element appears.

## Product truth — the film has to show the product doing its job

The rejected film was a metaphor with nothing underneath it: words gather into a
circle. It could have been an ad for anything. Both accepted films show the
product's actual behaviour, stylised: a sentence typed into an input, a pipeline
of six steps lighting up, progress syncing across three devices, deliverables
arriving, memory cards connecting to a centre.

The metaphor (dive into the logo, slam the stamp) is the frame. The product's
real workflow, abstracted into clean UI, is the content inside it. You need both.

Before writing code, list the product's 3–5 concrete behaviours from the brief
and assign each to an act. If an act has no product behaviour, it must be the
hook or the lockup.

## Copy comes from the source, not from you

Every on-screen line should be traceable to the brief, the product page, or the
brand's own tagline. Write the source next to each line in the shot list. If the
brief has a mandatory selling line, it appears verbatim. If you need a line that
is not in any source, flag it to the user as invented rather than shipping it
silently.

## Real assets, real fonts

- Use the brand's current logo file for this exact product (SVG preferred; a
  raster favicon only at small size, flagged in delivery). Never redraw a logo,
  never take one from a logo-aggregator site. Bring back ≥ 2 official images as
  well. The search order, the five-point logo check and the `assets.md` manifest
  are in [assets.md](assets.md); `film_audit.py` fails without the manifest.
- Every face on screen must be a local `woff2` loaded via `@font-face` with a
  `url()`. `local()` and system font names are not allowed — the headless render
  browser does not have them and falls back silently. Use
  `scripts/fetch_cjk_fonts.sh` for Chinese.

## No slide furniture

An earlier version of this skill told you to add a chapter counter top-right
(`02 / 05`), a progress rail, and labels in all four corners. Drop all of it.
On review the user's verdict was that the counter "太像PPT了" — it is the single
most slide-like thing you can put on a frame. A film never tells the viewer
which scene it is on, and never shows how much is left.

Keep only what reads as material, not interface: a moving grain overlay, a
radial falloff, and at most one quiet brand mark in one corner.
`film_audit.py` fails on a counter or progress bar.
