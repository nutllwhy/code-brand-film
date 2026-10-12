#!/usr/bin/env python3
"""build.py — template → film/index.html, and regenerate the CJK font subset.

Copy next to your film's `src/` and edit the CONTENT blocks at the top. Keeping
the repetitive markup generated is what makes a copy change a one-line edit
instead of a six-place edit with one of them missed.

    python3 src/build.py      # writes film/index.html + src/chars.txt

Why the subset list: the render browser fetches local woff2 files, and a system
CJK font is not reliable (PingFang SC fails to load and the render silently
falls back to a typeface with different metrics, shifting every line in the
layout). Download the subset from Google Fonts with the `text=` parameter set to
the contents of chars.txt. Re-run the build whenever copy changes, then
re-download the subset.

    curl -G 'https://fonts.googleapis.com/css2' \
      --data-urlencode "family=Noto Serif SC:wght@900" \
      --data-urlencode "text=$(cat src/chars.txt)" \
      -H 'User-Agent: Mozilla/5.0 ... Chrome/120' > /tmp/serif.css
    # then pull the woff2 url out of /tmp/serif.css into film/assets/fonts/

The UA header matters: without a Chrome UA, the API serves ttf instead of woff2.
"""
import os
import re

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(D)

# ==========================================================================
# CONTENT — everything repetitive in the film is defined here, once.
# ==========================================================================

# Act 2: the pipeline steps, one per beat. Each becomes a numbered node.
STEPS = [
    "读取数据", "清洗 · 汇总", "生成图表",
    "撰写报告", "排版成演示稿", "定时发送",
]

# Act 4: a spreadsheet, generated as rows.
SPREADSHEET = [
    ("A", "120", "3.0%"),
    ("B", "90", "2.5%"),
    ("C", "70", "4.0%"),
    ("TOTAL", "280", "3.1%"),
]

# Act 1: the typed line. One span per character, so the timeline can reveal
# them one at a time — a character reveal is unmistakably hand-made.
TYPED = "把这周的数据整理成报告，做成演示稿，明早发给大家。"

# ==========================================================================
# BUILD
# ==========================================================================

tl = open(os.path.join(D, 'index.tpl.html')).read()

# --- nodes: a horizontal pipeline, one node per step -----------------------
NODE_PITCH = 560          # px between node centres
NODE_LEFT = 180           # left edge of the first node
nodes = ''.join(
    f'<div class="node" id="nd{i}" style="left:{NODE_LEFT + i * NODE_PITCH - 59}px">'
    f'<div class="dot"><div class="fill"></div><span>0{i + 1}</span></div>'
    f'<div class="lab">{label}</div><div class="st mono">进行中</div></div>'
    for i, label in enumerate(STEPS))

# --- spreadsheet cells: three columns, one rule line per row ---------------
cells = ''
for r, (a, b, c) in enumerate(SPREADSHEET):
    y = 128 + r * 46
    cells += f'<div class="cell" style="top:{y + 34}px"></div>'
    colour = '#2B5CFF' if a == 'TOTAL' else '#15171C'   # accent the total row
    cells += (f'<div class="xv" style="left:32px;top:{y}px;color:{colour}">{a}</div>'
              f'<div class="xv" style="left:150px;top:{y}px;color:{colour}">{b}</div>'
              f'<div class="xv" style="left:280px;top:{y}px;color:{colour}">{c}</div>')

# --- typed line: one span per character, non-breaking spaces preserved -----
tspans = ''.join(
    f'<span class="ch">{"&nbsp;" if ch == " " else ch}</span>' for ch in TYPED)

tl = (tl.replace('__NODES__', nodes)
        .replace('__CELLS__', cells)
        .replace('__TYPED__', tspans))

# --- write the film, then collect the CJK subset --------------------------
out = os.path.join(ROOT, 'film', 'index.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w').write(tl)

# every CJK/ideograph character on screen, plus the punctuation the film uses
cjk = sorted(set(ch for ch in tl if ord(ch) > 0x2E80)
             | set('：·｜（）「」，。✓→←↑↓％'))
open(os.path.join(D, 'chars.txt'), 'w').write(''.join(cjk))

print(f'{len(tl)} bytes → {out}')
print(f'{len(cjk)} cjk chars → {os.path.join(D, "chars.txt")}')
