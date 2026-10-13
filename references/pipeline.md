# Engineering pipeline

> **Not the first file to read.** Start with `SKILL.md`, `creative.md`,
> `layout.md`, `assets.md`, `quality-bar.md`, `shot-list.md`, `recipes.md` and `examples/office-agent/`.
> Nothing in this file makes a film good; it only keeps a good one from breaking.
> The film is done when `scripts/film_audit.py`, `scripts/layout_audit.mjs` and
> `scripts/frame_audit.py` all print `0 failed`.

The film is a single static HTML page driven by a paused GSAP timeline that the
renderer seeks frame by frame. Nothing is captured live, so anything that depends
on wall-clock time, network access at render time, or a system font will fail
sooner or later. Everything the film needs must be a local file.

## Directory layout

```
<film-project>/
├── film/
│   ├── index.html          ← generated; what the renderer reads
│   ├── hyperframes.json
│   ├── package.json
│   ├── assets/fonts/*.woff2
│   ├── assets/<brand assets>
│   ├── renders/            ← output mp4s
│   └── snapshots/          ← frame dumps for review
├── assets.md              ← every image file + source URL + logo check
├── shot-list.md
├── copy.md
├── src/
│   ├── index.tpl.html      ← the source of truth you edit
│   ├── build.py            ← tpl → film/index.html + CJK subset list
│   └── chars.txt           ← generated subset character set
└── audio/
    ├── score.py            ← the score, in code
    ├── score.wav           ← generated
    └── mix.wav             ← score + SFX, loudness-normalized
```

## Why a template plus a build step

Two problems make a hand-written `index.html` the wrong source of truth:

1. **Repetition.** Six pipeline nodes, six table rows, thirty document lines —
   hand-writing them means every copy tweak is six edits and one missed.
2. **Font subsets.** The CJK subset has to be regenerated whenever the copy
   changes, and it has to cover exactly the characters on screen.

So generate the file. `build.py` reads `index.tpl.html`, substitutes `__NODES__`,
`__CELLS__`, `__TYPED__`-style placeholders, collects every character above
`0x2E80` into `chars.txt`, and writes `film/index.html`. Keep the generated file
out of the editing loop — edit the template, run the build.

The typed-input case is worth doing per character: emit one `<span class="ch">`
per character and `tl.set(ch, { opacity: 1 }, t)` each on its own micro-timing.
A character-by-character reveal is unmistakably hand-made and a CSS `width`
animation is not.

## Composition structure

Three nested levels, each with a job:

```html
<div class="scene" id="s2">        <!-- the act: opacity + lifetime -->
  <div class="cam" id="cam2">      <!-- the camera: transform, scale, x -->
    <div class="scene-inner">      <!-- the content -->
```

- Animate **`.cam`** for movement (scale / x / y / rotation).
- Animate **`.scene-inner`** for the act's own fade, if it needs one.
- Never fade a `.cam` that is also being scaled, and never fade an element that
  has its own opacity animation — the two fight and you get ghosting.

**Initial hidden state belongs in CSS, not in the timeline.** Put
`#s2, #s3, #s4, #seal, #lock, #cta { opacity: 0; }` in the stylesheet. A
`tl.set(..., { opacity: 0 }, 0)` looks equivalent but is not: lint flags it, and
at frame 0 the renderer may capture the element fully visible before the `set`
runs, which shows up as every future scene stacked on top of the first frame.

## The authoring loop

```bash
cd film
npx --yes hyperframes@0.8.78 lint                 # after every structural change
npx --yes hyperframes@0.8.78 check                # the gate: lint + browser audit
npx --yes hyperframes@0.8.78 render . -q draft -o ./renders/draft.mp4    # while iterating
npx --yes hyperframes@0.8.78 render . -q high --fps 30 -o ./renders/final.mp4
ffprobe -v error -show_entries stream=codec_type,duration -of csv=p=0 ./renders/final.mp4
```

Target **0 lint errors**. Warnings are not automatically fine — read them:

- `gsap_non_transform_motion`: you animated `letterSpacing`, `top`, `width`.
  Animate `scale` / `x` / `y` instead, or accept the jitter.
- **Contrast findings**: the browser measures real rendered contrast. Anything
  under 4.5:1 for body text is a genuine defect and usually means you put light
  text on a light element (white numbers inside a white chip, a dark label on a
  dark card). Fix by switching the element's colour, not by ignoring it.
- Overlap warnings are usually fine; a scale animation briefly overlapping its
  own bounding box is not a real defect.

## Render-time pitfalls on macOS

- `timeout` does not exist on macOS. Wrap long commands with
  `perl -e 'alarm N; exec @ARGV'`.
- The npx cache occasionally corrupts with `ENOTEMPTY`. Move the offending
  `_npx/<hash>` directory aside rather than deleting it.
- Set `PRODUCER_BROWSER_GPU_MODE=hardware` for the render; software GPU mode is
  much slower and sometimes produces black frames on large transforms.
- `hyperframes render` wants the project directory as a positional argument, so
  `render . -q high` is right; `render --output x.mp4` in a project root also
  works, but passing both a path and `-o` is the reliable form.

## Reviewing the render

Nothing about a film can be verified from source. After the render:

```bash
# contact sheet, 2 per second — a 30-cell grid of a 15s film
ffmpeg -y -v error -i renders/final.mp4 -vf "fps=2,scale=384:-1,tile=6x5" -frames:v 1 snapshots/sheet.jpg

# one suspect frame, full size
ffmpeg -y -v error -ss 11.0 -i renders/final.mp4 -frames:v 1 snapshots/f11.png
```

Then look at them with an image-capable model. See `creative.md` for the review
prompt that works. Keep the sheets and frames in `snapshots/` — they are the
evidence for what changed between versions.

Check for these specifically, because each one has actually shipped before:

- **Ghosting at a scene boundary.** The previous act is still partly visible
  because its fade starts on the same frame the next act fades in. Give the
  outgoing act a 0.2s head start.
- **A one-frame black flash in a whip transition.** Caused by fading out before
  the incoming scene is opaque. Overlap them, or make the incoming camera move a
  `fromTo` that starts at the same instant.
- **An element that shows up at frame 0** even though it belongs to act 5:
  initial hidden state ended up in the timeline instead of CSS.
- **A visible text collision** introduced by a font swap. If you edit copy and
  the build does not regenerate the subset, the fallback font's metrics push a
  line into an overlap.

Two traps in the review tooling itself:

- **A vision model reading a contact sheet raises false alarms.** On a 6×5
  sheet of thumbnails it called four frames "black / glitched" that were fine.
  Before changing anything, map the flagged cell to its timestamp
  (`t = (row·cols + col) / fps`), extract that frame full size with
  `ffmpeg -ss t -i silent.mp4 -frames:v 1`, and look again. Fix only what
  survives the full-size look.
- **Puppeteer hangs on `page.evaluate(t => tl.seek(t))`.** An arrow with an
  expression body returns the GSAP timeline, which is circular and never
  serialises. Always use a block body: `t => { tl.seek(t, false); }`.

## Music and mixing is a separate pass

Score synthesis is its own step — see `scoring.md`. The order is:

1. Render the picture silent.
2. Write and generate the score against the picture's cut list.
3. Layer SFX from the shared library, `loudnorm` the sum, mux it onto the
   picture with `-c:v copy`.

Do not try to do all three in one pass; you will re-render the picture every time
a note moves.
