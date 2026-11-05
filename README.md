# OBS + Resolve, AI-assisted video workflow

Tools for making a video, from pressing record to the final export: OBS scenes driven by script, a Claude-run rough cut in DaVinci Resolve, and text animation rendered from reveal.js. Each stage is a folder, and each folder's README is its manual.

| Stage | Folder | What's in it |
|---|---|---|
| Capture | [capture/](capture/README.md) | `shoot` (one command to build something with Claude and record it), OBS scripting, the phone mirror, the config check, printable cards |
| Animate | [animate/](animate/README.md) | Text and motion built as a reveal.js deck and rendered to video, frame by frame, with sound |
| Cut | [cut/](cut/README.md) | Media management, transcripts, rough cuts and Resolve project setup, run by Claude |
| Finish | [finish/](finish/README.md) | The final pass in DaVinci Resolve: keyboard preset, keys card, console scripts |

A rendered deck is a clip like any other. A long take and a video built clip by clip go through the same stages. `cut/scripts/ingest.py` takes a dated folder of clips or loose files from the inbox.

## Design

Unix-style, in every stage. Each tool does one thing, takes explicit arguments or stdin, writes to stdout, and holds no state. There is no manifest and no config file. The filesystem is the state, and Claude is the shell. A new tool goes in its stage's folder and follows the same rules.

## The working folder

The tools hold no recordings, settings or personal values. Those live in a separate working folder, `~/reps/video`:

```
inbox/        recordings land here: one "YYYY-MM-DD Topic" folder of clips per video
videos/       one folder per video: footage/ transcripts/ graphics/ resolve/ exports/
rig/          setup.md, LOOK.md, obs/ (known-good OBS files), luts/,
              templates/ (Resolve .drp, brand.json, vocab.json)
.claude/skills/
              links to animate/ and cut/ here, so Claude Code lists both skills
```

[cut/sample/](cut/sample/2026-01-15-acme-sync-demo/README.md) is a synthetic video folder showing what the cut stage generates. Media is gitignored, so only the text artifacts are here.

## Paths

This repo is `~/repos/video`. These hold the working folder's path, `~/reps/video`: `WORK` in `capture/scripts/shoot`, `finish/console_setup.py` and `finish/console_grade.py`, the known-good path in `capture/scripts/check.sh`, `capture/obs/restore.sh` and `capture/obs/snapshot.sh`, and the `--root` default in `cut/scripts/ingest.py` and `cut/scripts/derive.py`. `shoot` also holds the site's path, `~/repos/joelshetler.com`.
