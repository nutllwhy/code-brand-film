"""Score template — copy this next to your film and fill it in.

    cp scripts/score_template.py <film-project>/audio/score.py
    cd <film-project> && python3 -m venv .venv && .venv/bin/pip install numpy
    perl -e 'alarm 200; exec @ARGV' .venv/bin/python audio/score.py

Before you write a note: fill in MEASUREMENTS and ACT_PLAN below from the
picture's real timeline. A score written against a guessed tempo fights the film
for its whole length.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_lib as sl  # noqa: E402

# ==========================================================================
# MEASUREMENTS — read these off the rendered picture, do not invent them.
#
# Where the cuts are:      render the silent film, open the timeline, note the
#                          act boundaries and the most-repeated event spacing.
# Beat:                    the gap between two repeated events.
# Key:                     pick one, and change harmony at act boundaries.
# ==========================================================================
DUR = 15.0                 # film length, seconds
BEAT = 0.5                 # seconds per beat → 120 BPM.  (0.62 → 96.8 BPM)
KEY = 'G'                  # tonic. G major / E minor.
SEED = 31                  # keeps the noise deterministic across renders

# Act boundaries, copied from the picture. Every entry below must be one of
# these times or an integer number of beats after one.
ACT1, ACT2, ACT3, ACT4, ACT5 = 0.0, 3.0, 6.0, 9.5, 12.5

S = sl.Score(dur=DUR, seed=SEED)
B = BEAT


# ==========================================================================
# ACT 1 — the hook. Slow, one idea, nothing rhythmic yet.
# Picture: <what happens>
# ==========================================================================
S.place(S.pad([f'{KEY}2', 'D3', 'B3', 'F#4', 'A4'], 3.2, att=1.0, rel=0.5, bright=0.8),
        ACT1, send=0.55)
S.place(S.marimba(sl.hz('D5'), vel=0.6), ACT1 + 0.1, pan=0.2, send=0.5)

# Typing: one tick per character, 5-30 ms off the grid, velocity varying.
# Line up TYPING_START / TYPING_END with the on-screen typing animation, and
# N_CHARS with the actual character count of the line.
TYPING_START, TYPING_END, N_CHARS = 0.55, 2.30, 30
step = (TYPING_END - TYPING_START) / N_CHARS
for i in range(N_CHARS):
    if i % 2 == 0:                                    # every other key
        S.place(S.tick(vel=0.6 + 0.4 * ((i * 7) % 5) / 5),
                TYPING_START + i * step + (i % 3) * 0.004,
                pan=-0.2 + 0.4 * ((i * 3) % 7) / 7, send=0.15)

# A rising melodic figure under the typing, then the send.
for t0, n in [(0.6, 'B4'), (1.1, 'D5'), (1.6, 'A4'), (2.1, 'G4')]:
    S.place(S.marimba(sl.hz(n), vel=0.55), t0, pan=0.3, send=0.5)
S.place(S.bell(sl.hz('B5'), d=1.4, vel=0.9), 2.5, pan=0.2, send=0.6)
S.place(S.riser(0.5, 400, 8000, vel=0.7), 2.5, send=0.3)


# ==========================================================================
# ACT 2 — development. Rhythm enters, one event per beat.
# Picture: <what happens>
# ==========================================================================
# Harmonies change at act boundaries, not on a fixed bar count.
S.place(S.pad(['E2', 'B2', 'G3', 'D4', 'F#4'], 1.5, att=0.05, rel=0.4, bright=1.2),
        ACT2, send=0.4)
S.place(S.pad(['C3', 'G3', 'B3', 'E4', 'G4'], 1.5, att=0.05, rel=0.4, bright=1.2),
        ACT2 + 1.5, send=0.4)
S.place(S.sub(sl.hz('E2'), 1.5, vel=0.8), ACT2)          # the floor under the pad

# One picture event per beat. N_EVENTS = however many steps the act has.
N_EVENTS = 6
for k in range(N_EVENTS):
    t0 = ACT2 + k * B
    S.place(S.kick(vel=0.9), t0, send=0.03)               # dry: kick stays close
    S.place(S.hat(vel=0.8), t0 + 0.25, pan=0.3, send=0.08)
    if k % 2 == 1:
        S.place(S.clap(vel=0.9), t0, pan=-0.1, send=0.25)

# A repeated figure so the listener hears progress: ascending thirds, one per
# beat, 0.35s after the beat so it reads as "the step completing".
for k, n in enumerate(['G4', 'A4', 'B4', 'D5', 'E5', 'G5']):
    S.place(S.pluck(sl.hz(n), vel=0.95), ACT2 + k * B + 0.35, pan=0.25, send=0.35)
    S.place(S.marimba(sl.hz(n) * 2, vel=0.35), ACT2 + k * B + 0.35, pan=-0.3, send=0.4)
S.place(S.riser(0.45, 600, 9000, vel=0.6), ACT2 + 2.55, send=0.25)


# ==========================================================================
# ACT 3 — the turn. THE DRUMS COME OUT HERE. This is the shape of the film.
# Picture: night falls / the work keeps running / the state changes
# ==========================================================================
S.place(S.pad(['A2', 'E3', 'G3', 'C4', 'E4'], 1.7, att=0.1, rel=0.5, bright=0.7),
        ACT3, send=0.6)
S.place(S.pad(['F2', 'C3', 'A3', 'E4', 'G4'], 1.9, att=0.3, rel=0.6, bright=0.7),
        ACT3 + 1.6, send=0.6)
S.place(S.sub(sl.hz('A1'), 1.6, vel=0.7), ACT3)

# A single close sound for the state change, and nothing else.
S.place(S.thud(vel=1.0), ACT3 + 1.03, send=0.2)
for k in range(7):                                        # hats only, no kick
    S.place(S.hat(vel=0.55), ACT3 + k * B + 0.25, pan=0.4, send=0.1)

# Time passing: ticks that accelerate. Shrinking the gap is the effect.
t, gap = ACT3 + 0.7, 0.18
while t < ACT3 + 3.1:
    S.place(S.tick(vel=0.5), t, pan=-0.45, send=0.2)
    gap = max(0.05, gap * 0.9)
    t += gap

# One mallet per device, one per beat, panned progressively outward.
S.place(S.bell(sl.hz('E5'), vel=0.7), ACT3 + 1.0, pan=0.1, send=0.7)
S.place(S.marimba(sl.hz('G5'), vel=0.7), ACT3 + 1.5, pan=0.4, send=0.5)
S.place(S.marimba(sl.hz('C6'), vel=0.7), ACT3 + 2.0, pan=0.5, send=0.5)
S.place(S.riser(0.55, 300, 9000, vel=0.9), ACT3 + 2.95, send=0.3)


# ==========================================================================
# ACT 4 — payoff. Everything comes back, brightest of the film.
# Picture: the deliverables arrive
# ==========================================================================
S.place(S.pad(['C3', 'G3', 'B3', 'E4', 'D5'], 1.5, att=0.02, rel=0.4, bright=1.4),
        ACT4, send=0.45)
S.place(S.pad(['D3', 'A3', 'C4', 'F#4', 'E5'], 1.5, att=0.02, rel=0.4, bright=1.4),
        ACT4 + 1.5, send=0.45)
S.place(S.sub(sl.hz('C2'), 1.5, vel=0.85), ACT4)
for k in range(5):
    t0 = ACT4 + k * B
    S.place(S.kick(vel=0.95 if k == 0 else 0.85), t0, send=0.03)
    S.place(S.hat(vel=0.85), t0 + 0.25, pan=0.3, send=0.08)
    S.place(S.hat(vel=0.45), t0 + 0.375, pan=-0.3, send=0.08)
    if k % 2 == 1:
        S.place(S.clap(vel=0.9), t0, send=0.25)
for t0, n in [(ACT4, 'E5'), (ACT4 + 0.5, 'G5'), (ACT4 + 1.0, 'B5')]:
    S.place(S.pluck(sl.hz(n), vel=0.9), t0, pan=0.2, send=0.35)
S.place(S.bell(sl.hz('D6'), d=1.2, vel=0.7), ACT4 + 1.5, pan=0.3, send=0.6)
S.place(S.swell(['G3', 'B3', 'D4', 'A4'], 0.5, vel=0.9), ACT4 + 2.5, send=0.4)


# ==========================================================================
# ACT 5 — landing. Bar 1 is nearly empty, then the hit.
# 90% of the perceived production value is in these last two seconds.
# ==========================================================================
STAMP = ACT5 + 1.0                                        # the film's big frame
S.place(S.pad(['E3', 'B3', 'D4', 'G4'], 1.0, att=0.05, rel=0.3, bright=0.6, vel=0.8),
        ACT5, send=0.6)
S.place(S.riser(0.9, 200, 6000, vel=0.8), ACT5 + 0.1, send=0.3)
S.place(S.swell(['D3', 'A3', 'C4', 'F#4'], 0.85, vel=1.0), ACT5 + 0.15, send=0.4)
S.place(S.boom(vel=1.0, d=2.4), STAMP, send=0.35)
S.place(S.thud(vel=1.0), STAMP, send=0.1)
S.place(S.pad(['G2', 'D3', 'B3', 'F#4', 'A4', 'D5'], 1.5,
              att=0.01, rel=0.9, bright=1.4, vel=1.15), STAMP, send=0.7)
for t0, n, v in [(STAMP, 'G4', 0.8), (STAMP, 'B4', 0.6), (STAMP, 'D5', 0.6),
                 (STAMP + 0.5, 'F#5', 0.6), (STAMP + 0.75, 'A5', 0.55)]:
    S.place(S.felt_piano(sl.hz(n), vel=v), t0, send=0.6)
S.place(S.bell(sl.hz('B5'), d=1.2, vel=0.6), STAMP + 0.5, pan=0.3, send=0.8)


# ==========================================================================
# OUTPUT
# loudnorm happens in the ffmpeg mix step, not here — see references/scoring.md
# ==========================================================================
S.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'score.wav'))
