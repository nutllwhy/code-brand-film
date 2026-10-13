# Example: office-automation agent, 15s, light palette

A complete, renderable film built with this skill — the reference for what
"enough" looks like. `film_audit.py` on it: 97 non-filler tweens, 12 entrance mechanics,
4 non-crossfade transitions, 19 eases, every act ≥ 7 timed events.

The brand is a placeholder ("Acme 工作台", `assets/logo.svg`). The structure,
motion and score are the real thing. Read it alongside
`references/shot-list.md` (the worked example there is this film).

```
shot-list.md         filled in before any code
copy.md              every on-screen line and its source (film_audit.py checks it)
reference-sheet.jpg  2 fps contact sheet — compare yours against it
src/index.tpl.html   the film — edit this (≈400 lines: CSS, markup, one timeline)
src/build.py         fills __NODES__ / __CELLS__ / __TYPED__, writes film/index.html + src/chars.txt
film/                what the renderer reads; assets/fonts are Noto Serif/Sans SC subsets (SIL OFL)
audio/score.py       the score, using ../../../scripts/score_lib.py
```

Run it:

```bash
cd examples/office-agent
python3 src/build.py                                              # template → film/index.html
../../scripts/fetch_cjk_fonts.sh src/chars.txt film/assets/fonts   # only after changing Chinese copy
python3 ../../scripts/film_audit.py film/index.html                # code gate
cd film && npx --yes hyperframes@0.8.78 lint
PRODUCER_BROWSER_GPU_MODE=hardware npx --yes hyperframes@0.8.78 render . -q high --fps 30 -o ./renders/silent.mp4
python3 ../../scripts/frame_audit.py renders/silent.mp4              # pixel gate
cd .. && python3 -m venv .venv && .venv/bin/pip install numpy && .venv/bin/python audio/score.py
ffmpeg -y -i film/renders/silent.mp4 -i audio/score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest film/renders/film.mp4
```

## How to read the timeline

The `<script>` at the bottom of `index.tpl.html` is one paused GSAP timeline,
written top to bottom in time order, one comment block per act. Things to notice:

- **`var B = 0.5`** — the beat. Every act boundary and every pipeline step is a
  multiple of it, and `audio/score.py` uses the same number.
- **The input bar lives outside every `.scene`.** That is what lets it survive
  act 1's fade and dock top-left as the brief for act 2 (persistent hand-off).
- **Each act has its own `.cam`.** All movement — the lateral whip into act 3,
  the zoom-through into act 4, the shake on the stamp — is applied to the camera,
  never to the content.
- **Initial hidden state is in CSS** (`#s2, #s3, … { opacity: 0; }`), not in a
  `tl.set` at time 0.
- **One proxy drives three screens** in act 3 (`prog.v`), which is the whole
  idea of "sync" made literal.
- **The laptop is a 3D rig** (`#lapRig` / `#deck` / `#lid` / `#lidBack`), not a
  flat rectangle — that is the only reason the lid can close convincingly.
- **The stamp lands at 13.5s**, the downbeat the score's boom is placed on.

## Adapting it to a different product

Do not reskin it. Write your own shot list first — a different product has
different behaviours and needs a different metaphor. Lift individual pieces
(the input bar, the pipeline, the device sync, the card fly-in, the stamp) where
your shot list calls for them.
