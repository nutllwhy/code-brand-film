#!/usr/bin/env bash
# Download subsetted Chinese webfonts (Noto Serif SC / Noto Sans SC, SIL OFL) for
# exactly the characters the film uses, as local woff2 files.
#
#   scripts/fetch_cjk_fonts.sh <chars.txt> <film/assets/fonts> [spec ...]
#
# spec = "<file-stem>:<Google family>:<weight>"; defaults:
#   serif-900:Noto Serif SC:900  serif-600:Noto Serif SC:600
#   sans-400:Noto Sans SC:400    sans-700:Noto Sans SC:700
#
# Why: the headless render browser has no system CJK fonts. `local("PingFang SC")`
# silently falls back to a face with different metrics and every line moves.
# Re-run after every copy change — a character missing from the subset renders
# in the fallback face. ASCII letters/digits are always included.
set -euo pipefail

CHARS_FILE="${1:?usage: fetch_cjk_fonts.sh <chars.txt> <outdir> [stem:Family:weight ...]}"
OUT="${2:?outdir required}"
shift 2
SPECS=("$@")
if [ ${#SPECS[@]} -eq 0 ]; then
  SPECS=("serif-900:Noto Serif SC:900" "serif-600:Noto Serif SC:600" "sans-400:Noto Sans SC:400" "sans-700:Noto Sans SC:700")
fi
mkdir -p "$OUT"

TEXT="$(cat "$CHARS_FILE")0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:;!?%+-/()·"
# a Chrome UA makes the CSS API answer with woff2 instead of ttf
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

for spec in "${SPECS[@]}"; do
  IFS=':' read -r STEM FAMILY WEIGHT <<< "$spec"
  CSS="$(curl -fsSG 'https://fonts.googleapis.com/css2' \
          --data-urlencode "family=${FAMILY}:wght@${WEIGHT}" \
          --data-urlencode "text=${TEXT}" \
          --data-urlencode "display=block" -A "$UA")"
  URL="$(printf '%s' "$CSS" | grep -oE 'url\([^)]+\)' | head -1 | sed -E 's/^url\(//; s/\)$//')"
  [ -n "$URL" ] || { echo "no font url for $spec" >&2; exit 1; }
  curl -fsS "$URL" -o "$OUT/$STEM.woff2"
  printf '%-10s %-16s %s  %s bytes\n' "$STEM" "$FAMILY" "$WEIGHT" "$(wc -c < "$OUT/$STEM.woff2" | tr -d ' ')"
done
