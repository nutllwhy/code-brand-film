# Motion recipes — copyable GSAP for every mechanic in quality-bar.md

All snippets assume one paused master timeline:

```js
window.__timelines = window.__timelines || {};
var tl = gsap.timeline({ paused: true });
// ... recipes ...
tl.seek(0);
window.__timelines["<composition-id>"] = tl;
```

Times are absolute seconds on that timeline. Every recipe below came out of an
accepted film. Adapt the selectors and times; keep the eases and durations
unless you have a reason — they are what make each move read correctly.

## Contents

1. Texture layer (grain, falloff) — and what not to add
2. Line mask reveal
3. Character typing + caret + send pulse
4. Letter scatter
5. Persistent element hand-off (dock across acts)
6. Pipeline: one step per beat
7. Number count-up / one value on many screens
8. Stroke draw (lines, connectors)
9. 3D card fly-in
10. 3D hinge (lid closing)
11. Ticker roll (word carousel)
12. Zoom-through transition
13. Lateral whip transition
14. Logo portal (dive into the mark, collapse back into it)
15. Iris reveal
16. Collapse to a point
17. Stamp slam + camera shake
18. Lockup (blur-in wordmark, rule, CTA)
19. Ambient motion (so no frame is static)
20. Screen portal (go in through the product's own screen)
21. Viewfinder / device HUD over footage
22. Claim-proof shots (log → graded wipe, lossless zoom, meter)
23. Light sweep across a product photo
24. Fold on the seam (two halves rotate shut on a centre line)
25. Seam open (next shot opens out of a line)
26. Anchor match cut (two clips, one hinge position)
27. Pose burst (several stills on one anchor, < 0.5 s each)

Recipes 24–27 belong to footage-led films — read `footage-led.md` first.

---

## 1. Texture layer

```html
<div id="grain"></div><div id="falloff"></div>
<!-- optional: ONE quiet brand mark in a corner. Nothing else. -->
<div class="mono" id="mark">BRAND</div>
```

**Do not add** a chapter / page counter (`02 / 05`), a progress bar, a timecode,
or four corner labels. They are slide and video-player furniture: the user's
first reaction to a film that had them was "太像 PPT 了". A film does not tell
the viewer which scene number it is on.

```css
#grain { position:absolute; inset:-40px; z-index:40; pointer-events:none; opacity:.14; mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)'/%3E%3C/svg%3E"); }
/* on a dark film use mix-blend-mode: overlay and opacity ~.11 */
#falloff { position:absolute; inset:0; z-index:39; pointer-events:none;
  background: radial-gradient(120% 100% at 50% 45%, rgba(0,0,0,0) 60%, rgba(0,0,0,.22) 100%); }
#mark { position:absolute; left:72px; top:52px; z-index:45; font-size:17px; opacity:.6; }
```

```js
tl.to("#grain", { x: 26, y: -20, duration: 15, ease: "steps(45)" }, 0);   // grain that crawls, not slides
```

## 2. Line mask reveal

Text rises from behind its own line. The parent clips; the child moves.

```html
<div class="line"><span id="l1">Most AI forgets you.</span></div>
```
```css
.line { overflow: hidden; } .line > span { display: inline-block; }
```
```js
tl.fromTo("#l1", { yPercent: 105 }, { yPercent: 0, duration: 0.9, ease: "expo.out" }, 0.15);
tl.fromTo("#l2", { yPercent: 105 }, { yPercent: 0, duration: 0.9, ease: "expo.out" }, 0.42);  // stagger lines ~0.27s
```

## 3. Character typing + caret + send pulse

Generate one span per character in the build step (`build_template.py` does it).

```js
var chars = document.querySelectorAll("#barText .ch");
var T_TYPE = 0.55, PER = 1.75 / chars.length;          // whole line in 1.75s
chars.forEach(function (c, i) { tl.set(c, { opacity: 1 }, T_TYPE + i * PER); });
// caret blinks only while idle — a caret blinking while typing looks broken
tl.to("#caret", { opacity: 0, duration: 0.01 }, 0.30);
tl.to("#caret", { opacity: 1, duration: 0.01 }, 0.45);
tl.to("#caret", { opacity: 0, duration: 0.01 }, 2.45);
// press the send button, then a ring
tl.fromTo("#send", { scale: 1 }, { scale: 0.86, duration: 0.08, ease: "power2.in" }, 2.5);
tl.to("#send", { scale: 1, duration: 0.3, ease: "back.out(3)" }, 2.58);
tl.fromTo("#pulse", { opacity: 0.9, scale: 0.6 }, { opacity: 0, scale: 3.2, duration: 0.7, ease: "power2.out" }, 2.5);
```
CSS: `#barText .ch { opacity: 0; }`

## 4. Letter scatter

A word falls apart. Offsets are a fixed table, not `Math.random()` — the
renderer seeks frames out of order and random values would differ per frame.

```js
var drift = [[-40,-150,-24],[30,-210,18],[-20,-120,32],[50,-260,-14],[-60,-180,22],[20,-230,-30],[70,-160,12]];
document.querySelectorAll("#word .f").forEach(function (el, i) {
  var d = drift[i % drift.length];
  tl.to(el, { x: d[0], y: d[1], rotation: d[2], opacity: 0, duration: 0.75, ease: "power2.in" }, 1.45 + i * 0.045);
});
```

## 5. Persistent element hand-off

The strongest transition: something from act 1 stays and act 2 is built around
it. Place the persistent element **outside** every `.scene` so scene fades do
not touch it.

```js
// act 1 ends: the input bar shrinks and docks top-left while act 1's backdrop leaves
tl.to("#bar", { x: -140, y: -340, scale: 0.62, duration: 0.6, ease: "expo.inOut" }, 2.75);
tl.to("#s1", { opacity: 0, duration: 0.4, ease: "power1.in" }, 2.8);
tl.set("#s2", { opacity: 1 }, 2.9);
// ... act 2 plays with the bar visible as "the brief" ...
tl.to("#bar", { opacity: 0, y: -400, duration: 0.45, ease: "power2.in" }, 5.6);   // released at the next cut
```
CSS: `#bar { transform-origin: 0 50%; }` so it shrinks toward its corner.

## 6. Pipeline: one step per beat

A track slides under the camera while nodes land one per beat and fill.

```js
var B = 0.5;
tl.fromTo("#track", { x: 0 }, { x: -1460, duration: 3.3, ease: "power1.inOut" }, 3.0);
tl.fromTo("#trackFill", { scaleX: 0 }, { scaleX: 1, duration: 2.9, ease: "power1.inOut" }, 3.05);
for (var i = 0; i < 6; i++) {
  var t = 3.0 + i * B;
  tl.fromTo("#nd" + i, { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.45, ease: "power4.out" }, t);
  tl.fromTo("#nd" + i + " .fill", { scale: 0 }, { scale: 1, duration: 0.35, ease: "back.out(2)" }, t + 0.35);
  tl.to("#nd" + i + " .dot", { color: "#FFFFFF", duration: 0.2 }, t + 0.4);
  tl.set("#nd" + i + " .st", { textContent: "done" }, t + 0.45);
}
```

## 7. Number count-up / one value on many screens

```js
// a single counter
var o = { v: 0 }, el = document.querySelector("#n1");
tl.to(o, { v: 47, duration: 0.5, ease: "power2.out", onUpdate: function () { el.textContent = Math.round(o.v); } }, 6.4);

// one progress value driving three devices — that is what "sync" looks like
var prog = { v: 12 };
var pcts = document.querySelectorAll("#s3 .pct"), bars = document.querySelectorAll("#s3 .p i");
tl.to(prog, { v: 100, duration: 2.6, ease: "power1.inOut", onUpdate: function () {
  var v = Math.round(prog.v);
  pcts.forEach(function (e) { e.textContent = v; });
  bars.forEach(function (b) { b.style.transform = "scaleX(" + (prog.v / 100) + ")"; });
} }, 6.6);

// a clock running overnight 23:40 → 08:52
var clk = { m: 23 * 60 + 40 }, clkEl = document.getElementById("clock");
tl.to(clk, { m: 24 * 60 + 8 * 60 + 52, duration: 2.4, ease: "power2.inOut", onUpdate: function () {
  var m = Math.round(clk.m) % 1440, h = Math.floor(m / 60), mm = m % 60;
  clkEl.textContent = (h < 10 ? "0" : "") + h + ":" + (mm < 10 ? "0" : "") + mm;
} }, 6.7);
```

## 8. Stroke draw

Do **not** put `stroke-dasharray` in CSS — it overrides the attribute the tween
sets and the line shows dashed from frame 0. Set it in the tween's `from`.

```js
["#th1", "#th2"].forEach(function (p, k) {
  var len = document.querySelector(p).getTotalLength();
  tl.fromTo(p, { attr: { "stroke-dashoffset": len, "stroke-dasharray": len + " " + len } },
               { attr: { "stroke-dashoffset": 0 }, duration: 0.4, ease: "power2.out" }, 7.0 + k * 0.5);
});
// for <line> elements use Math.hypot(x2-x1, y2-y1) instead of getTotalLength()
```

## 9. 3D card fly-in

Parent needs `perspective: 1800px`. Land the cards slightly off-axis, not flat —
a little residual rotation is what makes them read as objects in space.

```js
tl.fromTo("#ppt", { opacity: 0, rotationY: -28, rotationX: 10, z: -400, y: 80 },
                  { opacity: 1, rotationY: -8, rotationX: 4, z: 0, y: 0, duration: 0.8, ease: "expo.out" }, 9.5);
tl.fromTo("#rpt", { opacity: 0, rotationY: 30, z: -500, x: -80 },
                  { opacity: 1, rotationY: 12, z: -120, x: 0, duration: 0.8, ease: "expo.out" }, 10.0);
tl.fromTo(".bar4", { scaleY: 0 }, { scaleY: 1, duration: 0.6, stagger: 0.07, ease: "power3.out" }, 9.85);  // chart inside the card
tl.fromTo("#note", { opacity: 0, y: 60, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "back.out(1.6)" }, 11.0);
```

## 10. 3D hinge (lid closing)

A flat rectangle cannot close. Build a rig: a tilted parent, a deck lying flat
at 90°, and a lid hinged on its bottom edge with a back face.

```css
#laptop { perspective: 1500px; perspective-origin: 50% -30%; }
#lapRig { position:absolute; inset:0; transform-style:preserve-3d; transform: rotateX(16deg); }
#deck { position:absolute; left:40px; top:430px; width:680px; height:400px; transform-origin:50% 0; transform: rotateX(90deg); }
#lid  { position:absolute; left:40px; top:0; width:680px; height:430px; transform-origin:50% 100%; transform-style:preserve-3d; }
#lid .screen { backface-visibility:hidden; }
#lidBack { position:absolute; inset:0; backface-visibility:hidden; transform: rotateX(180deg); }  /* logo goes here */
```
```js
tl.fromTo("#lid", { rotationX: 0 }, { rotationX: -90, duration: 0.55, ease: "power3.in" }, 6.5);
```

## 11. Ticker roll

A column of words in an `overflow:hidden` window; move it one row per beat.

```js
var STEP = 0.62, T0 = 6.4;            // the beat grid
tl.fromTo("#tickIn", { y: 300 }, { y: 0, duration: 0.55, ease: "expo.out" }, 6.25);
for (var k = 1; k < 5; k++) {
  tl.to("#tickIn", { y: -300 * k, duration: 0.42, ease: "expo.inOut" }, T0 + k * STEP - 0.12);  // start just before the beat
}
```

## 12. Zoom-through transition

Fly into an object in act N; act N+1 starts slightly small and settles.

```js
tl.to("#cam3", { scale: 3.2, x: -1500, y: -150, duration: 0.45, ease: "power3.in" }, 9.15);  // toward the target object
tl.to("#cam3", { opacity: 0, duration: 0.2, ease: "power1.in" }, 9.4);
tl.fromTo("#s4", { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "power1.out" }, 9.45);
tl.fromTo("#cam4", { scale: 0.88 }, { scale: 1.0, duration: 1.0, ease: "expo.out" }, 9.45);
```
Find `x, y` by pointing the camera's scale at the target: `x ≈ (960 - targetCenterX) * (scale - 1)`.

## 13. Lateral whip transition

Overlap the exit and entrance by ~0.25s so no frame is empty.

```js
tl.to("#cam2", { x: -700, opacity: 0, duration: 0.55, ease: "power3.in" }, 5.6);
tl.set("#s3", { opacity: 1 }, 5.85);
tl.fromTo("#cam3", { x: 760 }, { x: 0, duration: 0.85, ease: "expo.out" }, 5.85);
```

## 14. Logo portal

For a logo with an opening (a hole, a counter, a window). The logo's scale and a
`clip-path` circle on the next layer are driven by one proxy so the clip edge
always sits under the logo's ring. Scale on an exponential curve — linear
scaling of a 40× zoom looks like a sticker being resized.

```js
var HOLE = 148;                                    // hole radius in px at scale 1, centred at (960,540)
function portal(logoSel, layerSel, proxy) {
  var logo = document.querySelector(logoSel), layer = document.querySelector(layerSel);
  return function () {
    logo.style.transform = "rotate(" + proxy.r + "deg) scale(" + proxy.s + ")";
    layer.style.clipPath = "circle(" + (HOLE * proxy.s) + "px at 960px 540px)";
  };
}
// dive in: appear, settle, then accelerate past the frame
var pa = { s: 0.001, r: -70 }, paW = portal("#logoA", "#s2", pa); paW();
tl.set(["#logoA", "#s2"], { opacity: 1 }, 2.05);
tl.to(pa, { s: 1,  r: 0,  duration: 0.85, ease: "expo.out",  onUpdate: paW }, 2.05);
tl.to(pa, { s: 38, r: 24, duration: 0.65, ease: "power3.in", onUpdate: paW }, 2.88);
tl.set("#logoA", { opacity: 0 }, 3.56);
// collapse back at the end: same function, scale 40 → 1, the world shrinks into the hole
var pb = { s: 40, r: -18 }, pbW = portal("#logoB", "#endLayer", pb); pbW();
tl.to(pb, { s: 1, r: 0, duration: 1.15, ease: "expo.inOut", onUpdate: pbW }, 12.25);
```
For a perceptually even zoom over a huge range, tween an exponent instead:
`proxy.e: 0 → 1`, then `s = Math.exp(Math.log(s0) + e * (Math.log(s1) - Math.log(s0)))`.

## 15. Iris reveal

```js
tl.set("#s4", { opacity: 1 }, 9.45);                 /* CSS: #s4 { clip-path: circle(0px at 960px 540px); } */
tl.to("#s4", { clipPath: "circle(1150px at 960px 540px)", duration: 0.8, ease: "expo.inOut" }, 9.45);
tl.fromTo("#ring", { opacity: 1, scale: 0 }, { scale: 58, opacity: 0, duration: 0.85, ease: "expo.inOut" }, 9.45);  // hides the clip edge
tl.fromTo("#photo", { scale: 1.16, x: -60 }, { scale: 1.02, x: 0, duration: 2.6, ease: "power1.out" }, 9.45);    // the revealed image keeps moving
```
`expo.inOut` over less than 0.8s snaps visibly in the middle; lengthen it or use `power3.inOut`.

## 16. Collapse to a point

```js
tl.to(["#ppt", "#rpt", "#xls", "#note"], { scale: 0.2, opacity: 0, x: 0, duration: 0.45, ease: "power3.in", stagger: 0.04 }, 12.05);
tl.to("#s4-head", { opacity: 0, y: -30, duration: 0.35, ease: "power2.in" }, 12.05);
tl.set("#s5", { opacity: 1 }, 12.45);
```

## 17. Stamp slam + camera shake

Leave a gap in the headline for the stamp to land in (`<span class="gap">`).

```js
tl.fromTo("#seal", { opacity: 0, scale: 2.4, rotation: -9 },
                   { opacity: 1, scale: 1, rotation: -2, duration: 0.25, ease: "power4.in" }, 13.25);   // lands at 13.5 = the downbeat
tl.fromTo("#sealInk", { scale: 0.6, opacity: 1 }, { scale: 1.5, opacity: 0, duration: 0.7, ease: "power2.out" }, 13.5);
tl.fromTo("#cam5", { y: 0 }, { y: 7, duration: 0.05, ease: "none" }, 13.5);     // shake: down, up, settle
tl.to("#cam5", { y: -4, duration: 0.06, ease: "none" }, 13.55);
tl.to("#cam5", { y: 0, duration: 0.12, ease: "power2.out" }, 13.62);
```
Keep the stamp's rotation small (≤ 3° at rest). A 10°+ tilt reads as a discount sticker.

## 18. Lockup

```js
tl.fromTo("#s5-rule", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "expo.inOut" }, 13.75);
tl.fromTo("#lockWord", { opacity: 0, x: 80, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.9, ease: "expo.out" }, 13.6);
tl.fromTo("#lockTag", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" }, 13.95);
tl.fromTo("#cta", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }, 14.25);
tl.to("#cam5", { scale: 1.02, duration: 1.2, ease: "sine.out" }, 13.8);   // a final slow push so the last frame is not frozen
```

## 19. Ambient motion

No frame should be completely still except, optionally, the last 0.3s. Give
every act a slow background drift that runs its whole length:

```js
tl.fromTo("#cam1", { scale: 1.04 }, { scale: 1.0, duration: 3, ease: "power2.out" }, 0);    // gentle settle
tl.fromTo("#ghost", { x: 60 }, { x: -80, duration: 3.2, ease: "none" }, 0);                  // giant faint word drifting behind
tl.fromTo("#dots", { x: 0, y: 0 }, { x: -48, y: -24, duration: 3.2, ease: "none" }, 0);      // dot grid parallax
tl.fromTo("#glow", { scale: 0.7, opacity: 0.4 }, { scale: 1.15, opacity: 1, duration: 2.6, ease: "sine.inOut" }, 0);
tl.fromTo("#cloudDot", { attr: { r: 8 } }, { attr: { r: 18 }, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 3 }, 7.2);  // "working"
```
A giant, 4–5%-opacity word behind the content (`font-size: 300px`) plus a dot
grid moving at a different speed is the cheapest way to get three depth layers.

## 20. Screen portal (go in through the product's own screen)

The strongest transition for any device with a display (camera, phone, watch,
laptop, car dashboard): the next act starts *inside* the screen of the product
photo, and the camera pushes until that screen is the frame. It is a
zoom-through whose target is the product itself, so the transition sells it.

Measure the screen glass in the photo's own pixels (open the image, read the
corners), then drive one proxy that scales the camera *and* recomputes the
clip of the next scene every frame, so the footage stays locked to the glass:

