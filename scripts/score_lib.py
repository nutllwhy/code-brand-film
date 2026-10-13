"""score_lib — a tiny orchestra for code-generated brand films.

Additive synthesis + FFT-convolution reverb + a soft-clip master. No samples,
no external audio files, no licensing: everything written here is original.

Why it exists
-------------
A 15-second film needs music that lands on its cuts. Stock tracks don't know
where the cuts are, and hunting for one costs more time than writing the part.
So the score is authored in the same units as the picture — seconds — using the
film's own cut list as the grid.

Basic use
---------
    import score_lib as sl

    B = 0.5                                   # seconds per beat (120 BPM)
    S = sl.Score(dur=15.0, seed=31)

    S.place(S.pad(['G2', 'D3', 'B3'], 3.2, att=1.0, rel=0.5), 0.0, send=0.55)
    for k in range(6):                        # one step per beat
        S.place(S.kick(), 3.0 + k * B)
        S.place(S.pluck(S.hz('A4')), 3.0 + k * B + 0.35, pan=0.25)
    S.place(S.boom(), 13.5)
    S.write('score.wav')

The only scheduling call is `place(sig, t, pan, gain, send)`. Everything else
is a plain function returning a float array — write your own with the same
shape and it drops straight in.

Two rules that keep a score from sounding mechanical
----------------------------------------------------
1. Derive the beat from the picture, not the other way round. Count the frames
   between two cuts, divide, and write that number into the header comment. If
   the film's grid is 0.62 s, do not use 0.5 s because it is rounder.
2. Take the drums out somewhere. A score that is loud from 0 to 15 s has no
   shape; the middle act should thin to pads and one lonely sound, so the
   final downbeat has somewhere to land.

Mixing is a separate step — see SKILL.md. This module deliberately does not do
loudness normalization, because ffmpeg's `loudnorm` does it better and the SFX
layer is added there anyway.
"""
from __future__ import annotations

import os
import wave

import numpy as np

SR = 48000

_NOTE_OFFSET = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5,
    'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11,
}


def hz(note: str) -> float:
    """'A4' -> 440.0. Equal temperament, A4 = 440 Hz."""
    name, octave = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((_NOTE_OFFSET[name] + 12 * (octave + 1) - 69) / 12)


def onepole_lp(x: np.ndarray, fc) -> np.ndarray:
    """One-pole lowpass. `fc` may be a scalar (fixed cutoff) or an array of the
    same length as `x` (a sweep — that's how the riser works)."""
    a = np.exp(-2 * np.pi * np.asarray(fc) / SR)
    a = np.broadcast_to(a, x.shape)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


