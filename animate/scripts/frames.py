#!/usr/bin/env python3
"""Step a web page through its own clock; write one PNG per frame to stdout.

  frames.py DECK.html --seconds 13 | ffmpeg -f image2pipe -framerate 30 -i - out.mov
  frames.py DECK.html --until "Reveal.isLastSlide() && !Reveal.availableFragments().next" --tail 2 | ffmpeg ...

clock.js replaces the page's timers and pins CSS animations and transitions
to the same clock, so every frame is a pure function of time: the same page
renders to the same pixels every run, at any speed the machine manages.
Timing lives in the page (reveal.js autoSlide, data-autoslide, CSS durations).

A deck that loads sound.js renders its audio in step with the frames;
--audio FILE saves it as a WAV. Needs Google Chrome. <video> elements and
network-timed content are outside the clock and will not render in step.
"""
import argparse
import base64
import sys
import time
from pathlib import Path

from cdp import Chrome

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("page", help="HTML file to render")
ap.add_argument("--fps", type=float, default=30)
ap.add_argument("--size", default="1920x1080", help="WIDTHxHEIGHT (default 1920x1080)")
ap.add_argument("--seconds", type=float, help="stop after this much page time")
ap.add_argument("--until", help="JS expression; stop once it is true")
ap.add_argument("--tail", type=float, default=0, help="seconds to keep rendering after --until")
ap.add_argument("--ready", default="document.readyState === 'complete' && (!window.Reveal || Reveal.isReady())",
                help="JS expression that is true once the page can start")
ap.add_argument("--max", type=float, default=600, help="give up after this much page time (default 600)")
ap.add_argument("--audio", help="write the deck's sound to this WAV file")
a = ap.parse_args()
if a.seconds is None and a.until is None:
    ap.error("give --seconds or --until")
if not Path(a.page).is_file():
    sys.exit(f"{a.page}: no such file")
if sys.stdout.isatty():
    sys.exit("frames.py writes PNG data to stdout; pipe it to ffmpeg")

w, h = map(int, a.size.split("x"))
c = Chrome(w, h)
c.open("about:blank")
c.send("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
length = (a.seconds if a.seconds is not None else a.max) + a.tail + 1
c.send("Page.addScriptToEvaluateOnNewDocument",
       source=f"window.__render = {{ seconds: {length}, sampleRate: 48000 }};\n"
              + Path(__file__).with_name("clock.js").read_text())
url = Path(a.page).resolve().as_uri()
c.send("Page.navigate", url=url)
for _ in range(400):  # zero-delay timers run while loading; no page time passes
    if c.js(f"location.href.split('#')[0] === {url!r} && typeof __advance === 'function'"):
        c.js("__advance(0)")
        if c.js(a.ready):
            break
    time.sleep(0.05)
else:
    sys.exit(f"{a.page}: never became ready ({a.ready})")

step = 1000 / a.fps
limit = round(a.fps * (a.seconds if a.seconds is not None else a.max))
tail = None
frame = 0
while frame < limit:
    sys.stdout.buffer.write(base64.b64decode(c.send("Page.captureScreenshot", format="png")["data"]))
    frame += 1
    if a.until and tail is None and c.js(f"!!({a.until})"):
        tail = round(a.fps * a.tail)
    if tail is not None:
        if tail == 0:
            break
        tail -= 1
    c.js(f"__advance({step})")
else:
    if a.until:
        sys.exit(f"{a.page}: --until never became true within {a.max:g}s of page time")
if a.audio:
    if c.js("typeof __audioWav === 'function'"):
        size = c.js(f"__audioWav({frame / a.fps})")
        with open(a.audio, "wb") as f:
            for start in range(0, size, 1 << 20):
                f.write(base64.b64decode(c.js(f"__audioChunk({start}, {1 << 20})")))
    else:
        print(f"{a.page}: no sound.js, so no {a.audio}", file=sys.stderr)
print(f"{frame} frames, {frame / a.fps:.2f}s", file=sys.stderr)
