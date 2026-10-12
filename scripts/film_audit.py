#!/usr/bin/env python3
"""film_audit.py — static quality gate for a code-generated brand film.

    python3 scripts/film_audit.py film/index.html [--duration 15]

Reads the composition's HTML and its timeline script and checks the floors in
references/quality-bar.md: how much is built, how varied the motion is, whether
fonts and logo are real files, whether transitions are all crossfades.

It cannot judge taste. It catches the under-built film — the one that lints
clean, renders without a single broken frame, and still looks like a template.
Exit code 1 if any hard check fails; 0 otherwise. Warnings never fail.

Counts are estimates from source text: a tween inside a `for` / `forEach` loop
is multiplied by the loop's iteration count when that count is a literal or the
length of a literal array; otherwise it is counted once and flagged.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

EASE_RE = re.compile(r'ease\s*:\s*["\']([a-zA-Z0-9.()]+)["\']')
TWEEN_RE = re.compile(r'\btl\.(to|from|fromTo|set)\s*\(')

# signatures of the entrance mechanics in quality-bar.md — (name, regex on script)
MECHANICS = [
    ("line mask reveal", r'yPercent\s*:\s*1\d\d'),
    ("character typing", r'\.ch\b|querySelectorAll\(["\'][^"\']*\.ch["\']'),
    ("letter scatter", r'rotation\s*:\s*d\[\d\]|rotation\s*:\s*-?\d+\s*,\s*opacity\s*:\s*0'),
    ("number count-up", r'textContent\s*=\s*(?:Math\.round|v\b|\()'),
    ("stroke draw", r'stroke-dashoffset|strokeDashoffset'),
    ("3D card fly-in", r'rotationY\s*:|(?<![a-zA-Z])z\s*:\s*-\d'),
    ("hard slam", r'scale\s*:\s*[2-9](?:\.\d+)?\s*,[^}]*\}\s*,\s*\{[^}]*scale\s*:\s*1[^}]*power4\.in'),
    ("scale pop", r'back\.out'),
    ("blur-in", r'filter\s*:\s*["\']blur'),
    ("iris", r'clip-?[pP]ath\s*:\s*["\']circle|clipPath\s*=\s*["\']circle'),
    ("bar/fill growth", r'scale[XY]\s*:\s*0\b'),
    ("pulse ring", r'scale\s*:\s*[3-9](?:\.\d+)?\s*,?\s*duration[^}]*\}|opacity\s*:\s*0\.9\s*,\s*scale\s*:\s*0\.\d'),
    ("ticker roll", r'y\s*:\s*-\s*\d+\s*\*\s*k'),
    ("lateral push-in", r'x\s*:\s*[5-9]\d\d\s*\}\s*,\s*\{\s*x\s*:\s*0'),
    ("3D hinge", r'rotationX\s*:\s*-?\d{2}'),
    ("yoyo breathe", r'yoyo\s*:\s*true'),
    ("camera shake", r'y\s*:\s*-?\d\s*,\s*duration\s*:\s*0\.0\d'),
]

TRANSITIONS = [
    ("persistent hand-off", r'scale\s*:\s*0\.[4-8]\d?\s*,\s*duration[^}]*expo\.inOut'),
    ("zoom-through", r'scale\s*:\s*[3-9](?:\.\d+)?\s*,\s*x\s*:\s*-?\d{3,}'),
    ("logo portal", r'clipPath\s*=\s*["\']circle\(["\']?\s*\+'),
    ("iris", r'clipPath\s*:\s*["\']circle\(\d{3,}px'),
    ("lateral whip", r'x\s*:\s*-\d{3}\s*,\s*opacity\s*:\s*0'),
    ("collapse to point", r'scale\s*:\s*0\.[0-3]\d?\s*,\s*opacity\s*:\s*0'),
]


def strip_comments(js: str) -> str:
    js = re.sub(r'/\*.*?\*/', '', js, flags=re.S)
    return re.sub(r'(?m)^\s*//.*$|(?<=[;{}\s])//[^\n"\']*$', '', js)


def loop_multiplier(js: str, pos: int) -> tuple[int, bool]:
    """Estimate how many times the tween at `pos` runs, from enclosing loops."""
    mult, guessed = 1, False
    depth, i = 0, pos
    while i > 0:
        i -= 1
        c = js[i]
        if c == '}':
            depth += 1
        elif c == '{':
            if depth:
                depth -= 1
                continue
            head = js[max(0, i - 220):i]
            m = re.search(r'for\s*\(\s*var\s+\w+\s*=\s*(\d+)\s*;\s*\w+\s*<=?\s*(\d+)[^)]*\)\s*$', head)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                mult *= max(1, b - a + (1 if '<=' in m.group(0) else 0))
                continue
            m = re.search(r'(\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])\s*\.forEach\s*\(\s*function[^)]*\)\s*$', head)
            if m:
                mult *= max(1, m.group(1).count('"#') + m.group(1).count("'#") or m.group(1).count('[') - 1 or 1)
                continue
            if re.search(r'(?:\.forEach|querySelectorAll\([^)]*\)\.forEach)\s*\(\s*function[^)]*\)\s*$', head) \
                    or re.search(r'for\s*\([^)]*\)\s*$', head) or re.search(r'while\s*\([^)]*\)\s*$', head):
                guessed = True
                mult *= 6
    return mult, guessed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('--duration', type=float, default=None)
    args = ap.parse_args()

    path = os.path.abspath(args.html)
    root = os.path.dirname(path)
    html = open(path, encoding='utf-8').read()
    scripts = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, flags=re.S)
    js = strip_comments('\n'.join(scripts))
    css = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', html, flags=re.S))

    dur = args.duration
    if dur is None:
        m = re.search(r'data-duration="([\d.]+)"', html)
        dur = float(m.group(1)) if m else 15.0
    k = dur / 15.0

    fails, warns, rows = [], [], []

    def check(name, value, floor, ok, note=''):
        rows.append((name, value, floor, 'PASS' if ok else 'FAIL', note))
        if not ok:
            fails.append(name)

    # ---- volume
    tweens, guessed_loops = 0, False
    for m in TWEEN_RE.finditer(js):
        mult, g = loop_multiplier(js, m.start())
        tweens += mult
        guessed_loops |= g
    floor_tw = round(70 * k)
    check('tweens (loops expanded)', tweens, f'>= {floor_tw}', tweens >= floor_tw,
          'loop count estimated' if guessed_loops else '')

    # ---- variety
    eases = sorted(set(EASE_RE.findall(js)))
    check('distinct eases', len(eases), '>= 8', len(eases) >= 8, ', '.join(eases))

    mech = [n for n, rx in MECHANICS if re.search(rx, js)]
    check('entrance mechanics', len(mech), '>= 8', len(mech) >= 8, ', '.join(mech))

    trans = [n for n, rx in TRANSITIONS if re.search(rx, js)]
    check('non-crossfade transitions', len(trans), '>= 2', len(trans) >= 2, ', '.join(trans))

    # ---- structure
    scenes = re.findall(r'class="scene"[^>]*id="([^"]+)"|id="([^"]+)"[^>]*class="scene"', html)
    n_scenes = len(scenes)
    check('acts (.scene)', n_scenes, '>= 4', n_scenes >= 4)
    cams = len(re.findall(r'class="cam"', html))
    check('camera layers (.cam)', cams, '>= 3', cams >= 3)
    cam_moves = len(re.findall(r'tl\.(?:to|fromTo|from)\(\s*["\']#cam\d', js))
    check('camera moves', cam_moves, '>= 8', cam_moves >= 8)

    # events per act: tweens whose start time falls in each act window, bucketed
    starts = [float(x) for x in re.findall(r'\}\s*,\s*(\d+(?:\.\d+)?)\s*\)\s*;', js)]
    if starts:
        edges = [0, 3.0 * k, 6.0 * k, 9.5 * k, 12.5 * k, dur + 0.01]
        buckets = [sum(1 for s in starts if edges[i] <= s < edges[i + 1]) for i in range(5)]
        thin = [i + 1 for i, b in enumerate(buckets) if b < 5]
        check('timed events per act (0-3/3-6/6-9.5/9.5-12.5/12.5-end)', '/'.join(map(str, buckets)), '>= 5 each',
              not thin, f'thin acts: {thin}' if thin else '')

    # ---- depth & chrome
    has_grain = bool(re.search(r'feTurbulence', html))
    check('grain texture', 'yes' if has_grain else 'no', 'yes', has_grain)
    grain_moves = bool(re.search(r'["\']#grain["\'][^;]*steps\(', js))
    if has_grain and not grain_moves:
        warns.append('grain is static — animate it with ease: "steps(N)" over the whole film')
    has_chrome = bool(re.search(r'id="(?:progress|rail)', html)) and len(re.findall(r'class="[^"]*\b(?:corner|chap|barTxt)\b', html)) >= 2
    check('chrome (corner labels + progress rail)', 'yes' if has_chrome else 'no', 'yes', has_chrome)

    # ---- real assets
    faces = re.findall(r'@font-face\s*\{(.*?)\}', css, flags=re.S)
    local_only = [f for f in faces if 'local(' in f and 'url(' not in f]
    url_faces = re.findall(r'url\(["\']?([^"\')]+\.woff2?)["\']?\)', css)
    missing_fonts = [u for u in url_faces if not u.startswith(('http', 'data:')) and not os.path.exists(os.path.join(root, u))]
    check('fonts embedded as files (no local())', f'{len(url_faces)} url / {len(local_only)} local-only',
          '0 local-only, all files exist', not local_only and not missing_fonts and bool(url_faces),
          ('missing: ' + ', '.join(missing_fonts)) if missing_fonts else '')

    imgs = re.findall(r'<img[^>]+src="([^"]+)"', html) + re.findall(r'url\(["\']?(assets/[^"\')]+\.(?:png|jpe?g|svg|webp))', css)
    logo_files = [s for s in imgs if re.search(r'logo|icon|mark|symbol|lockup|wordmark|avatar', s, re.I)]
    # an inline <svg> logo counts if it carries a real path (many commands), not a primitive
    for sid, body in re.findall(r'<svg[^>]*id="([^"]*(?:logo|mark|symbol)[^"]*)"[^>]*>(.*?)</svg>', html, flags=re.S | re.I):
        cmds = sum(len(re.findall(r'[MLCQAZHVSTmlcqazhvst]', d)) for d in re.findall(r'\bd="([^"]+)"', body))
        if cmds >= 12:
            logo_files.append(f'inline svg #{sid}')
        else:
            warns.append(f'#{sid} looks like a primitive shape, not the brand logo — use the real file')
    for m in re.finditer(r'<(?:div|g)[^>]*id="([^"]*logo[^"]*)"[^>]*>\s*(<svg.*?</svg>)', html, flags=re.S | re.I):
        cmds = sum(len(re.findall(r'[MLCQAZHVSTmlcqazhvst]', d)) for d in re.findall(r'\bd="([^"]+)"', m.group(2)))
        if cmds >= 12:
            logo_files.append(f'inline svg in #{m.group(1)}')
    missing_imgs = [s for s in imgs if not s.startswith(('http', 'data:')) and not os.path.exists(os.path.join(root, s))]
    check('real logo file used', ', '.join(sorted(set(logo_files))) or 'none', '>= 1', bool(logo_files),
          ('missing: ' + ', '.join(missing_imgs)) if missing_imgs else '')
    if missing_imgs:
        fails.append('missing image files')

    # ---- known foot-guns
    if re.search(r'stroke-dasharray\s*:', css):
        warns.append('stroke-dasharray in CSS overrides the tween attribute; lines will show dashed from frame 0')
    if re.search(r'Math\.random', js):
        warns.append('Math.random in the timeline: frames are seeked out of order, use a fixed table')
    if re.search(r'tl\.set\([^)]*opacity\s*:\s*0[^)]*\)\s*,\s*0\s*\)', js):
        warns.append('initial hidden state set at t=0 in the timeline; put it in CSS')
    fade_only = len(re.findall(r'tl\.to\(\s*["\']#s\d["\']\s*,\s*\{\s*opacity\s*:\s*[01]\s*,', js))
    if fade_only >= 3:
        warns.append(f'{fade_only} whole-scene opacity fades — most act changes are crossfades')

    # ---- report
    w = max(len(r[0]) for r in rows)
    print(f'film_audit  {os.path.relpath(path)}  ({dur:g}s)\n')
    for name, val, floor, status, note in rows:
        print(f'  {status:4}  {name:<{w}}  {str(val):<14} {floor:<16} {note}')
    if warns:
        print('\n  warnings:')
        for x in warns:
            print('   -', x)
    print(f'\n  {len(fails)} failed' + (': ' + ', '.join(fails) if fails else ' — clear to render'))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