class Score:
    """One film's score. Build it with `place`, write it with `write`."""

    def __init__(self, dur: float = 15.0, seed: int = 31):
        self.dur = float(dur)
        self.n = int(SR * self.dur)
        self.layers = None          # set by write()/master() if the caller wants it
        self.bus = np.zeros((2, self.n))
        self.reverb_send = np.zeros((2, self.n))
        self.rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------ core
    def t(self, d: float) -> np.ndarray:
        """A time axis of `d` seconds, used by every instrument."""
        return np.arange(int(d * SR)) / SR

    def noise(self, d: float) -> np.ndarray:
        return self.rng.standard_normal(int(d * SR))

    def place(self, sig: np.ndarray, at: float, pan: float = 0.0,
              gain: float = 1.0, send: float = 0.3) -> None:
        """Add `sig` to the mix starting at `at` seconds.

        pan  -1 hard left, +1 hard right (equal-power).
        send  0..1 into the reverb bus. Raise it for anything you want to sound
              far away (bells, pads); keep it low for kicks and steps, which
              need to feel close.
        """
        i = int(at * SR)
        if i >= self.n:
            return
        sig = sig[: self.n - i] * gain
        lg = np.cos((pan + 1) * np.pi / 4)
        rg = np.sin((pan + 1) * np.pi / 4)
        self.bus[0, i:i + len(sig)] += sig * lg
        self.bus[1, i:i + len(sig)] += sig * rg
        if send:
            self.reverb_send[0, i:i + len(sig)] += sig * lg * send
            self.reverb_send[1, i:i + len(sig)] += sig * rg * send

    # ----------------------------------------------------------- instruments
    # Felt piano: 5 slightly inharmonic partials plus a hammer transient.
    # Reads as "expensive" rather than "synth" — good for the opening and the
    # final chord.
    def felt_piano(self, f: float, d: float = 2.6, vel: float = 1.0) -> np.ndarray:
        t = self.t(d)
        partials = [(1, 1.0, 2.2), (2, 0.42, 3.4), (3, 0.18, 5.0),
                    (4, 0.08, 7.0), (5.02, 0.04, 9.0)]
        s = sum(a * np.sin(2 * np.pi * f * m * t * (1 + 0.0004 * m * m)) * np.exp(-t * dec)
                for m, a, dec in partials)
        hammer = self.rng.standard_normal(len(t)) * np.exp(-t * 90) * 0.05
        return (s * np.minimum(1, t / 0.006) + hammer) * vel * 0.32

    # FM bell. Long and floaty; the arrival sound for "something happened".
    def bell(self, f: float, d: float = 1.8, vel: float = 1.0) -> np.ndarray:
        t = self.t(d)
        mod = np.sin(2 * np.pi * f * 3.5 * t) * 1.6 * np.exp(-t * 4)
        s = np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 2.6) * np.minimum(1, t / 0.003)
        return s * vel * 0.16

    # Short plucked string. The workhorse for "one thing per beat" sequences.
    def pluck(self, f: float, d: float = 1.0, vel: float = 1.0) -> np.ndarray:
        t = self.t(d)
        s = (np.sin(2 * np.pi * f * t)
             + 0.5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 12)
             + 0.25 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 20))
        return s * np.exp(-t * 5.5) * np.minimum(1, t / 0.002) * vel * 0.2

    # Marimba-ish mallet: strong 4th partial, very fast decay.
    def marimba(self, f: float, d: float = 0.9, vel: float = 1.0) -> np.ndarray:
        t = self.t(d)
        s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 6)
             + 0.35 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 22)
             + 0.12 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t * 40))
        return s * np.minimum(1, t / 0.002) * vel * 0.22

    # Sustained bed. `notes` is a chord as note names; detuning creates the
    # width, so pass 4-6 notes rather than doubling one.
    def pad(self, notes, d: float, att: float = 1.2, rel: float = 1.2,
            bright: float = 1.0, vel: float = 1.0) -> np.ndarray:
        t = self.t(d)
        s = np.zeros(len(t))
        for n in notes:
            f = hz(n)
            for det in (-0.07, 0.0, 0.065):
                ff = f * (1 + det / 100 * 1.5)
                ph = self.rng.uniform(0, 2 * np.pi)
                s += (np.sin(2 * np.pi * ff * t + ph)
                      + 0.28 * bright * np.sin(2 * np.pi * 2 * ff * t + ph)
                      + 0.10 * bright * np.sin(2 * np.pi * 3 * ff * t + ph))
        env = np.minimum(1, t / att) * np.clip(np.minimum(1, (d - t) / rel), 0, 1)
        breathe = 1 + 0.08 * np.sin(2 * np.pi * 0.35 * t)
        return s * env * breathe * vel * 0.045 / max(1, len(notes) / 4)

    # Sine sub. This is what makes the mix feel like it has a floor.
    def sub(self, f: float, d: float, vel: float = 1.0) -> np.ndarray:
        t = self.t(d)
        s = np.sin(2 * np.pi * f * t) + 0.15 * np.sin(2 * np.pi * 2 * f * t)
        env = np.minimum(1, t / 0.02) * np.clip(np.minimum(1, (d - t) / 0.15), 0, 1)
        return s * env * vel * 0.22

    # Pitch-swept kick with a click on top. Sits at the front of the mix.
    def kick(self, vel: float = 1.0) -> np.ndarray:
        t = self.t(0.55)
        f = 46 + 110 * np.exp(-t * 28)
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = np.sin(ph) * np.exp(-t * 6.5) + self.noise(0.55)[: len(t)] * np.exp(-t * 160) * 0.15
        return np.tanh(s * 1.6) * vel * 0.5

    # Closed hi-hat: differenced noise is a cheap highpass.
    def hat(self, vel: float = 1.0) -> np.ndarray:
        t = self.t(0.09)
        n = self.noise(0.09)[: len(t)]
        n = n - np.concatenate([[0], n[:-1]])
        return n * np.exp(-t * 55) * vel * 0.05

    # Clap: three offset noise bursts. Reads as "groove" without a snare.
    def clap(self, vel: float = 1.0) -> np.ndarray:
        t = self.t(0.25)
        n = self.noise(0.25)[: len(t)]
        n = n - onepole_lp(n, 1200)
        env = (np.exp(-t * 30)
               + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
               + 0.4 * np.exp(-np.maximum(t - 0.024, 0) * 25) * (t > 0.024))
        return n * env * vel * 0.12

    # Tick / clock / keystroke. Half inaudible on purpose — it sells detail.
    def tick(self, vel: float = 1.0, f: float = 3800.0) -> np.ndarray:
        t = self.t(0.03)
        return np.sin(2 * np.pi * f * t) * np.exp(-t * 260) * vel * 0.09

    # A door closing / a lid shutting. Short, low, no pitch centre.
    def thud(self, vel: float = 1.0) -> np.ndarray:
        t = self.t(0.4)
        f = 70 + 60 * np.exp(-t * 30)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * vel * 0.45

    # The big arrival. Use once, at the film's most important frame.
    def boom(self, vel: float = 1.0, d: float = 3.0) -> np.ndarray:
        t = self.t(d)
        f = 38 + 50 * np.exp(-t * 6)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.4)
        noise = onepole_lp(self.noise(d)[: len(t)], 900) * np.exp(-t * 9) * 0.25
        return np.tanh((s + noise) * 1.4) * vel * 0.55

    # Band-swept noise ramp. The transition sound — put it just before a cut.
    def riser(self, d: float, f0: float = 200, f1: float = 3200,
              vel: float = 1.0) -> np.ndarray:
        t = self.t(d)
        fc = f0 * (f1 / f0) ** (t / d)
        y = onepole_lp(self.noise(d)[: len(t)], fc)
        y = y - onepole_lp(y, fc * 0.35)
        tone_f = 110 * 2 ** (2.5 * t / d)
        tone = np.sin(2 * np.pi * np.cumsum(tone_f) / SR) * 0.25
        return (y * 2.2 + tone) * (t / d) ** 2.2 * vel * 0.32

    # A chord that grows instead of being struck. Pairs with a riser.
    def swell(self, notes, d: float, vel: float = 1.0) -> np.ndarray:
        t = self.t(d)
        return self.pad(notes, d, att=0.01, rel=0.01, bright=1.6) * (t / d) ** 2.5 * vel * 3.0

    # ---------------------------------------------------------------- output
    def reverb(self, x: np.ndarray, secs: float = 2.6) -> np.ndarray:
        """FFT convolution with a synthetic hall impulse.

        The IR is noise decayed exponentially and lowpassed — no external file,
        so the reverb is as original as the notes. Decay rate sets the room
        size: 3.2 is a medium hall. Lower it for a small room.
        """
        t = self.t(secs)
        ir = self.noise(secs)[: len(t)] * np.exp(-t * 3.2)
        ir = onepole_lp(ir, 5200)
        ir[: int(0.018 * SR)] = 0                    # pre-delay
        ir /= np.sqrt(np.sum(ir ** 2))
        n = len(x) + len(ir)
        nfft = 1 << (n - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
        return y

    def mix(self, wet: float = 0.55, drive: float = 1.2,
            peak: float = 0.89, fade_out: float = 0.45, fade_in: float = 0.02,
            width: int = 240) -> np.ndarray:
        """Reverb return + fades + soft clip + normalize. Returns (2, n) float.

        Stereo width on the reverb comes from offsetting the right tail by a few
        hundred samples — cheaper than a true stereo IR and it does the job.
        """
        out = self.bus.copy()
        out[0] += self.reverb(self.reverb_send[0]) * wet
        out[1] += self.reverb(np.roll(self.reverb_send[1], width)) * wet
        f = np.ones(self.n)
        fo = int(fade_out * SR)
        if fo:
            f[-fo:] = np.linspace(1, 0, fo) ** 1.5
        fi = int(fade_in * SR)
        if fi:
            f[:fi] = np.linspace(0, 1, fi)
        out *= f
        out = np.tanh(out * drive) / np.tanh(drive)
        m = np.max(np.abs(out))
        if m:
            out /= m / peak
        self.layers = out
        return out

    def write(self, path: str, **kwargs) -> str:
        """Write 16-bit 48 kHz stereo WAV. Returns the path."""
        path = os.path.abspath(path)
        _check_gates(path)
        out = self.mix(**kwargs)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        pcm = (out.T * 32767).astype('<i2')
        with wave.open(path, 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        print('wrote', path, f'({self.dur:g}s)')
        return path


def _check_gates(path):
    """Scoring is the last step. If the picture has not passed all three audits,
    stop: no score is written, so there is nothing to mux. Music on an
    under-built film is wasted work."""
    d = os.path.dirname(path)
    root = None
    while True:
        if os.path.isdir(os.path.join(d, 'film')):
            root = d
            break
        up = os.path.dirname(d)
        if up == d:
            break
        d = up
    if not root:
        return
    missing = [n for n in ('film_audit', 'layout_audit', 'frame_audit')
               if not os.path.exists(os.path.join(root, '.gates', n + '.ok'))]
    if missing:
        import sys
        bar = '!' * 72
        sys.stderr.write(f"""
{bar}
  NOT READY TO SCORE — the picture has not passed: {', '.join(missing)}
  run  python3 <skill>/scripts/film_audit.py  film/index.html
  and  node <skill>/scripts/layout_audit.mjs film/index.html
  and  python3 <skill>/scripts/frame_audit.py film/renders/silent.mp4
  All must print "0 failed". A film that fails them is not deliverable,
  however good the music is. Go back to the timeline, not to the mix.
  score.wav was NOT written.
{bar}

""")
        raise SystemExit(1)