```js
// screen glass inside #cam1 (the product photo layer), local px; ox/oy = its centre
const SC = { l: 816, r: 1036, t: 456, b: 592, ox: 926, oy: 524 };
tl.set("#cam1", { transformOrigin: SC.ox + "px " + SC.oy + "px" }, 2.4);
const zoom = { k: 1, x: 230 };
const place = () => {
  const k = zoom.k, X = zoom.x;
  gsap.set("#cam1", { scale: k, x: X });
  const L = SC.ox + k * (SC.l - SC.ox) + X, R = SC.ox + k * (SC.r - SC.ox) + X,
        T = SC.oy + k * (SC.t - SC.oy),     B = SC.oy + k * (SC.b - SC.oy);
  gsap.set("#s3", { clipPath: `inset(${Math.max(0,T)}px ${Math.max(0,1920-R)}px ${Math.max(0,1080-B)}px ${Math.max(0,L)}px round ${Math.min(10*k,40)}px)` });
};
tl.set("#s3", { opacity: 1 }, 2.75);                                            // footage appears on the glass
tl.fromTo(zoom, { k: 1, x: 230 }, { k: 1.18, x: 200, duration: 1.5, ease: "sine.inOut", onUpdate: place, immediateRender: false }, 2.75); // hold, breathe
tl.to(zoom, { k: 13, x: 30, duration: 0.85, ease: "expo.in", onUpdate: place }, 4.25);  // dive
tl.to("#cam1", { opacity: 0, duration: 0.25 }, 4.85);
tl.set("#s3", { clipPath: "inset(0px round 0px)" }, 5.1);                       // land: full frame, downbeat
```
Rules: the footage inside the glass must already be moving (its own slow
scale) before the dive, or it reads as a sticker. Land on a downbeat with a
flash or a sub hit. Check the glass corners at k=1 by screenshot — 4px off is
visible.

