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
    ("seam open (clip from a line)", r'clip-?[pP]ath\s*:\s*["\']inset\(\s*0(?:px)?\s+\d{3}px\s+0(?:px)?\s+\d{3}px'),
    ("fold on a hinge (two halves)", r'rotationY\s*:\s*-\s*(?:8\d|9\d)\b'),
    ("screen portal", r'clip-?[pP]ath\s*:\s*`?["\']?inset\([^)]*round'),
]

# drawn UI furniture laid over official imagery (focus brackets, capture rings, cursors)
HUD_RE = re.compile(r'class="[^"]*\bcorner\b|id="[^"]*(?:focus|capture|ring|bracket|cursor|reticle)[^"]*"', re.I)


def media_coverage(html: str, dur: float) -> tuple[int, float]:
    """(number of <video> elements, share of runtime with at least one video on screen)."""
    spans = []
    for tag in re.findall(r'<video\b[^>]*>', html):
        a = re.search(r'data-start="([\d.]+)"', tag); d = re.search(r'data-duration="([\d.]+)"', tag)
        if a:
            s0 = float(a.group(1)); spans.append((s0, s0 + (float(d.group(1)) if d else dur - s0)))
    spans.sort(); cov, end = 0.0, 0.0
    for a, b in spans:
        a = max(a, end); b = min(b, dur)
        if b > a:
            cov += b - a; end = b
    return len(spans), cov / dur if dur else 0


