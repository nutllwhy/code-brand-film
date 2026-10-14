# Creative direction — how to make a 15-second brand film that does not look made by a machine

Read this before writing any HTML. The engineering is the easy half; this is the
half that decides whether the film is deliverable.

> **This file is not the whole method.** An agent that read only this file,
> `pipeline.md` and `scoring.md` built a film that linted clean, sounded fine,
> and failed 13 of 19 checks: 36 tweens, 1.3% of the frame covered, a 4.4s
> stretch where nothing moved, no logo, no product. Before you write code you
> also need [layout.md](layout.md), [assets.md](assets.md), [quality-bar.md](quality-bar.md), [shot-list.md](shot-list.md),
> [recipes.md](recipes.md) and the timeline in `examples/office-agent/`.
> The film is done when `scripts/film_audit.py`, `scripts/layout_audit.mjs` and
> `scripts/frame_audit.py` all print `0 failed` — not when it lints, and not when you like the sheet.

## Start from one sentence, not from the visuals

A brand film fails when it starts as "a nice-looking animation". It works when
the whole film is a physical metaphor for one sentence the product actually
claims, and every act is a literal depiction of part of that sentence.

Two real examples, both delivered and both accepted:

| Film | The sentence | The move | The film |
| --- | --- | --- | --- |
| A · memory-first AI assistant (dark) | "What stays with you, shapes what comes next." | The logo is a blob with an off-centre hole. Treat that hole as a camera lens: dive into it at the start, collapse the whole world back into it at the end. | 5 acts: FORGET (text falls apart) → REMEMBER (floating memory cards in the lens) → ACT (verbs firing) → IMPRINT (official imagery through an iris) → LOCKUP (everything falls back into the hole) |
| C · pocket gimbal camera (dark, hardware) | The product's official slogan, used as the opening line. | The device has a flip-out screen: go **in through its own screen**, and the rest of the film is what that screen sees. | 5 acts: product photo pulled out of a macro close-up with a light sweep → footage appears on the device's screen, camera dives through it → viewfinder HUD over four official sample shots, one feature proven per shot → zoom button 1×→2× and the frame pushes 2× → stabiliser mechanism, then wordmark + logo + slogan |
| D · foldable phone (white, hardware, footage-led) | The page's two-word greeting, one word on each side of the fold. | The product folds on a hinge: put a seam down the middle of the frame and make **every act change a fold shut on it and an opening out of it**. Every product shot is placed with its hinge on the seam. | 5 acts: greeting folds shut → hero clip opens out of the seam → hinge-to-hinge match cut into the big-screen clip, screen size number flips → five poses in 1.5 s → titanium hinge macro shrinks to a line, the line turns 90° into the seam, the name splits around it. See `footage-led.md`. |
| B · office-automation agent (light) | The product's key line ends on a decision verb ("…and you make the call"). | Take that last verb literally. Make it an actual stamp that slams on the final downbeat. | 5 acts: one sentence typed → six pipeline steps → laptop shut, work keeps running in the cloud → deliverables arrive → the stamp |

The test: can you say the film's idea in one sentence that contains a *physical
verb*? "Dive into the logo." "Slam a stamp." If it's "show the product's
features", you don't have a film yet.

Look for the metaphor in the brand's own assets first. Film A's idea only exists
because the logo has a hole in it. Real assets are better raw material than
invented ones because they carry the brand for free.

**The metaphor is the frame, the product is the picture.** The physical verb
decides the camera and the transitions; acts 2–4 are filled with the product's
own interface doing its own work. Film A's lens has memory cards and real
imagery inside it. Film B's stamp lands on deliverables that were built on
screen. A verb is not enough by itself:

| Metaphor | Why it failed / worked |
| --- | --- |
| "Your sentence is a stone thrown into a lake; the ripples grow the whole work system." | Rejected. Ripples and six glowing icons on a dark void. The verb is fine; nothing the product actually produces is ever on screen, so it is an ad for anything. |
| "A drop of ink becomes lines, becomes shapes, becomes a flower." | Rejected. Same failure: pure abstraction, 3% of the frame lit. |
| "Dive through the logo's hole." | Accepted. Through the lens you see the product's memory cards and the brand's own imagery. |
| "The work goes on while the lid is shut; you just stamp it." | Accepted. Each act shows a real step: typed instruction, pipeline, synced devices, finished files. |

**Hardware has no interface to show — its output is the interface.** For a
camera, headphones, a projector: acts 2–4 are what the product produces (the
footage, framed by its own viewfinder HUD; the sound, as a waveform the
picture cuts to), and every feature line on screen gets a shot that proves it
(see recipes 21–22). Product photo and footage placed side by side — device
on the left, a framed clip on the right — was rejected in review as a slide;
go *through* the product to its output instead of placing them next to each
other.

Test it: describe act 3 to someone without saying the metaphor. If what is left
is "shapes move", rewrite it until it is "the spreadsheet fills itself while the
laptop is closed".

## The five-act skeleton, and its timing

15 seconds is the default commercial length. The reliable split:

