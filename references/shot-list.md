# Shot list — fill this in before writing any HTML

Write it to `<film-project>/shot-list.md`. Show it to the user if they are
around; either way, do not start authoring until every cell is filled. An empty
cell here becomes an empty act on screen.

## Part 1 — sources

| Item | Value | Source |
| --- | --- | --- |
| Product's mandatory selling line | | brief p.? / product page URL |
| 3–5 concrete product behaviours | 1. … 2. … 3. … | |
| Required copy / CTA / offer | | |
| Red lines (claims you must not make, words you must not use) | | |
| Logo file | path, format, size | official site / brand kit |
| Other brand assets (wordmark, imagery, colours) | | |
| Fonts | family + weight, embedded file path | |

If the logo you have is a raster under 256px, note it here and flag it in the
delivery.

## Part 2 — the idea

- **Metaphor sentence (must contain a physical verb):**
- **Where the metaphor comes from** (which asset, which word in the brief):
- **Palette:** base / foreground / accent / secondary — and why the accent is used as a highlight here, not a ground.
- **Beat grid:** seconds per beat, and which on-screen event sets it.
- **Signature transition:** one move taken from the product's own shape (hinge → fold on a seam, lens → iris, screen → portal). Mark the act exits that use it with the word "signature". Required for footage-led films (≥ 3 exits).
- **Studio ground:** the hex sampled from the official photos / clips, which becomes the stage colour (footage-led films; `footage-led.md`).

## Part 3 — acts

One block per act. Every act needs **at least five** timed events and must name
its camera move, its exit transition, and its depth layers. Fill in the
"mechanic" column with names from `quality-bar.md`'s list, and check that no two
consecutive rows use the same one.

### Act 1 · <name> · 0.0–3.0s

- **Product behaviour shown:** (or "hook — none")
- **On-screen copy:** "…" ← source
- **Camera:** (e.g. settle 1.04 → 1.0, power2.out)
- **Depth layers:** bg: … / mid: … / fg: …
- **Exit transition into act 2:** (from the transitions list; ≤ 1 plain crossfade in the whole film)
- **Music:** what plays / what stops

| t (s) | Element | Mechanic | Ease, duration |
| --- | --- | --- | --- |
| 0.10 | input bar | rise + scale | expo.out 0.7 |
| 0.55–2.30 | typed line | character typing | set per char |
| 2.50 | send button | press + pulse ring | power2.in 0.08 → back.out(3) 0.3 |
| … | | | |

### Act 2 · …

(repeat)

## Part 4 — self-check before coding

- [ ] Every on-screen line has a source, or is flagged as invented
- [ ] ≥ 2 acts depict a real product behaviour
- [ ] ≥ 8 distinct mechanics across the table
- [ ] ≥ 3 distinct transitions; at most one plain crossfade
- [ ] One persistent element crosses at least one act boundary
- [ ] Exactly one pull-back in the whole film
- [ ] The final landing (stamp / collapse / lockup) is on a downbeat
- [ ] The real logo file is used; nothing is redrawn as a primitive
- [ ] The logo appears in the lockup only — no corner mark through the film
- [ ] The end frame has no type baked in, or it is used as the lockup without a second title; the product doesn't cross any type; lockup is one group on the product's axis

## Worked example (an office-automation agent, 15s, light palette)

Sources: selling line "hand the repetitive work to the agent; you think and make
the call"; behaviours: one-sentence request → auto breakdown → runs in the cloud
with the laptop shut → syncs to phone and web → delivers files.

Metaphor: **the last verb of the selling line becomes a stamp that slams on the
final downbeat.** Palette: warm paper `#F4F2ED`, ink `#15171C`, one blue `#2B5CFF`.
Grid: 0.5s (six pipeline steps, one per beat).

| Act | Time | Product behaviour | Camera | Exit | Events |
| --- | --- | --- | --- | --- | --- |
| 1 Request | 0–3.0 | a sentence typed into the input, sent | settle 1.04→1.0 | **persistent hand-off**: bar docks top-left | bar rise · kicker · 30 chars typed · caret · send press · pulse ring · ghost word drift · dot grid drift · glow breathe |
| 2 Breakdown | 3.0–6.0 | six steps light up, one per beat | track slides −1460px | **lateral whip** | headline · track fill · 6 × (node rise, fill pop, colour, status text) · bar exits |
| 3 Overnight | 6.0–9.5 | laptop closes; cloud keeps running; phone and web sync | slow push 1.0→1.035 | **zoom-through** the web window | lateral push-in · headline · sub · lid hinge · night tint · 2 stroke draws · cloud pop · cloud breathe · phone rise · web slide · shared progress count · clock 23:40→08:52 |
| 4 Delivered | 9.5–12.5 | report, deck and sheet arrive; a "sent" notification | settle 0.88→1.0, slow push | **collapse to point** | headline · 3 × 3D card fly-in · 6 chart bars grow · 18 cells fade · notification pop |
| 5 Sign-off | 12.5–15 | — | none, then a final slow push | — | line 1 · line 2 with gap · **stamp slam** · ink spread · 3-step shake · rule draw · logo lockup · CTA |

That is 97 non-filler tweens, 12 mechanics, 4 non-crossfade transitions, 19 eases — see
`examples/office-agent/` for the complete source.

- [ ] `assets.md` lists the current logo for this exact product (five-point check
      answered) and ≥ 2 official images with source URLs, and the shot list says
      which act uses each one.

## Zone map (one row per act, before any CSS — see layout.md)

| Act | Headline zone | Product zone | Accent / logo zone | Empty on purpose |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