def studio_grounds(root: str, html: str):
    """Assets shot on a flat studio ground: [(file, '#rrggbb')]. Needs pillow; ffmpeg for video."""
    try:
        from PIL import Image
    except ImportError:
        return None
    import subprocess, tempfile
    out = []
    files = re.findall(r'<img[^>]+src="(assets/[^"]+\.(?:jpe?g|png|webp))"', html)
    vids = re.findall(r'<video\b[^>]*src="(assets/[^"]+)"', html)
    for f in files + vids:
        p = os.path.join(root, f)
        if not os.path.exists(p) or re.search(r'logo|icon|mark|font', f, re.I):
            continue
        try:
            if f in vids:
                tmp = tempfile.mktemp(suffix='.png')
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.3', '-i', p, '-frames:v', '1', tmp],
                               check=True, capture_output=True)
                im = Image.open(tmp).convert('RGB')
            else:
                im = Image.open(p).convert('RGB')
        except Exception:
            continue
        im.thumbnail((480, 480)); w, h = im.size; px = im.load()
        ring = [px[x, y] for x in range(w) for y in (0, 1, h - 2, h - 1)] + \
               [px[x, y] for y in range(h) for x in (0, 1, w - 2, w - 1)]
        ring.sort(key=sum); mid = ring[len(ring) // 2]
        near = sum(1 for c in ring if max(abs(c[i] - mid[i]) for i in range(3)) <= 4) / len(ring)
        if near >= 0.6:  # most of the border is one flat colour: a studio ground
            out.append((f, '#%02x%02x%02x' % mid))
    return out


def css_colours(css: str):
    cols = set()
    for m in re.findall(r'background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,6})\b', css):
        h = m[1:]
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        cols.add('#' + h.lower())
    return cols


def hexdist(a, b):
    return max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))


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

    # Footage-led: the brand ships its own product motion and the film cuts it.
    # Floors written for code-drawn UI films would push such a film into busy-ness
    # (an accepted footage-led film scored 79 tweens / 6 mechanics / 7 camera moves).
    n_vid, vid_cov = media_coverage(html, dur)
    footage = n_vid >= 2 and vid_cov >= 0.4
    F = dict(tweens=60, mech=5, eases=6, cam=5) if footage else dict(tweens=90, mech=8, eases=8, cam=8)

    def check(name, value, floor, ok, note=''):
        rows.append((name, value, floor, 'PASS' if ok else 'FAIL', note))
        if not ok:
            fails.append(name)

    # ---- volume
    # filler does not count: grain / rail / chapter-number tweens, and any yoyo "breathing"
    # beyond the first three (a headline that bobs is not an event)
    tweens, guessed_loops, filler, yoyos = 0, False, 0, 0
    for m in TWEEN_RE.finditer(js):
        stmt = js[m.start():js.find(';', m.start()) + 1]
        if re.search(r'["\']#(?:grain|rail\w*|chap\w*|progress\w*)["\']', stmt[:60]):
            filler += 1
            continue
        if 'yoyo' in stmt:
            yoyos += 1
            if yoyos > 3:
                filler += 1
                continue
        mult, g = loop_multiplier(js, m.start())
        tweens += mult
        guessed_loops |= g
    floor_tw = round(F['tweens'] * k)
    check('tweens (loops expanded, filler excluded)', tweens, f'>= {floor_tw}', tweens >= floor_tw,
          '; '.join(x for x in ['loop count estimated' if guessed_loops else '',
                                f'{filler} filler not counted' if filler else ''] if x))

    # ---- variety
    eases = sorted(set(EASE_RE.findall(js)))
    check('distinct eases', len(eases), f">= {F['eases']}", len(eases) >= F['eases'], ', '.join(eases))

    mech = [n for n, rx in MECHANICS if re.search(rx, js)]
    check('entrance mechanics', len(mech), f">= {F['mech']}", len(mech) >= F['mech'], ', '.join(mech))

    trans = [n for n, rx in TRANSITIONS if re.search(rx, js)]
    check('non-crossfade transitions', len(trans), '>= 2', len(trans) >= 2, ', '.join(trans))

    # ---- structure
    scenes = re.findall(r'class="scene"[^>]*id="([^"]+)"|id="([^"]+)"[^>]*class="scene"', html)
    n_scenes = len(scenes)
    check('acts (.scene)', n_scenes, '>= 4', n_scenes >= 4)
    cams = len(re.findall(r'class="cam"', html))
    check('camera layers (.cam)', cams, '>= 3', cams >= 3)
    cam_moves = len(re.findall(r'tl\.(?:to|fromTo|from)\(\s*["\']#cam\d', js))
    check('camera moves', cam_moves, f">= {F['cam']}", cam_moves >= F['cam'])

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
    if footage:
        rows.append(('mode', f'footage-led: {n_vid} videos, {vid_cov:.0%} of runtime', '', 'INFO',
                     'floors for cut-the-brand\'s-motion films — references/footage-led.md'))
    else:
        check('grain texture', 'yes' if has_grain else 'no', 'yes', has_grain)

    # studio-ground assets: the stage must be the same colour, and no texture may sit on top
    grounds = studio_grounds(root, html)
    if grounds is None:
        warns.append('pillow not installed: studio-ground match not checked (pip install pillow)')
    elif grounds:
        stage = css_colours(css)
        bad = []
        for f, g in grounds:
            d = min((hexdist(g, c) for c in stage), default=255)
            if d > 3:
                bad.append(f'{os.path.basename(f)} ground {g} (nearest stage colour off by {d})')
        check('stage colour = asset studio ground', f'{len(grounds) - len(bad)}/{len(grounds)}', 'all within 3',
              not bad, ('; '.join(bad[:3]) + ' — sample the ground, use that hex') if bad else '')
        texture = has_grain or bool(re.search(r'id="(?:falloff|vignette)\w*"', html))
        if footage:
            check('no grain / falloff over studio-ground footage', 'present' if texture else 'none', 'none',
                  not texture, 'it tints the ground and the clip edges show — references/footage-led.md' if texture else '')
    hud = len(HUD_RE.findall(html))
    if hud >= 3 and (footage or grounds):
        warns.append(f'{hud} drawn UI marks (focus corners / rings / cursors) over official imagery — reads as a '
                     'software demo. Keep them only if they reproduce the product\'s own UI (references/footage-led.md)')
    grain_moves = bool(re.search(r'["\']#grain["\'][^;]*steps\(', js))
    if has_grain and not grain_moves:
        warns.append('grain is static — animate it with ease: "steps(N)" over the whole film')
    # slide furniture: a scene counter ("02 / 05") or a progress bar makes a film read as a deck
    counter = bool(re.search(r'id="chap\w*"', html)) or bool(re.search(r'>\s*0?\d\s*<[^>]*>\s*/\s*0?\d\s*<|>\s*0?\d\s*/\s*0\d\s*<|</b>\s*/\s*0\d', html))
    rail = bool(re.search(r'id="(?:progress\w*|rail\w*)"', html))
    furniture = [x for x, on in (('scene counter', counter), ('progress bar', rail)) if on]
    check('no slide furniture (counter / progress bar)', ', '.join(furniture) or 'none', 'none', not furniture,
          'remove it — reads as PPT' if furniture else '')

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

    # ---- asset provenance: assets.md next to film/ (references/assets.md)
    proj_ = os.path.dirname(root)
    am = next((os.path.join(d, 'assets.md') for d in (proj_, root)
               if os.path.exists(os.path.join(d, 'assets.md'))), None)
    local_imgs = sorted(set(s for s in imgs if not s.startswith(('http', 'data:'))
                            and not re.search(r'fonts?/', s)))
    others = [s for s in local_imgs if s not in logo_files]
    if am:
        A = open(am, encoding='utf-8').read()
        trows = [l for l in A.splitlines() if l.strip().startswith('|')]
        def sourced(f):
            name = os.path.basename(f)
            return any(name in l and (re.search(r'https?://', l) or 'provided by user' in l.lower()) for l in trows)
        unsourced = [f for f in local_imgs if not sourced(f)]
        check('every image file has a source URL in assets.md', f'{len(local_imgs) - len(unsourced)}/{len(local_imgs)}',
              'all', not unsourced, ('no source: ' + ', '.join(unsourced[:5])) if unsourced else '')
        need = ['right product', 'current version', 'variant', 'untouched', 'resolution']
        low = A.lower()
        miss = [k for k in need if k not in low]
        check('logo check answered in assets.md', f'{5 - len(miss)}/5', '5/5', not miss,
              ('missing: ' + ', '.join(miss)) if miss else '')
        none_found = 'imagery: none found' in low
        check('official images besides the logo', len(others), '>= 2', len(others) >= 2 or none_found,
              'accepted: "imagery: none found" + searches listed' if none_found and len(others) < 2
              else ('search the press kit, site og:image, app store screenshots — references/assets.md' if len(others) < 2 else ''))
    else:
        check('assets.md (sources + logo check)', 'missing', 'present', False,
              'search for the real logo and imagery first — references/assets.md')
    for f in sorted(set(logo_files)):
        p = os.path.join(root, f)
        if f.lower().endswith('.png') and os.path.exists(p):
            with open(p, 'rb') as fh:
                head = fh.read(24)
            if head[:8] == b'\x89PNG\r\n\x1a\n':
                wpx = int.from_bytes(head[16:20], 'big')
                if wpx < 512:
                    warns.append(f'{f} is a {wpx}px raster logo — show it small and ask for the vector file')

    # ---- process artefacts: the shot list and the copy sheet must exist next to film/
    proj = os.path.dirname(root)
    def find(name):
        for d in (proj, root):
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    sl = find('shot-list.md')
    sl_rows = len([l for l in open(sl, encoding='utf-8') if l.startswith('|') and not set(l.strip()) <= set('|-: ')]) if sl else 0
    check('shot-list.md filled', f'{sl_rows} rows' if sl else 'missing', '>= 6 table rows', sl_rows >= 6,
          'write it BEFORE the timeline — references/shot-list.md' if not sl else '')

    zm = 0
    if sl:
        t = open(sl, encoding='utf-8').read()
        i = t.lower().find('headline zone')
        if i >= 0:
            for l in t[i:].splitlines()[1:]:
                if not l.startswith('|'):
                    if zm: break
                    continue
                cells = [c.strip() for c in l.strip().strip('|').split('|')]
                if set(''.join(cells)) <= set('-: '): continue
                if len(cells) >= 4 and all(cells[1:4]): zm += 1
    check('zone map per act in shot-list.md', f'{zm} acts', '>= 5', zm >= 5,
          'plan headline / product / logo zones per act first — references/layout.md' if zm < 5 else '')

    sig, sig_n = '', 0
    if sl:
        t = open(sl, encoding='utf-8').read()
        m = re.search(r'(?im)^[\s*\-]*\**signature transition\**\s*[:：]\**\s*(.+)$', t)
        if m and len(re.sub(r'[\s*_`]+', '', m.group(1))) >= 4:
            sig = m.group(1).strip()
            sig_n = len(re.findall(r'(?im)^.*\bexit\b.*\bsignature\b', t))
    sig_ok = bool(sig) and sig_n >= 3
    if footage:
        check('signature transition named + used on >= 3 exits', f'{sig_n} exits' if sig else 'missing',
              '>= 3', sig_ok,
              '' if sig_ok else 'one move from the product\'s own geometry, repeated — references/footage-led.md')
    elif not sig_ok:
        warns.append('no signature transition in shot-list.md — films where one move (taken from the product\'s '
                     'shape) carries most act changes read as one idea, not a sampler')

    cp = find('copy.md')
    body = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', html, flags=re.S)
    body = re.sub(r'<!--.*?-->', ' ', body, flags=re.S)
    texts = [re.sub(r'\s+', ' ', t).strip() for t in re.findall(r'>([^<>]+)<', body)]
    texts = [t for t in texts if len(re.findall(r'[\u4e00-\u9fff]', t)) >= 2 or len(re.findall(r'[A-Za-z]', t)) >= 6]
    if cp:
        src = re.sub(r'\s+', '', open(cp, encoding='utf-8').read())
        norm = lambda t: re.sub(r'[\s·・，。,.!！?？:：、|｜—\-]+', '', t)
        unsourced = [t for t in texts if norm(t) and norm(t) not in re.sub(r'[\s·・，。,.!！?？:：、|｜—\-]+', '', src)]
        check('on-screen copy listed in copy.md', f'{len(texts) - len(unsourced)}/{len(texts)}', 'all', not unsourced,
              ('not in copy.md: ' + ' / '.join(unsourced[:6])) if unsourced else '')
    else:
        check('on-screen copy listed in copy.md', 'missing', 'all', False,
              'copy.md: every on-screen line + where it came from (brief / product page / invented-flagged)')

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
    _stamp(path, 'film_audit', not fails, f'{len(fails)} failed')
    return 1 if fails else 0


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


if __name__ == '__main__':
    sys.exit(main())
