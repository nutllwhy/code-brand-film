#!/usr/bin/env python3
"""Pull every image an official product page uses, so you pick from the brand's
own pictures instead of guessing.

    python3 harvest_page_images.py <url> [<url> ...] --out research

Writes:
  research/pages/*.html        the raw pages (keep them: they are your source proof)
  research/raw/<n>.<ext>       every image, de-duplicated by content hash
  research/index.tsv           n, width, height, bytes, url  (svg width = 0)
  research/sheet-<k>.jpg       contact sheets of everything >= --min px wide, labelled by n

Then open the sheets, pick by number, and copy the URL from index.tsv into
assets.md. Product pages hide most images in srcset / data-src / CSS
background-image / JSON blobs; a plain <img src> scan finds a third of them.
Needs: pillow (pip install pillow). Uses only urllib otherwise.
"""
import argparse, hashlib, html, os, re, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
EXT = r"(?:jpe?g|png|webp|avif|svg|gif)"
PAT = re.compile(r"""(?:https?:)?//[^\s"'()<>\\]+?\.""" + EXT + r"""(?:\?[^\s"'()<>\\]*)?""", re.I)
REL = re.compile(r"""(?:src|data-src|data-original|href|content)=["']([^"']+?\.""" + EXT + r""")["']""", re.I)


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": url})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def urls_in(page_url, text):
    text = html.unescape(text).replace("\\/", "/").replace("\\u002F", "/")
    found = set()
    for m in PAT.findall(text):
        found.add(("https:" + m) if m.startswith("//") else m)
    for m in REL.findall(text):
        found.add(urllib.parse.urljoin(page_url, m))
    # srcset: "a.jpg 1x, b.jpg 2x" — PAT already catches each entry
    return sorted(found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--out", default="research")
    ap.add_argument("--min", type=int, default=900, help="min width for contact sheets")
    a = ap.parse_args()
    os.makedirs(f"{a.out}/pages", exist_ok=True); os.makedirs(f"{a.out}/raw", exist_ok=True)

    all_urls = []
    for i, u in enumerate(a.urls):
        body = get(u).decode("utf-8", "replace")
        open(f"{a.out}/pages/page{i}.html", "w").write(body)
        us = urls_in(u, body)
        print(f"{u}: {len(body)} bytes, {len(us)} image urls")
        all_urls += us
    all_urls = list(dict.fromkeys(all_urls))

    def fetch(u):
        try:
            return u, get(u)
        except Exception as e:  # noqa
            return u, None

    seen, rows = {}, []
    with ThreadPoolExecutor(8) as ex:
        for u, data in ex.map(fetch, all_urls):
            if not data or len(data) < 2000 and not u.lower().split("?")[0].endswith(".svg"):
                continue
            h = hashlib.sha1(data).hexdigest()
            if h in seen:
                continue
            n = len(seen); seen[h] = n
            ext = re.search(EXT + r"$", u.split("?")[0], re.I)
            ext = ext.group(0).lower() if ext else "bin"
            path = f"{a.out}/raw/{n:03d}.{ext}"
            open(path, "wb").write(data)
            w = hgt = 0
            if ext != "svg":
                try:
                    from PIL import Image
                    with Image.open(path) as im:
                        w, hgt = im.size
                except Exception:
                    pass
            rows.append((n, w, hgt, len(data), u, path))
    with open(f"{a.out}/index.tsv", "w") as f:
        f.write("n\twidth\theight\tbytes\turl\n")
        for n, w, hgt, b, u, _ in rows:
            f.write(f"{n}\t{w}\t{hgt}\t{b}\t{u}\n")
    svgs = [r for r in rows if r[5].endswith(".svg")]
    big = [r for r in rows if r[1] >= a.min]
    print(f"{len(rows)} unique images, {len(big)} >= {a.min}px, {len(svgs)} svg (logo / wordmark candidates: open them)")

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("pillow missing: no contact sheets"); return
    cols, tw, th, per = 5, 384, 216, 30
    for k in range(0, len(big), per):
        chunk = big[k:k + per]
        rows_n = (len(chunk) + cols - 1) // cols
        S = Image.new("RGB", (cols * tw, rows_n * (th + 18)), (40, 40, 40)); d = ImageDraw.Draw(S)
        for i, r in enumerate(chunk):
            try:
                im = Image.open(r[5]).convert("RGB"); im.thumbnail((tw, th))
            except Exception:
                continue
            x, y = (i % cols) * tw, (i // cols) * (th + 18)
            S.paste(im, (x, y)); d.text((x + 4, y + th + 3), f"#{r[0]}  {r[1]}x{r[2]}", fill=(255, 255, 255))
        out = f"{a.out}/sheet-{k // per}.jpg"; S.save(out, quality=85); print("sheet:", out)


if __name__ == "__main__":
    sys.exit(main())
