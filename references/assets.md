# Assets — finding the real logo and real imagery, and proving it

Two films built from this skill were sent back for the same pair of reasons:
nobody went looking for the brand's own pictures, and the logo on screen was
not the brand's current logo (one was "an abstract shape inspired by the logo",
drawn by the agent; another was a 192px favicon of the parent app). A viewer
recognises a brand by its mark and its imagery before reading a word. Get these
wrong and nothing else in the film matters.

This is a research step, done **before** the shot list, and it leaves a file:
`assets.md` next to `film/`. `film_audit.py` fails without it.

## 1. Where to look, in order

Stop at the first source that has what you need, but go through all of them
for the logo check in step 2.

1. **What the user or the brief supplied.** Attachments, a brand kit link, a
   drive folder. Always first. If the brief names a product page, that page is
   the second source.
2. **The brand's official press / brand kit.** Search
   `"<brand> press kit"`, `"<brand> brand assets"`, `"<brand> logo download"`,
   `"<品牌> 品牌资源"`, `"<品牌> 媒体资源"`, `"<品牌> 新闻中心 下载"`.
   These carry the vector logo, colour values and approved imagery.
3. **The official product website.** Read the HTML, not just the page:
   - the header logo — often an inline `<svg>` or an `.svg` file; copy it exactly
   - `<link rel="icon">`, `apple-touch-icon`, `manifest.json` icons (largest size)
   - `og:image` / `twitter:image` — the brand's chosen hero picture
   - hero and feature images, product screenshots, demo video posters
   - **product motion**: `harvest_page_images.py <page> --video` pulls the
     page's animations and films. If the brand ships motion, the film is
     footage-led — read `footage-led.md` before the shot list.
   - the same page **in the audience's language** (country site): the copy
     comes from there, and it can carry different clips
4. **The app store listing** (App Store / Google Play / Mac App Store / the
   Windows store): the current app icon at 512–1024px and 5–10 official
   screenshots of the real interface. This is the best source of what the
   product actually looks like today.
5. **Official social accounts and launch posts** (WeChat official account,
   Weibo, X, YouTube, the launch blog post): launch posters, key visuals.

Never use: logo aggregator sites (seeklogo, worldvectorlogo, brandfetch mirrors,
icon packs) — they are often years out of date; screenshots of search results;
AI-generated "brand-like" images; anything you drew yourself to look like the
logo.

**Harvest the product page in one go.** Product pages hide most of their
images in `srcset`, `data-src`, CSS backgrounds and JSON blobs; reading `<img
src>` finds about a third. Run

```bash
python3 <skill>/scripts/harvest_page_images.py <product-page-url> [<regional-page-url>] --out research
```

It saves the pages, downloads every image (deduped), writes `index.tsv`
(number, size, URL) and contact sheets of everything ≥ 900px wide. One real
product page gave 250 images: product shots on black, sample footage, UI
close-ups, and the logo and product wordmark as inline SVG. Look at the
sheets, pick by number, copy the URL into `assets.md`. Open every `.svg` — the
logo and the product's own wordmark are usually among them, already in the
light and dark variants.

## 2. Is it the right logo? Check before you use it

A file called `logo.svg` is not proof. Answer all five in `assets.md`:

| Check | How |
| --- | --- |
| **Right product** | Is the film for the parent brand or a sub-product? A sub-product (a "Work" / "Pro" / "Agent" edition, a desktop app) often has its own mark or lockup. Use the one on that product's own page, not the parent app's icon. |
| **Current version** | Compare against what the official site header and the app store icon show *today*. If they differ from your file, your file is old. Brands redesign; aggregators and old articles keep the previous mark. |
| **Right variant** | Symbol vs horizontal lockup vs wordmark; light-ground vs dark-ground version; monochrome. Pick the variant made for your background — do not invert colours yourself. |
| **Untouched** | Not recoloured, re-lettered, stretched, rotated, cropped, outlined, or given a drop shadow beyond what the brand uses. Animate its container (scale, position, opacity, a mask), never redraw its shape. |
| **Resolution** | Vector, or raster at ≥ 512px for anything shown larger than ~120px. A favicon is acceptable only small, and must be flagged in delivery with a request for the vector file. |

If two official sources disagree (site header vs app icon), use the product
page's version, and tell the user which one you picked and why.

## 3. Imagery: what to bring back

Floor for a 15s film: **the logo plus ≥ 2 official images**, at least one of
which shows the real product (a screenshot, a device render, the interface).

Use them as material, not as slides:
- a real screenshot as the screen of a device, cropped and pushed into
- an official key visual seen through a mask, an iris, a lens
- a screenshot as the reference you rebuild in HTML — the rebuilt UI must match
  the real one's layout, colours and labels; cite the screenshot in `assets.md`

**Physical products** (cameras, phones, headphones, drinks): the product appears
as its official photo or render, cut out on transparent ground, every time it is
on screen. A glowing outline or a CSS rectangle "standing for" the device is a
rejected film — one was delivered with the camera drawn as a rounded rectangle
and the maker's name typed in a font instead of its logo. Official product
pages always carry these images; look in the page's `<img>` / `srcset` /
`og:image` and the press or media centre.

**Product photos on black.** Hardware pages usually shoot the product on pure
black. Do not cut it out — make the stage the same black and lift the photo's
shadows with a curve (e.g. Pillow `point(lambda v: 255*((v/255)**0.8))`) so
the edges read on a phone. A cut-out with a hand-made mask looks pasted; the
original black ground melts into the stage. Choose images where the product is
shot from different angles (front, three-quarter, the mechanism/X-ray view)
so act 1 and the landing do not repeat the same angle.

If you truly find nothing beyond the logo (a brand with no site, a product not
launched yet), write `imagery: none found` in `assets.md` followed by every
search you ran and every URL you checked. The audit accepts that line; the user
will read it.

## 4. `assets.md` — the manifest

One row per non-font file in `film/assets/`, plus the logo checks. In Notes,
say whether the image has **type baked in** (a headline, the product name in
3D letters, a price) — such an image can't take a second title next to it
(`layout.md`, "The last frame"):

```markdown
# Assets

| File | What | Source URL | Fetched | Notes |
| --- | --- | --- | --- | --- |
| assets/logo.svg | product lockup, dark-ground variant | https://example.com/ (header inline svg) | 2026-10-13 | vector |
| assets/screen-1.png | task panel screenshot | https://apps.apple.com/app/id000 (screenshot 2) | 2026-10-13 | 2048×1536 |
| assets/hero.jpg | launch key visual (type baked in: product name) | https://example.com/ (og:image) | 2026-10-13 | 1920×1080 |

## Logo check
- Right product: the "Work" edition's own lockup, from its product page — not the parent app icon
- Current version: matches the site header and the App Store icon as of today
- Variant: light-on-dark lockup, for the dark ground
- Untouched: used as-is; only its container is animated
- Resolution: vector

## Searches run
- "example press kit" → brand kit page, no download without login
- App Store listing → icon + 6 screenshots
```

Files supplied by the user: write `provided by user` in the Source column.

## 5. Delivery

List what came from where in one or two lines, and flag: any raster logo,
any logo variant you were unsure about, any UI you rebuilt rather than used,
and `imagery: none found` if it applies. For client work, say the brand should
confirm the logo version before publishing.