## 21. Viewfinder / device HUD over footage

For hardware, "the product doing its work" is its *output*, framed by its own
interface. Put a thin HUD over the footage acts: corner brackets, REC dot +
running timecode, a mode tag that changes per shot (`D-LOG`, `4K 240`, `2×`).
Keep it at 56px insets, 2px lines, mono font, 70–85% white; it is a frame, not
content. Brackets pop in once (`scale 1.6 → 1`, `expo.out`, stagger 0.04), the
timecode counts every frame, the mode tag swaps on each cut with a 0.1s
mask-wipe. The HUD also hides the seams of very different footage — it makes
four official sample shots read as one camera's day.

```js
const tc = { f: 0 };
tl.to(tc, { f: 6 * 30, duration: 6, ease: "none", onUpdate: () => {
  const f = Math.floor(tc.f), s = Math.floor(f / 30);
  document.querySelector("#tc").textContent = `00:00:${String(s).padStart(2,"0")}:${String(f % 30).padStart(2,"0")}`;
} }, 5.1);
```

## 22. Claim-proof shots

A feature line on screen needs a picture that proves it in under a second.
Three that work:

- **Log → graded wipe** ("10-bit log", "HDR", "colour science"): the same image
  twice, the top copy desaturated and flattened (`filter: saturate(.25)
  contrast(.72) brightness(1.08)`), revealed by a vertical line sweeping
  `clip-path: inset(0 0 0 100%) → inset(0 0 0 0)` over ~0.8s, `power2.inOut`.
  Put a 2px white line on the wipe edge.
