#!/usr/bin/env python3
"""Rendered-film audit: measures what the viewer actually sees.

film_audit.py counts code. Code counts can be met with filler (a headline that
breathes, three identical ripples). This script looks at the rendered pixels
instead, which cannot be padded:

  coverage   share of the frame that differs from the background, per frame
  motion     how much of the frame changes between frames 1/10 s apart
  dead time  longest stretch where almost nothing moves
  busy acts  per act: median coverage

usage: frame_audit.py film.mp4 [--fps 10]
"""
import subprocess, sys, statistics, argparse, os

W, H = 192, 108

def frames(path, fps):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf",
           f"fps={fps},scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = W * H
    return [raw[i:i + n] for i in range(0, len(raw) - n + 1, n)]

def background(fr):
    # most common brightness on the frame border = the ground colour
    hist = [0] * 256
    for x in range(W):
        hist[fr[x]] += 1; hist[fr[(H - 1) * W + x]] += 1
    for y in range(H):
        hist[fr[y * W]] += 1; hist[fr[y * W + W - 1]] += 1
    return max(range(256), key=lambda v: hist[v])

def coverage(fr):
    bg = background(fr)
    return sum(1 for p in fr if abs(p - bg) > 18) / len(fr)

def detail(fr):
    # share of pixels on a visible edge: how much is actually drawn, regardless of ground colour
    n = 0
    for y in range(0, H - 1):
        r = y * W
        for x in range(0, W - 1):
            p = fr[r + x]
            if abs(p - fr[r + x + 1]) > 14 or abs(p - fr[r + W + x]) > 14: n += 1
    return n / ((W - 1) * (H - 1))

def motion(a, b):
    return sum(1 for p, q in zip(a, b) if abs(p - q) > 10) / len(a)

ACTS = [(0, 3), (3, 6), (6, 9.5), (9.5, 12.5), (12.5, 99)]

# Calibrated on six renders (2026-10): accepted films sit at detail 0.07-0.10,
# coverage 0.08-0.43, motion 0.03-0.05; rejected ones at detail 0.01-0.06,
# coverage 0.01-0.06, motion 0.00-0.02. These floors sit between the two groups.
FLOORS = {
    "median coverage": 0.065,         # share of frame that is not bare ground
    "median detail": 0.065,           # share of pixels on a visible edge
    "median motion": 0.025,           # share of frame changing per 0.1s
    "longest still stretch (s)": 2.5,
    "thinnest act coverage": 0.04,    # no act may be a near-empty frame
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--fps", type=float, default=10)
    a = ap.parse_args()
    fs = frames(a.video, a.fps)
    dt = 1 / a.fps
    cov = [coverage(f) for f in fs]
    det = [detail(f) for f in fs]
    mot = [motion(fs[i], fs[i + 1]) for i in range(len(fs) - 1)]
    # skip the first and last 0.5s: fade-in from black and the held end frame are allowed
    skip = int(0.5 * a.fps)
    body_cov = cov[skip:len(cov) - skip] or cov
    body_mot = mot[skip:len(mot) - skip] or mot
    longest = run = 0
    for m in body_mot:
        run = run + 1 if m < 0.01 else 0
        longest = max(longest, run)
    acts = []
    for s, e in ACTS:
        seg = [c for i, c in enumerate(cov) if s <= i * dt < e]
        if seg: acts.append(statistics.median(seg))
    res = {
        "median coverage": statistics.median(body_cov),
        "median detail": statistics.median(det[skip:len(det) - skip] or det),
        "median motion": statistics.median(body_mot),
        "longest still stretch (s)": longest * dt,
        "thinnest act coverage": min(acts),
    }
    print(f"frame_audit  {a.video}  ({len(fs) * dt:.1f}s @ {a.fps:g}fps)\n")
    failed = []
    for k, v in res.items():
        lim = FLOORS[k]
        ok = v <= lim if k == "longest still stretch (s)" else v >= lim
        sign = "<=" if k == "longest still stretch (s)" else ">="
        print(f"  {'PASS' if ok else 'FAIL'}  {k:30s} {v:6.3f}   {sign} {lim}")
        if not ok: failed.append(k)
    print("\n  per-act median coverage: " + " / ".join(f"{c:.2f}" for c in acts))
    print("  coverage timeline (0.5s): " + " ".join(f"{int(c*100):02d}" for c in cov[::int(a.fps / 2) or 1]))
    if failed:
        print(f"\n  {len(failed)} failed: {', '.join(failed)}")
        print("  the frame is too empty or too still — add product on screen, depth layers, persistent objects; do not deliver")
        _stamp(a.video, 'frame_audit', False, '')
        sys.exit(1)
    _stamp(a.video, 'frame_audit', True, '0 failed')
    print("\n  0 failed")


def _project_root(p):
    """Nearest ancestor that contains a film/ directory (the film project)."""
    d = os.path.abspath(p if os.path.isdir(p) else os.path.dirname(p))
    while True:
        if os.path.isdir(os.path.join(d, 'film')):
            return d
        up = os.path.dirname(d)
        if up == d:
            return None
        d = up


def _stamp(path, name, ok, summary):
    """Leave <project>/.gates/<name>.ok on pass, remove it on fail.
    score_lib checks for both stamps before it writes the score."""
    root = _project_root(path)
    if not root:
        return
    g = os.path.join(root, '.gates')
    os.makedirs(g, exist_ok=True)
    f = os.path.join(g, name + '.ok')
    if ok:
        open(f, 'w').write(summary + '\n')
    elif os.path.exists(f):
        os.remove(f)


if __name__ == "__main__":
    main()
