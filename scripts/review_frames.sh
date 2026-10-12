#!/usr/bin/env bash
# Sheet a rendered film into review frames.
#
#   ./review_frames.sh film/renders/final.mp4 [outdir] [fps]
#
# Produces:
#   <outdir>/sheet.jpg    a contact sheet — the whole film at a glance
#   <outdir>/f-<t>.png    one still per requested timestamp (optional)
#
# Why 2 fps and not 1: a 0.2s artifact (ghosting at a scene boundary, a one-frame
# black flash in a whip transition) vanishes completely when you sample at 1 fps.
# The sheet is for finding a suspect region; the still is for judging it.
set -euo pipefail

SRC="${1:?usage: review_frames.sh <film.mp4> [outdir] [fps] [t1,t2,...]}"
OUT="${2:-$(dirname "$SRC")/../snapshots}"
FPS="${3:-2}"
TIMES="${4:-}"
mkdir -p "$OUT"

# contact sheet: 6 columns; rows follow the film length (15s at 2fps = 30 = 5 rows)
ffmpeg -y -v error -i "$SRC" -vf "fps=${FPS},scale=384:-1,tile=6x5" -frames:v 1 "$OUT/sheet.jpg"
echo "sheet  $OUT/sheet.jpg"

# individual stills at full size
if [ -n "$TIMES" ]; then
  IFS=',' read -ra TS <<< "$TIMES"
  for t in "${TS[@]}"; do
    ffmpeg -y -v error -ss "$t" -i "$SRC" -frames:v 1 "$OUT/f-${t}.png"
    echo "still  $OUT/f-${t}.png"
  done
fi

# duration and stream sanity, so a truncated render is caught here and not later
ffprobe -v error -show_entries stream=codec_type,codec_name,duration -of csv=p=0 "$SRC"