- **Lossless zoom** ("2× zoom", "48MP crop"): a scale push from 1 to 2 on an
  image whose source is at least 2× the frame (a 4K official still for a 1080p
  film). If the source is only 1920 wide the push shows mush and contradicts
  the claim — pick another image. `transformOrigin` on the subject, `expo.inOut`.
- **Meter** ("14 stops", "1000 nits", "48 h battery"): a row of segments that
  light one per frame (`tl.set` each with 0.045s spacing). Counting things up
  is more believable than a big number.

## 23. Light sweep across a product photo

A specular band crossing the product sells "premium hardware" in 0.8s. Use a
blend layer, never a luminance mask (a mask leaves a grey haze over the black
ground):

```css
#sweep { position:absolute; inset:0; mix-blend-mode: color-dodge; opacity:0; pointer-events:none;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,.55) 50%, transparent 60%) no-repeat;
  background-size: 1300px 100%; }
```
```js
tl.fromTo("#sweep", { opacity: 1, backgroundPosition: "1300px 0" }, { backgroundPosition: "-2600px 0", duration: 1.1, ease: "power2.inOut" }, 0.9);
```
color-dodge only brightens what is already lit, so the band rides the edges of
the product and leaves the black ground black.

## 24. Fold on the seam

The current picture splits into two halves that rotate shut on the centre line,
like a book closing. Build the act as two clipped halves of the same content
(duplicate any `<video>` file so each half has its own copy):

