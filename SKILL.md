---
name: code-brand-film
description: >
  Produce a short brand film or product promo (10-60s, typically 15s) entirely
  as code: one static HTML page with a paused GSAP timeline that a renderer seeks
  frame by frame, plus a music score synthesized in Python. Use when the user
  wants a 品牌宣传片, 广告片, 宣传动画, 产品短片, 发布会开场视频, brand
  film, promo video, product teaser, logo animation, or a generated ad spot —
  especially when they ask for 高级感 / 艺术感 / 电影感 / 别像模板, or when an
  existing video "looks like AI made it" or "too simple" and needs to be redone
  properly. Also use when a film already exists and needs a score, a soundtrack,
  background music, or 配乐, or when a code-generated video needs ghosting,
  contrast, font, or transition defects fixed.
metadata:
  category: media
---

# Code-generated brand films

A film is one static HTML page inside `film/`, driven by a paused GSAP timeline
that the renderer ([HyperFrames](https://github.com/heygen-com/hyperframes))
seeks frame by frame. Every asset is a local file. The score is a separate Python
program that writes a WAV, muxed onto the silent picture at the end.

## The failure this skill exists to prevent

The usual failure is not a broken film, it's an **under-built** one: it lints
clean, has no bad frames, and still looks like a template. A real example built
from an earlier version of this skill had 18 tweens, one entrance mechanic
(fade + slide), only crossfades between acts, a logo redrawn as a circle,
system fonts, a tagline nobody had written, and no product on screen. The two
accepted films it was compared against had ~105 tweens, 9–12 mechanics, 2–4
non-crossfade transitions, and showed the product working in most acts.

So this skill sets **floors you can measure** and gives you **code to copy**.
There are two gates: `scripts/film_audit.py` on the HTML before rendering, and
`scripts/frame_audit.py` on the rendered MP4 after. Both must print `0 failed`.

**The floors are minimums, not targets.** A later film cleared the code gate at
exactly 70 tweens and 8 mechanics, padded with breathing headlines, and was still
an abstract ink-drop animation covering 3% of the frame with no product in it.
The tween count now excludes filler, and the pixel gate exists because pixels
cannot be padded. If you find yourself adding tweens to pass a number, stop: the
film is missing content, not motion. Aim at the reference example, not the floor.

## Read these — in this order

| Step | File | Why |
| --- | --- | --- |
| before anything | [references/creative.md](references/creative.md) | metaphor, five-act timing, motion rules, palettes, the AI-look traps |
| before anything | [references/quality-bar.md](references/quality-bar.md) | the numbers, the mechanic list, the transition list, product truth, real assets |
| before coding | [references/shot-list.md](references/shot-list.md) | the table you fill in first; worked example included |
| while coding | [references/recipes.md](references/recipes.md) | copyable GSAP for all 19 mechanics and transitions |
| while coding | [examples/office-agent/](examples/office-agent/) | a complete 400-line film that clears every floor — read its timeline |
| scaffold / render | [references/pipeline.md](references/pipeline.md) | layout, template+build, lint warnings, macOS pitfalls, defect checklist |
| music | [references/scoring.md](references/scoring.md) | beat grid from picture, energy plan, mix graph, verify without ears |

Do read the example's `src/index.tpl.html` end to end before writing your own.
Seeing how much one 15s film contains is worth more than any rule here.

## Workflow

1. **Collect sources.** Brief or product page: the mandatory selling line, 3–5
   concrete product behaviours, required copy and CTA, red lines. Download the
   **real logo** and any official imagery. Never redraw a logo as a shape.
2. **Find the metaphor** — one sentence with a physical verb, ideally taken
   from the brand's own asset or the selling line's own words (`creative.md`).
3. **Write `shot-list.md` and `copy.md`** in the film project (next to `film/`;
   the audit fails without them). `copy.md` lists every on-screen line with its
   source; see `examples/office-agent/copy.md`. Shot list from the template. Every act:
   ≥ 5 timed events, a named camera move, a named exit transition, three depth
   layers, a product behaviour (except hook/lockup), and a source for each line
   of copy. Run the self-check at its bottom. If the user is around, show it.
4. **Scaffold.** `film/hyperframes.json` (copy `assets/hyperframes.json`),
   `film/package.json` pinning `hyperframes@0.8.78`, `src/index.tpl.html`,
   `src/build.py` (copy `scripts/build_template.py`). Start from the example's
   CSS chrome (grain, falloff, corners, rail) — it's ten lines and it matters.
5. **Fonts.** `python3 src/build.py`, then
   `scripts/fetch_cjk_fonts.sh src/chars.txt film/assets/fonts` for Chinese.
   Latin fonts: download woff2 files into `film/assets/fonts/`. Every
   `@font-face` uses `url()` to a local file; `local()` is not allowed.
6. **Author** the timeline act by act from the shot list, pulling mechanics from
   `recipes.md`. Run `npx --yes hyperframes@0.8.78 lint` after each act.
7. **Gate.** `python3 scripts/film_audit.py film/index.html` → must print
   `0 failed`. Fix every FAIL by adding real content, not by gaming the regex.
8. **Render silent**, then `python3 scripts/frame_audit.py film/renders/silent.mp4`
   → must print `0 failed`. Make a contact sheet and put it next to
   `examples/office-agent/reference-sheet.jpg`; answer the three comparison
   questions in `quality-bar.md`. If yours is clearly thinner, go back to step 6
   — add product on screen, not decoration. Then fix the single worst frame.
9. **Score it** (`scripts/score_template.py` → `audio/score.py`), mix SFX,
   `loudnorm` to −14 LUFS, mux with `-c:v copy`.
10. **Deliver** one `MEDIA:`/file line per output. State what you verified
    (both audits' numbers, lint, loudness, the reference comparison) and what only the user can judge
    (taste, how the music sounds). Flag any invented copy and any low-res logo.

## Commands

```bash
python3 src/build.py
python3 <skill>/scripts/film_audit.py film/index.html           # code gate: must be "0 failed"
cd film
npx --yes hyperframes@0.8.78 lint                                # target 0 errors; read every warning
PRODUCER_BROWSER_GPU_MODE=hardware \
  npx --yes hyperframes@0.8.78 render . -q high --fps 30 -o ./renders/silent.mp4
python3 <skill>/scripts/frame_audit.py renders/silent.mp4        # pixel gate: must be "0 failed"
<skill>/scripts/review_frames.sh renders/silent.mp4 snapshots 2 "11.0,13.5"
```

## Hard rules (each one came from a rejected or broken film)

- **Floors are floors, not targets.** ≥ 90 non-filler tweens, ≥ 8 mechanics, ≥ 2 non-crossfade
  transitions, ≥ 8 eases, ≥ 8 camera moves, ≥ 5 events in every act (15s film).
- **Show the product working** in at least two acts — its interface, its
  output, a device running it, real-looking data. An abstract metaphor (ink,
  particles, light, a seed growing) with no product in it could be an ad for
  anything and is rejected even if every number passes.
- **Fill the frame.** A line of text and one small shape on a flat ground is an
  empty frame. Every act needs background, midground and foreground layers.
- **Copy comes from the source.** Every on-screen line traces to the brief or the
  product page; anything invented is flagged to the user.
- **Real logo, real fonts.** The brand's file, embedded woff2 subsets.
- **No template look.** No beige/orange-pink lifestyle palettes, no centring
  everything, no equal-length acts doing the same thing. The accent colour is a
  highlight, not a ground.
- **One pull-back per film.** It reads as "this is ending".
- **Motion lives on `.cam` layers**; initial hidden state lives in CSS; never
  fade an element that also has its own opacity tween. (Ghosting.)
- **No `Math.random()` in the timeline** — frames are seeked out of order.
- **Ship it with music**, landing the final hit on a downbeat. A brand film with
  no score is an incomplete delivery.
- **Verify honestly.** You cannot hear audio or watch motion in real time; report
  the checks you ran, not a feeling.
- **Client work gets reviewed before publishing.** Say so in the delivery.

## Bundled resources

```
scripts/film_audit.py       code gate, before render (floors, shot list, copy sources)
scripts/frame_audit.py      pixel gate, after render (coverage, detail, motion)
scripts/fetch_cjk_fonts.sh  Noto Serif/Sans SC subsets for exactly the characters used
scripts/build_template.py   template → film/index.html + CJK character list
scripts/review_frames.sh    render → contact sheet + stills + duration check
scripts/score_lib.py        instrument library + reverb + master (import, don't edit)
scripts/score_template.py   five-act arrangement to copy and fill in
assets/hyperframes.json     project config
examples/office-agent/      complete reference film (placeholder brand), with its
                            shot-list.md, copy.md and reference-sheet.jpg
```
