---
name: animate
description: >
  Make a short animated video with sound from Joel's own words, built as a
  single-file reveal.js deck and rendered frame by frame. Use when the user
  says "animate this", "make a text video", "turn this into a video", or
  names a deck.html. First action: read ~/reps/video/rig/LOOK.md.
---

# Animate: entry

The tools are in `~/repos/video/animate/`, with their flags in its
`README.md`. Decks live in `~/reps/video/videos/`. Run the commands below
from `~/reps/video`.

1. Read `rig/LOOK.md`. It is a list of what the result must never look
   like. There is no list of what it must always look like.
2. Research, then ask, before any deck exists. For a piece about something
   Joel made, read the thing itself: its README, its background or design
   notes, every example and app, and its page on joelshetler.com. Then bring
   him what you found and the few questions that decide the piece (what it
   should make someone do, which one claim it carries, which example shows
   it). The first example in the README is rarely the right one.
3. Get the words from Joel: an essay on joelshetler.com, a file, or lines he
   types. Use them exactly. Never write, trim or reword his copy. If no words
   were given, ask for them.
4. Start the deck from the one he said yes to:

       mkdir -p videos/YYYY-MM-DD-slug/footage
       cp videos/2026-10-09-reduce-friction/deck.html videos/YYYY-MM-DD-slug/deck.html

   The deck is the whole piece: layout, timing, motion and sound in one file
   that Joel can open in a browser and edit by hand. Keep it that way. Take
   colors, type and layout from `~/repos/joelshetler.com/static/style.css`,
   and sound from `~/repos/video/animate/sound.js`.
5. Render it:

       ~/repos/video/animate/render videos/YYYY-MM-DD-slug/deck.html videos/YYYY-MM-DD-slug/footage/deck.mov --until "window.done" --tail 2.5

6. Check your own work before showing it. Pull six to eight frames into a
   contact sheet with ffmpeg, look at every one against the never list, and
   confirm the file has an audio stream that is not silent.
7. Show Joel the video. A text reveal is not enough: he asked for movement
   and sound. When he rejects something, add it to `rig/LOOK.md` in his words and
   change the deck. When he says yes, say which deck it was in `rig/LOOK.md` so
   the next one can start from it.

The rendered `.mov` is a clip like any other. The cut and finish stages take
it from there.
