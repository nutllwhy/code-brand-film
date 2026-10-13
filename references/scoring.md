# Scoring a film in code

> **Score last.** Only write the score after `scripts/film_audit.py`,
> `scripts/layout_audit.mjs` and `scripts/frame_audit.py` all print `0 failed`. `score_lib.write()` prints a loud
> warning if they have not — music does not rescue an under-built picture.

A 15-second film needs music that lands on its cuts. Stock music does not know
where the cuts are, and auditioning tracks takes longer than writing the part.
So the score is produced the same way the film is: as code, in the picture's own
units of time.

`scripts/score_lib.py` is the instrument library — additive synthesis, an
FFT-convolution reverb, and a soft-clip master. It has no samples and no external
audio files, so the result is original and free of licensing risk. Read its
module docstring for the API; this file is the workflow around it.

## Step 1 — measure the picture's grid

Do not pick a tempo and then fit the picture to it. Count the film's cuts.

Two cuts at `t0` and `t1`: the beat must divide the gap between them. From the
film A the verb carousel changed every 0.62s → 96.8 BPM. From film B the
six pipeline steps landed one per 0.5s → 120 BPM.

Practical procedure: pick the act with the most repeated events (a step per
beat), measure the spacing between two of them in the timeline, and use that.
Then set every act boundary on an integer multiple of the beat, and write the
number into the score's header comment so the next person can check it.

If the film's events are irregular, keep the tempo but let the *arrangement*
follow the picture — hit the accents with a bell or a boom at the exact frames,
and keep the pulse underneath.

## Step 2 — plan energy per act, before writing a note

Write down one line per act: what is playing, and what stops. A blank in this
table is a hole in the film.

| Act | Film B (15s) |
| --- | --- |
| 1 · the request (0–3s) | airy pad, typing ticks at ~17 ms intervals, one bell on send, riser into the cut |
| 2 · breakdown (3–6s) | groove enters: kick + hat + clap on beat; one pluck per node, each 0.35s after its beat |
| 3 · runs overnight (6–9.5s) | drums thin to hats only; accelerating clock ticks; three mallets one per device |
| 4 · delivered (9.5–12.5s) | full groove, brighter chords, bell on "sent", swell into the turn |
| 5 · sign-off (12.5–15s) | bar 1 nearly empty; riser + swell; **boom + sub + big chord at the stamp**; bell tail |

The rule that matters most: **take the drums out somewhere**. A score at full
intensity from 0 to 15s has no shape, and the final downbeat has nothing to land
against. The third act (the turn) is the usual place to strip it back.

## Step 3 — write the arrangement

Copy `scripts/score_template.py` and fill in the act sections. Two habits worth
keeping:

- **Comment every placement with the picture event it serves.** `# lid shuts`,
  `# on the check`, `# sent`. Six months later the comment is the only thing that
  explains why a bell is at 7.0s.
- **Let repeated picture events be a repeated musical figure.** In film B the
  six pipeline steps are an ascending pluck dyad, `G4 A4 B4 D5 E5 G5` — the
  listener hears the progress without being told.

Run it with the project's venv, not the system Python:

```bash
cd <film-project> && python3 -m venv .venv && .venv/bin/pip install numpy
perl -e 'alarm 200; exec @ARGV' .venv/bin/python audio/score.py
```

numpy on the system interpreter is usually blocked by PEP 668. The synthesis is
pure numpy and runs in a couple of seconds for 15s of audio.

## Step 4 — layer the SFX and normalize

The score is the bed; a handful of effects create the impacts. Any royalty-free SFX
library works; the HyperFrames `media-use` skill ships one (
`whoosh-cinematic.mp3`, `whoosh-short.mp3`, `sparkle.mp3`, `impact-bass-1.mp3`,
`riser.mp3`, `chime.mp3`, `click.mp3`, `typing.mp3`, …).

Mux them with ffmpeg in one filter graph. The pattern that works — `adelay` in
milliseconds to place each hit, `amix` with `normalize=0` (the default `1`
divides everything by the input count and quietly ruins the balance), then
`loudnorm` on the sum:

