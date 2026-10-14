# Footage-led films — when the brand already ships its own product motion

> Read this whenever the product page has product animation or film (most
> hardware, most large consumer brands). `harvest_page_images.py --video` tells
> you in one run. `film_audit.py` switches to footage-led floors by itself when
> ≥ 2 `<video>` elements are on screen for ≥ 40% of the runtime.

When the brand has already filmed its product, the job changes. You are no
longer building the picture in code. You are **editing the brand's own motion
around one idea**. Code supplies the cut, the camera, the type and the one
recurring gesture. It does not supply the content, and it must not decorate
the content.

## The comparison this file comes from

Same product (a foldable phone from a large consumer-electronics brand), same
night, same skill version. One film was accepted ("much better"), the other was
built by a different agent that followed every step of this skill: shot list,
copy sheet, assets manifest, all three gates at `0 failed`, 109 tweens, 10
mechanics, 22 eases. It still lost, clearly, and the gates could not see why.

| | Accepted | Rejected (passed every gate) |
| --- | --- | --- |
| Official motion | 7 product animations, on screen ~63% of the runtime; every act after the hook is footage | 3 clips (~59%); the middle 6 s were **two still photos** with code motion on top |
| Stage vs asset ground | stage set to the clips' sampled ground (`#FDFDFD`); no texture layer; the clips have no visible edges | white stage + 4.7% multiply grain + falloff → measured ground `rgb(241,244,243)`; first act on `#e7e7e9` over a `#e3e3e5` clip; edges and tint show |
| Transitions | **one move**, from the product's shape: the frame folds shut on a centre seam and the next shot opens out of that seam — used on every act change | shutters, iris, zoom-through, split wipe, lateral whip, line mask… a sampler; no move is "this product's move" |
| Product geometry | every product shot placed so its hinge lands on the seam; act 2 → 3 is a hinge-to-hinge match cut | device parked left (x 100–1130) in one act, centred in the next, held in a hand in the next |
| Decoration over the product | none; the only drawn line is the seam | focus corners, capture rings, a focus dot crossing panes, hairlines, specular arcs — 19 drawn UI marks. Vision review: "UI design demonstration", "corner brackets … indicate this is a screenshot of a working file" |
| Copy | the brand's own lines from its site **in the audience's language**; one claim per shot, numbers when the page has them (outer screen size flipping to the inner screen size) | the site's English lines for a Chinese-speaking audience; two feature names used as act headlines |
| Rhythm | uneven on purpose: a five-pose burst at 0.3 s per pose, a 3 s hero | five even 3 s acts, each "one feature + one title" |

Run on the old floors, **the accepted film failed six craft checks** (79 tweens,
6 mechanics, 0 recognised transitions, 7 camera moves, no grain). The old floors
were written for films whose picture is drawn in code; applied to a footage
film they reward exactly what made the rejected one busy. They are now
footage-aware, and three new checks catch the rejected film: ground mismatch,
texture over studio-ground footage, and a missing signature transition.

## The rules

1. **Harvest motion first.** `harvest_page_images.py <page> --video` pulls
   direct `.mp4` links and the `anim/<name>/` directories big brand sites load
   by script, largest variant first, plus a contact sheet. Also fetch the
   brand's page in the audience's language — it can carry different clips and
   it is where the copy comes from.
2. **Footage carries acts 2–4.** A still photo is allowed as a burst (≤ 0.5 s
   per image, ideally a montage of poses on one anchor) or as the final
   product frame. A still held > 1.5 s with code motion on top reads as a
   slide, however good the motion is.
3. **Stage colour = the assets' studio ground.** Sample the border of every
   photo and clip (`film_audit.py` does it and fails beyond Δ3 per channel). Set
   the stage to that exact hex. If photos and clips differ by a step, darken
   the brighter one with `filter: brightness()` rather than tinting the stage.
   Cover-fit clips so any remaining edge leaves the frame.
4. **No texture over studio-ground footage.** Grain, falloff and vignettes are
   for code-drawn worlds; over the brand's white or black sweep they tint the
   ground and expose every clip rectangle. The audit fails it in footage mode.
5. **One signature transition, from the product's own geometry.** Hinge → the
   frame folds on a seam. Lens → iris out of the lens. Screen → through the
   screen (recipe 20). Flip screen → rotate on its axis. Write it into the shot
   list as `Signature transition:` and use it on at least three act exits
   (write "signature" in those Exit lines; the audit counts them). Variety
   belongs in type entrances and small events, not in the act changes.
6. **Anchor the product to one screen line.** Decide where the signature lives
   (the seam at x = 960, the lens at a point) and place every product shot so
   the matching part of the product lands there. Measure it on an extracted
   frame (bounding box of non-ground pixels), don't eyeball it. This is what
   lets two different clips cut as one motion (recipe 26).
7. **Draw nothing on the product.** No focus brackets, capture rings, cursors,
   hairlines, specular arcs over official footage — they turn an ad into a
   software demo. The single exception is a HUD that reproduces the product's
   own UI (a camera's viewfinder, recipe 21). The audit warns at ≥ 3 such marks.
8. **Copy in the audience's language, from the brand's localised page.** One
   claim per shot. Prefer the line that has a number. A feature name is a
   label, not a headline; if you use one, pair it with the brand's sentence.
9. **Colour comes from the footage.** Ground, two text greys (`#1D1D1F`-ish
   ink, a mid grey for kickers). No invented accent: the product and its
   screens are the colour.
10. **Uneven rhythm.** At least one burst (several cuts inside a second) and
    one long hold. Five equal acts each doing "feature + title" is a deck.

## Footage-led floors (15 s; scale with length)

| Measure | UI / code-drawn film | Footage-led film |
| --- | --- | --- |
| Tweens (non-filler) | ≥ 90 | ≥ 60 |
| Entrance mechanics | ≥ 8 | ≥ 5 |
| Distinct eases | ≥ 8 | ≥ 6 |
| Camera moves | ≥ 8 | ≥ 5 |
| Grain texture | required | **not allowed** over studio-ground footage |
| Stage = studio ground | checked when assets have one | checked (Δ ≤ 3) |
| Signature transition | warning if missing | **required**, ≥ 3 exits |
| Non-crossfade transitions | ≥ 2 | ≥ 2 (seam open, hinge fold and screen portal are recognised) |

All other checks (shot list, copy sheet, assets manifest, layout gate, pixel
gate, music) are unchanged.

## Tools you will need for review

- Snapshot tools must **seek the videos themselves**: for each `<video>` set
  `currentTime = data-media-start + (t − data-start) × data-playback-rate` and
  wait for `seeked`, or every snapshot shows the poster frame and you will
  "fix" problems that don't exist.
- Duplicate a clip file if it appears twice at the same time (two halves of a
  fold). The renderer's media discovery treats one file in two places as a risk.
- To check text placement over footage: hide the text, screenshot, and measure
  how many non-ground pixels sit under each text box (> 2% means the line is on
  the product). `layout_audit.mjs` checks boxes, not pixels.