```css
.persp { perspective: 2400px; perspective-origin: 960px 540px; }
.half { position:absolute; top:0; width:960px; height:1080px; overflow:hidden; backface-visibility:hidden; }
.half.l { left:0;     transform-origin: 960px 540px; }
.half.r { left:960px; transform-origin: 0px 540px; }
.half .inner { position:absolute; top:0; width:1920px; height:1080px; }
.half.r .inner { left:-960px; }
.shade { position:absolute; inset:0; opacity:0; pointer-events:none; }
.half.l .shade { background: linear-gradient(90deg, rgba(0,0,0,.05), rgba(0,0,0,.42)); }
.half.r .shade { background: linear-gradient(270deg, rgba(0,0,0,.05), rgba(0,0,0,.42)); }
```
```html
<div id="a3" class="scene persp">
  <div id="a3L" class="half l"><div class="inner"><div class="cam">…content…</div></div><div class="shade"></div></div>
  <div id="a3R" class="half r"><div class="inner"><div class="cam">…same content…</div></div><div class="shade"></div></div>
</div>
```
```js
tl.set("#seam", { opacity: 1, scaleY: 1 }, T - 0.02);
tl.to("#a3L", { rotationY: -89, duration: 0.42, ease: "power3.in" }, T);
tl.to("#a3R", { rotationY:  89, duration: 0.42, ease: "power3.in" }, T);
tl.to("#a3 .shade", { opacity: 1, duration: 0.42, ease: "power2.in" }, T);   // the crease darkens
```
Put `perspective` on the scene that holds the halves, not on a parent that also
has `transform` — a transformed ancestor flattens `preserve-3d` and the fold
looks like a squash. Text can fold too: split a line into its two words, one
per half (`transform-origin` at the seam side of each word).

