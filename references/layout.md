# Layout — where things sit

> Read before placing anything. `scripts/layout_audit.mjs` checks the result
> frame by frame in a real browser; a film is not done until it prints
> `0 failed`.

Both other gates can pass while the frame is a mess: a headline under the input
bar, the logo sitting on the first character of a word, a notification card
parked on the brand mark, a card hanging 10 % off the edge. Viewers see those in
the first second. This file is how to not make them.

## 1. Plan the frame before writing coordinates

Every act gets a **zone map** in `shot-list.md` before any CSS:

| Act | Headline zone | Product zone | Accent / logo zone | Empty on purpose |
| --- | --- | --- | --- | --- |
| 2 | top-left, y 120–300 | lower band, y 560–900 | none | top-right |

- Zones do not overlap. If the product moves into the headline zone, the
  headline leaves first (or the camera moves so it does).
- One focal point per beat. While the product works, the headline is either
  gone or small and out of the way.
- Leave one side genuinely empty, on purpose, and name it. Asymmetry is good;
  random leftover space is not.

## 2. Hard rules

- **Text is never covered.** No card, bar, image, logo or device paints over
  text that is visible, not even its corner, not even for half a second. If two
  things must share space, the text moves, fades, or the other thing goes
  behind it.
- **The logo never sits on text.** Logo and wordmark get their own clear space
  (at least the logo's own height around it).
- **Text never overlaps text.** A new line arrives after the old one has left
  or has moved out of its box.
- **No corner marks.** No logo, wordmark or brand name parked in a corner for
  the film (a TV-channel "bug"). It fights every composition it sits on, and a
  brand film is not a broadcast. The logo appears once: in the lockup.
  `layout_audit.mjs` fails a small brand mark held in a corner for ≥ 0.3 s
  (an icon inside product UI — an input bar, an app window — is exempt).
  A corner logo does **not** count as the persistent element that crosses acts.
- **The lockup is one group, built for this frame.** See "The last frame" below.
- **Title safe = 48 px.** No text closer than 48 px to any edge (96 px is
  better for headlines).
- **Nothing parks half off-frame.** Things may enter and leave through an edge.
  Once something stops moving, it is either fully inside, or a declared bleed
  (`data-bleed` on the element, ≥ 25 % off-frame, chosen on purpose). A card
  5–20 % off the edge always reads as a mistake.
- **Moving things re-check their landing.** When a timeline moves an element
  (`x`, `y`, `scale`, camera), compute where it ends and check it against the
  zone map. Most collisions in rejected films came from an element that was
  fine at its CSS position and landed on something after a tween.

## 3. Composition habits that read as "designed"

- Align to a few verticals: pick 2–3 x positions (e.g. 120, 960, 1440) and put
  left edges on them. Headline, cards and labels share those lines.
- Group by distance: things that belong together sit ≤ 24 px apart; separate
  groups ≥ 80 px apart. Equal spacing everywhere looks like a list.
- Overlapping cards are fine when the overlap is large and clear (≥ 30 % of the
  card) and the covered card's text is not under the top card. A 20 px sliver
  of overlap looks like a bug.
- A card cluster needs a counterweight: if three cards fill the right two
  thirds, the headline anchors the left third.
- Labels belong to their object: same left edge or centred under it, 12–20 px
  away, never closer to a neighbour than to their own object.

## 4. Running the gate

```bash
node scripts/layout_audit.mjs <project>/film/index.html --shots <project>/.gates/layout
```

It seeks the timeline every 0.1 s and fails on anything lasting ≥ 0.3 s:

| Check | Means |
| --- | --- |
| text hidden | visible text under an opaque box / image painted above it |
| text collision | two separate texts overlapping |
| text clipped | text cut by the frame edge while holding still |
| safe area | text inside the 48 px margin |
| parked off-edge | a card / image holding still while 5–70 % off-frame (or a `data-bleed` under 25 % off) |

Each line names the element, the time range and what covers it. `--shots`
saves a screenshot of every problem; look at them, fix, re-run. On `0 failed`
it writes `.gates/layout_audit.ok`; `score_lib` refuses to call the film ready
without it.

What it does not catch: ugly but legal placement. After `0 failed`, still look
at one still per act and ask: where does the eye land first, and is that the
thing this act is about?

## The last frame

The lockup is the frame people screenshot. A rejected film ended on an official
key-visual still that already had the product's name set in large 3D type, with
the phone lying across those letters — then added its own logo, name, slogan,
price and URL in a block in the lower left, far from the picture. Two titles,
a product colliding with type, and a dead band of black between them; the 4:3
still was contained in 16:9, so the picture sat small in the middle of a black
field. Rules:

- **Check every candidate end frame for type baked into the image** (record it
  in `assets.md`). If the official frame already carries the name or headline,
  either use it *as* the lockup with nothing added but a small logo / date
  line under it on the same axis, or don't use it. Never stack your own title
  next to the brand's title.
- **Product never crosses the type.** Not in the image you pick, not in what
  you add. If the hero frame has the product over its own letters, pick
  another frame.
- **One group, one axis.** Logo, name, line, CTA sit on the product's axis
  (centred under it, or as a block vertically centred beside it), with a gap
  smaller than the block's own height. Text in a far corner while the product
  is in the middle reads as two layouts.
- **Fill the frame for its shape.** Don't `object-fit: contain` a 4:3 still into
  16:9; cover it and choose the crop, or scale the product so the group spans
  at least half the frame height. Empty space is fine when it's one deliberate
  field, not leftovers on three sides (`layout_audit.mjs` warns on contained
  media).
- Look at the last frame alone, full size, before delivering. Ask: is there one
  thing to look at, and is it where the eye lands?