```bash
S=${SFX_DIR:?point SFX_DIR at a folder of royalty-free sfx}
ffmpeg -y -v error -i audio/score.wav \
  -i $S/whoosh-short.mp3 -i $S/whoosh-cinematic.mp3 -i $S/impact-bass-1.mp3 \
  -filter_complex "\
[1:a]aresample=48000,volume=0.35,adelay=2400|2400[a1];\
[2:a]aresample=48000,atrim=2.2:3.4,asetpts=PTS-STARTPTS,afade=t=in:d=0.15,afade=t=out:st=0.9:d=0.3,volume=0.5,adelay=8690|8690[a2];\
[3:a]aresample=48000,volume=0.7,adelay=13400|13400[a3];\
[0:a][a1][a2][a3]amix=inputs=4:normalize=0:duration=first,atrim=0:15,afade=t=out:st=14.5:d=0.5,loudnorm=I=-14:TP=-1.0:LRA=9[out]" \
  -map "[out]" -ar 48000 audio/mix.wav
```

**No SFX library? Synthesise the hits.** Every effect a brand film needs can
be a few lines of numpy, and then each one sits exactly on its frame: a
pitch-dropping sine for the sub hit (55 Hz × (1 + 2.5·e^(−30t))), noise through
a band that sweeps up for a whoosh (pan it the direction the picture moves), a
two-click high-passed noise burst for a shutter, a 2–3 kHz sine blip for a
button press, a ring of inharmonic partials (1, 2.76, 5.4) for the bell. Start
the score file by copying the film's event times from the timeline into a
comment and place every hit from that list — that list *is* the arrangement.

**Hit true peak exactly: two-pass loudnorm.** One pass overshoots (a real mix
measured −13.3 LUFS / −0.5 dBFS after a single pass at TP=−1). Measure first,
then apply with `linear=true`:

```bash
J=$(ffmpeg -hide_banner -i in.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -v error -i in.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" -ar 48000 audio/mix.wav
```
That lands at about −13.8 LUFS / −1.0 dBFS.

`loudnorm` needs `atrim` before it — it buffers and will stretch the output if it
never sees the end. Every fx input needs `aresample=48000`, because the library
files are 44.1 kHz and mismatched rates shift `adelay`.

Then mux onto the silent picture — video is copied, never re-encoded:

```bash
ffmpeg -y -v error -i film/renders/silent.mp4 -i audio/mix.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest film/renders/final.mp4
```

## Step 5 — verify what you cannot hear

You cannot listen to the output. Verify structurally instead, and say so in the
delivery rather than claiming it sounds good.

```bash
# integrated loudness and true peak — expect about -14 LUFS, peak ≤ -1 dBFS
ffmpeg -hide_banner -i audio/mix.wav -af ebur128=peak=true -f null - 2>&1 | grep -E " I:|Peak:"

# waveform: does it have shape, or is it a flat wall? does it clip?
ffmpeg -y -v error -i audio/mix.wav -filter_complex "showwavespic=s=1600x400:colors=#F5B860" -frames:v 1 audio/wave.png

# spectrum: clean harmonics, or broadband hash from a synthesis bug?
ffmpeg -y -v error -i audio/mix.wav -lavfi showspectrumpic=s=1600x600 -frames:v 1 audio/spec.png
```

Read them honestly: the waveform shows whether the arrangement has dynamics and
whether anything is clipping; the spectrum shows whether a riser or a reverb is
adding noise where it should not. Both are silent-frame checks, not a
substitute for someone's ears — hand the file over and ask which second felt
wrong, so a revision can be surgical.

## What "synthetic-sounding" usually means, and the fixes

- **Everything on the same grid with no human offset.** Nudge repeated elements
  off the beat by 5–30 ms, and vary velocity (`0.6 + 0.4 * ((i * 7) % 5) / 5`).
- **No low end.** Add `sub()` under chord changes; a pad alone has no floor.
- **Reverb on everything equally.** Dry, close sounds (kick, steps, ticks) next
  to wet, distant ones (bells, pads) is what creates depth. Use the `send`
  parameter for this.
- **A chord that never changes.** Change harmony at act boundaries — a pedal
  point for 15 seconds wears out fast.
- **Ending on nothing.** The last 1.5s needs a deliberate resolution: a boom, a
  big chord, and a bell tail. Ninety percent of the perceived production value is
  in the final two seconds.