| Act | Time | Job |
| --- | --- | --- |
| 1 Hook | 0–3.0s | The sentence arrives. Establish the world; move slowly, one idea. |
| 2 Development | 3.0–6.0s | Something repeats, one step per beat. Rhythm enters. |
| 3 Turn | 6.0–9.5s | The longest act. Change of state (night falls, the laptop closes, the work keeps going). This is where drums drop out. |
| 4 Payoff | 9.5–12.5s | The result arrives. Fastest cutting, most objects, brightest music. |
| 5 Landing | 12.5–15s | One line, one gesture (the stamp, the collapse), then lockup + CTA. |

Every cut should land on a grid. Pick one beat length for the whole film and put
every act boundary and every element entrance on multiples of it. This is what
makes the music and the picture feel like one object rather than two layers.

## Motion rules

**One pull-back per film.** A camera that pulls away reads as "this is ending".
If you pull back three times, the film has three endings and feels shapeless.
Push in, push in, push in, pull once at the reveal, then settle.

**Moves live on a camera layer, never on the element.** Give each act its own
`<div class="cam">` inside the scene and animate *that*. Scaling the content
directly makes the whole thing read as a sticker being resized. The camera layer
is also what lets you do a real zoom-through: scale `#cam3` to 3.2 and translate
it at the same time, so act 4 looks like you flew through the laptop screen.

**Keep the accent colour as a highlight, not a ground.** A saturated accent
works as the one thing that glows. Filling the frame with it looks like a
promotional template. Two palettes that worked:

- dark: base `#10142A` (deep indigo), foreground `#F3EDE2` (warm paper), accent
  `#F5B860` (amber). On a dark base the accent glows.
- light: base `#F4F2ED` (warm paper), ink `#15171C`, accent `#2B5CFF` (blue).
  On a light base the accent has to be used sparingly or it turns muddy.

**Compose asymmetrically.** Centring every element produces the "presentation
slide" look. Put the headline at x=120 and the object at x=640. Let things run
off the edge.

**Add texture — unless the brand's footage is the picture.** (Over a brand's
white or black studio sweep, texture tints the ground and every clip edge
shows; see `footage-led.md`.) A paper-grain SVG turbulence layer at 11–16% and a radial
falloff are what separate "rendered" from "designed". A barely-moving grain
(`x: 26, ease: "steps(45)"` over the full film) costs nothing and removes the
sterile flatness of a pure vector frame.

**Vary entrance mechanics.** If every element fades up and slides 40px, the film
is one long animation. Mix: a line that types character by character, a card that
flies in on rotationY, a number that counts, a line that draws itself with
`stroke-dashoffset`, a stamp that scales down hard from 2.4×, a shape that pulses
`yoyo/repeat`.

## Things that read as "made by AI" and must be avoided

These come from real client rejections of this exact kind of work:

- Beige and orange-pink palettes with everything neatly arranged on a cream
  background. Reads as a sweet lifestyle template, not a brand film.
- Symmetry, and objects parked in the dead centre.
- Every act being the same length doing the same thing.
- Continuous smooth easing everywhere. Real motion has hard attacks — a stamp
  hits with `power4.in` over 0.25s, not `power2.inOut` over 0.6s.
- A film with no music, or with music that ignores the cuts.
- Text that is never the point. If an act has no words, that is fine; if every
  act has three lines of words, it's a slideshow.
- An abstract metaphor carrying the whole film (ripples, ink, particles, light,
  orbs, a seed growing) with no product interface inside it.
- A dark film that is mostly void. Deep indigo/purple ground with dim, thin,
  low-contrast elements on it reads as "nothing is there" on a phone. On a dark
  ground the content must be lit: paper-white cards, bright text, the accent
  glowing — and it must occupy the frame. If the contact sheet looks like a
  black page with dust on it, the film is under-built, not moody.
- Copy at body size. Headlines in a 1080p film are 72–120px; a 30px line at the
  top of the frame is a caption nobody reads.

## The review loop that catches the rest

This loop is for **polish**, and it only starts after both audits print
`0 failed`. If either gate fails, the film is not a polish problem — it is
missing content, and fixing "the single worst frame" will not save it. Go back
to the shot list and the timeline.

You cannot judge a film by reading its code. Render it, then look at it:

1. Render at 30 fps.
2. Cut a contact sheet: `ffmpeg -i film.mp4 -vf "fps=2,scale=384:-1,tile=6x5" -frames:v 1 sheet.jpg`
3. Look at the sheet with an image-capable model. Ask for: overall coherence,
   any broken frame (blank, garbled text, overlapping elements, ghosting), a
   score out of 10, and **the single most worthwhile fix, with the frame number**.
4. Fix that one thing. Re-render. Repeat at most twice — after that you are
   polishing noise.

Ask for one fix, not a list. A model asked for a list will invent ten, most of
them wrong; asked for the worst one it is usually right about the worst one.

For an individual suspect frame, extract it directly and ask a focused question
(`-ss 11.0 -frames:v 1 f11.png`). Ghosting and text overlap only show at speed,
so also sample the tile sheet at 2 fps rather than 1 — a 0.2s artifact
disappears entirely at 1 fps.

## Chinese text

System CJK fonts are not reliable inside the headless render browser; PingFang SC
fails to load and the render silently falls back to a different typeface with
different metrics, which shifts every line in your layout. Embed subsetted
webfonts instead: Noto Serif SC for headlines, Noto Sans SC for body, downloaded
from Google Fonts' CSS API with a `text=` parameter limited to the characters the
film actually uses. The build step should collect the character set from the
template so the subset stays in sync when the copy changes.
