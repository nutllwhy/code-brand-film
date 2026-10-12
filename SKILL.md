---
name: code-brand-film
description: >
  Produce a short brand film or product promo (10-60s, typically 15s) entirely
  as code: one static HTML page with a paused GSAP timeline that a renderer seeks
  frame by frame, plus a music score synthesized in Python. Use when the user
  wants a 品牌宣传片, 广告片, 宣传动画, 产品短片, 发布会开场视频, brand
  film, promo video, product teaser, logo animation, or a generated ad spot —
  especially when they ask for 高级感 / 艺术感 / 电影感 / 别像模板, or when an
  existing video "looks like AI made it" and needs to be redone properly. Also
  use when a film already exists and needs a score, a soundtrack, background
  music, or 配乐, or when a code-generated video needs ghosting, contrast, font,
  or transition defects fixed.
metadata:
  category: media
---

# Code-generated brand films

A film is one static HTML page inside `film/`, driven by a paused GSAP timeline
that the renderer seeks frame by frame. Every asset is a local file. The score is
a separate Python program that writes a WAV, mixed with SFX and muxed onto the
silent picture at the end.

Two reference films came out of this method and both were accepted by the
client: a dark 15s spot for an AI assistant (the hole in the logo is a camera
lens you dive into) and a light 15s spot for an office agent (the key line's final verb becomes a stamp that slams on the final downbeat).

## Read before you start

| File | Read it when |
| --- | --- |
| [references/creative.md](references/creative.md) | **Always, before writing any HTML.** Metaphor, five-act timing, motion rules, palettes, the AI-look traps, and the review loop. |
| [references/pipeline.md](references/pipeline.md) | When you scaffold the project, and whenever lint or the render misbehaves. Directory layout, template+build, initial-hidden-state, macOS pitfalls, per-defect checklist. |
| [references/scoring.md](references/scoring.md) | When you write the music. Measuring the film's beat grid, act-by-act energy plan, the ffmpeg mix graph, verification without ears. |

## The workflow

1. **Understand the brand.** Read the brief or the product page. Get: what the
   product actually claims, the brand's real assets (logo, wordmark, imagery),
   the required copy, and any compliance red lines. Download real assets — they
   carry the brand in ways invented graphics do not.
2. **Find the metaphor.** One sentence containing a physical verb. See
   `creative.md` for the two worked examples and the test for whether you have
   one. Look for it in the brand's own assets first.
3. **Set the five acts.** Write down, per act: the time range, the picture, and
   the music. Put every act boundary on a shared beat grid.
4. **Scaffold.** Create the project directory, `film/hyperframes.json` (copy
   `assets/hyperframes.json`), `film/package.json` with the pinned CLI version,
   and the `src/` → `film/` build. Copy `scripts/build_template.py` to
   `src/build.py` and fill in the CONTENT blocks.
5. **Author the film** in `src/index.tpl.html`, then run `python3 src/build.py`.
   Run `lint` after every structural change; it catches things you cannot see.
6. **Render silent** at high quality and review the frames (step 8) before
   touching music. A film that does not work silent will not be rescued by a
   score.
7. **Earn the picture.** Fix what the frames show, re-render. A 15s film at 1080p
   renders in about 15 seconds once the browser is warm, so iterate freely.
8. **Score it.** Copy `scripts/score_template.py` to `audio/score.py`, measure
   the picture's beat grid, fill in the acts, generate `score.wav`.
9. **Mix and mux.** SFX on top, `loudnorm`, then `-c:v copy` onto the silent
   picture. Verify loudness and waveform structurally — you cannot hear it.
10. **Deliver with a MEDIA line per file**, and state plainly what you verified
    and what only the user can judge.

## Commands

```bash
cd film
npx --yes hyperframes@0.8.78 lint                                  # after every structural change
npx --yes hyperframes@0.8.78 check                                 # lint + browser audit
npx --yes hyperframes@0.8.78 render . -q draft -o ./renders/draft.mp4
PRODUCER_BROWSER_GPU_MODE=hardware \
  npx --yes hyperframes@0.8.78 render . -q high --fps 30 -o ./renders/final.mp4
```

Target **0 lint errors**. Read every warning — contrast findings are real
defects, not noise. `references/pipeline.md` has the warning-to-cause table.

## Reviewing a render

Never judge a film from its source. Sheet it and look at it:

```bash
scripts/review_frames.sh film/renders/final.mp4 film/snapshots 2 "11.0,13.5"
```

Then ask an image-capable model for overall coherence, any broken frame, a score,
and **the single most worthwhile fix with its frame number**. Fix that one thing
and re-render. At most twice — past that you are polishing noise.

Sample at 2 fps, not 1: ghosting at a scene boundary and a one-frame black flash
in a whip transition disappear entirely at 1 fps.

## Scoring

A score that ignores the cuts fights the film for its whole length. Measure the
picture's grid first — count the spacing between two repeated events and use that
as the beat. Read `references/scoring.md`, then:

```bash
cd <film-project> && python3 -m venv .venv && .venv/bin/pip install numpy
cp <skill>/scripts/score_template.py <film-project>/audio/score.py   # then edit it
perl -e 'alarm 200; exec @ARGV' .venv/bin/python audio/score.py
```

`scripts/score_lib.py` is the instrument library: felt piano, bell, pluck,
marimba, pad, sub, kick, hat, clap, tick, thud, boom, riser, swell, plus an
FFT-convolution reverb and a soft-clip master. Signature — no samples, no
licensing:

```python
S.place(S.pad(['G2','D3','B3'], 3.2, att=1.0, rel=0.5), 0.0, send=0.55)
S.place(S.kick(vel=0.9), 3.0 + k * 0.5)
S.place(S.bell(hz('B5')), 2.5, pan=0.2, send=0.6)
S.write('score.wav')
```

## Bundled resources

```
scripts/score_lib.py       instrument library + reverb + master (import, don't edit)
scripts/score_template.py  the arrangement to copy and fill in, with the act structure
scripts/build_template.py  template → film/index.html + CJK subset, with content blocks
scripts/review_frames.sh   render → contact sheet + stills + duration check
assets/hyperframes.json    project config to copy into a new film
```

## Non-negotiables that came from real rejections

- **No template look.** Beige and orange-pink palettes with everything centred on
  cream read as a sweet lifestyle template. What clients ask for instead: a
  good-looking film with motivated camera moves, a premium feel, and artistry.
- **The accent colour is an accent.** On a light base a saturated accent turns
  muddy when it fills the frame; on a dark base it glows.
- **One pull-back per film.** A pull-back reads as "this is ending".
- **Never fade an element that also has an opacity animation**, and put initial
  hidden state in CSS, not in the timeline. Both cause ghosting.
- **Ship it with music.** Delivering a brand film with no score is an incomplete
  delivery, not a neutral one. If you cannot source a track, synthesize one.
- **Verify honestly.** You cannot hear audio and cannot watch motion in real time.
  Report what you checked (loudness numbers, waveform shape, frame sheet) rather
  than claiming a subjective result.
- **Client work gets reviewed before publishing.** Say so in the delivery.
