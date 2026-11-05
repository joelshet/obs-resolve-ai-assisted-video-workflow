# Video tools

The tools for Joel's video workflow, in four stage folders: `capture/` (the recording rig, and `shoot`), `animate/` (reveal.js decks rendered to video), `cut/` (the new-video-project skill and its scripts), `finish/` (Resolve keyboard preset and console scripts). This repo is public on GitHub as `obs-resolve-ai-assisted-video-workflow`.

The work happens in the private working folder, `~/reps/video`: `inbox/` for recordings, `videos/` with one folder per video, and `rig/` for settings, LUTs, templates, known-good OBS files and `LOOK.md`. Its `CLAUDE.md` is about Joel and his devices. Read it before working on a video.

## Design rules

Unix-style. Joel depends on this to keep the project in his head and maintain it for years, so hold to it. Each tool does one thing, takes explicit arguments or stdin, writes to stdout, sends errors to stderr, and holds no state. No manifest, no config file, no interactive prompts. The filesystem is the state. Layout, naming and editorial judgment live in SKILL.md and EDIT.md prose. Extend the repo by adding a small tool to the right stage folder, never by growing an existing tool a second job.

## What goes where

- Joel doesn't run the tools himself, except `shoot`. Claude runs them by their path in this repo, and they work from any folder. The README's "Paths" section lists every tool that holds the working folder's path.
- Anything true only of Joel's machine, devices or taste goes in the working folder, never here: device and display IDs, serials, settings values, LUTs, his notes. Check a change for these before committing, because this repo is public.

## Animate and cut

Follow `animate/SKILL.md` for "animate this" and `cut/SKILL.md` for "new video in inbox". Both are linked into `.claude/skills/` here and in the working folder.

## OBS rules

- Never edit OBS config files while OBS is running; it overwrites them on exit. Quit OBS first (`pgrep -x OBS` to check).
- OBS shows an "unclean shutdown" dialog if it was killed rather than quit; leftover `run_*` files in `~/Library/Application Support/obs-studio/.sentinel/` cause it when OBS is not running. Delete them only then.
- obs-websocket runs on port 4455 (password in `~/Library/Application Support/obs-studio/plugin_config/obs-websocket/config.json`). `capture/scripts/obs.py` sends one request.

The local SSH key belongs to another GitHub account, so `gh repo clone` fails. Use HTTPS remotes.