## 25. Seam open

The next shot opens out of the same line the last one folded into:

```js
tl.fromTo("#a4", { clipPath: "inset(0px 958px 0px 958px)" },
                 { clipPath: "inset(0px 0px 0px 0px)", duration: 0.45, ease: "expo.out" }, T + 0.4);
tl.to("#seam", { opacity: 0, duration: 0.25 }, T + 0.5);
```
Fold (24) + open (25) is one signature transition. Used on every act change it
is the film's grammar; the audience reads one idea instead of a sampler.

## 26. Anchor match cut

Two different clips cut as one motion when the same part of the product sits
on the same screen position on both sides of the cut. Find it, don't guess:

```bash
ffmpeg -ss 2.9 -i a.mp4 -frames:v 1 a_end.png; ffmpeg -ss 0.45 -i b.mp4 -frames:v 1 b_start.png
python3 - <<'PY'
import numpy as np; from PIL import Image
for f in ("a_end.png", "b_start.png"):
    a = np.asarray(Image.open(f).convert("RGB")).astype(int)
    m = np.abs(a - a[2, 2]).sum(2) > 24            # not the studio ground
    ys, xs = np.where(m); print(f, "content x", xs.min(), xs.max(), "y", ys.min(), ys.max())
PY
```
Then set each clip's container `x / scale` (in the act's `.cam`) so the hinge
x (or lens centre, or screen corner) is identical in both, and choose
`data-media-start` so the poses match. Cut on a hard ease, no crossfade.

## 27. Pose burst

Several official stills of the product in different poses, each 0.25–0.35 s,
all placed on the same anchor (recipe 26) with a label that changes with them.
It is the one place stills belong in a footage film: the cut rate is the motion.

```js
const poseT = [8.1, 8.4, 8.7, 9.0, 9.3];
poseT.forEach((t, i) => {
  tl.set(`#p${i + 1}`, { opacity: 1 }, t);  tl.set(`#l${i + 1}`, { opacity: 1 }, t);
  if (i < poseT.length - 1) { tl.set(`#p${i + 1}`, { opacity: 0 }, poseT[i + 1]); tl.set(`#l${i + 1}`, { opacity: 0 }, poseT[i + 1]); }
});
tl.fromTo("#posew", { scale: 0.82 }, { scale: 0.9, duration: 1.5, ease: "none" }, 8.1);   // one slow push under the cuts
```
Put a click or a short tick on every pose change in the score.
