# animate

Turns a reveal.js deck into a video. The deck is one HTML file that plays in a browser while you work on it, and renders to the same frames every time.

```bash
animate/render ~/reps/video/videos/2026-10-09-reduce-friction/deck.html out.mov --until "window.done" --tail 2.5
```

`render` writes ProRes 422 HQ at 30 fps, with the deck's sound if it has any. It is a wrapper around two steps you can run yourself:

```bash
python3 animate/scripts/frames.py animate/example.html \
  --until "Reveal.isLastSlide() && !Reveal.availableFragments().next" --tail 2 \
  | ffmpeg -f image2pipe -framerate 30 -i - -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le out.mov
```

`frames.py` writes one PNG per frame to stdout and ffmpeg encodes them. `--audio FILE` saves the deck's sound as a WAV. `--seconds N` renders a fixed length instead of waiting for the deck to end. `--size 1080x1920` renders vertical. `frames.py --help` lists the rest.

## How timing works

Timing lives in the deck. `autoSlide` in `Reveal.initialize` sets the default hold, `data-autoslide="1800"` on a slide or fragment overrides it, and CSS sets how long each transition and animation runs. Open the deck in a browser and it plays at that speed.

A deck with no slides to step through sets `window.done = true` when it finishes, and the render stops on `--until "window.done"`.

For a render, `clock.js` replaces the page's clock. Timers, `requestAnimationFrame`, `Date` and `performance.now` read it, and CSS animations and transitions are paused and set to it. The clock moves one frame at a time, so a slow machine renders the same pixels as a fast one.

## Sound

A deck that loads `sound.js` gets the typebeat synth: `Sound.note(ch)` maps a letter or digit to a pitch on a pentatonic scale from A3, `Sound.tone(hz)` plays it, `Sound.tick()` is the noise click for spaces and punctuation, and `Sound.wave()` returns the newest 2048 output samples for a scope. `Sound.random()` is seeded, so rhythm built on it repeats.

In a browser the sound plays live after the first click or key press. In a render the same code runs on an offline audio context that advances with the page clock, so the scope drawn in each frame and the saved WAV are the same audio.

## Files

| File | What it does |
|---|---|
| `render` | Deck in, ProRes with sound out |
| `scripts/frames.py` | Page in, PNG stream out, and optionally a WAV |
| `sound.js` | The synth and scope source, loaded by a deck |
| `scripts/clock.js` | The page clock, injected before the deck's own scripts |
| `scripts/cdp.py` | Talks to headless Chrome over a pipe. Stdlib only |
| `reveal/` | reveal.js 5.1.0 (`reset.css`, `reveal.css`, `reveal.js`), vendored so decks work offline |
| `example.html` | A three-slide deck with auto-animate, fragments and a CSS animation. A renderer test, not a model for the look |
| `SKILL.md` | The recipe an agent follows for "animate this", linked into `.claude/skills/` |

A deck outside this repo loads reveal and `sound.js` by absolute file URL, for example `file:///Users/joel/repos/video/animate/reveal/reveal.js`.

## Limits

- Needs Google Chrome at `/Applications/Google Chrome.app` and ffmpeg.
- Sound is mono, 48 kHz, and only what `sound.js` makes. Music and voice go on in Resolve.
- `<video>` elements and anything timed by the network run outside the clock and won't stay in step.
- Canvas drawn through `requestAnimationFrame` follows the clock. WebGL is untested.
