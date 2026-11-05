# finish

The final pass in DaVinci Resolve: sync, grade, and the keyboard layout for cutting.

| File | What it does |
|---|---|
| `cheatsheet.html` | Printable card of the keyboard layout |
| `console_setup.py` | Paste into Resolve's Workspace → Console → Py3. Creates a UHD 29.97 project, imports the newest OBS and camera recordings, and stacks them on a timeline |
| `console_grade.py` | Paste into the same console after syncing. Applies the Nicest 709 LUT to camera clips and assigns Camera and Screen color groups, so one grade covers every clip of a kind |
| `keyboard.preset.xml` | Exact copy of the live preset file. This is the restore artifact |
| `keymap_full.tsv` | All 588 actions decoded to readable keys (action, tab, keys) |
| `decode_keymap.py` | Regenerates the TSV: `python3 decode_keymap.py keyboard.preset.xml > keymap_full.tsv` |

Resolve's console has no current folder, so both console scripts name the working folder in `WORK` at their top (`~/reps/video`). They look for recordings in its `inbox/` and for the LUT in its `rig/luts/cube/`.

## Keyboard shortcuts

Preset name in Resolve: **My Keyboard**.

## The asdfqwer edit layout

| Key | Action |
|---|---|
| A | Ripple trim start to playhead (`trimRippleStartToPlayhead`) |
| S | Blade / razor cut at playhead (`editBladeRazor`) |
| D | Ripple trim end to playhead (`trimRippleEndToPlayhead`) |
| F | Match frame (`editMatchFrame`) |
| Q | Toggle source/timeline viewer (`viewViewerToggle`) |
| W | Step one frame back (`controlStepReverse`) |
| E | Step one frame forward (`controlStepForward`) |
| R | Range selection (`editRangeSelection`); the decoder also shows R on `clipChangeClipSpeed`, which may be decoder noise — verify in Resolve if R misbehaves |
| T | Trim Mode (`editTrim`) — comma/period ripple trims only in this mode; added 2026-09-01 |
| C | Normal (pointer) edit mode (`editPointer`) — the way back out of Trim/Blade modes; added 2026-09-01 |

## Restore

1. Quit Resolve.
2. Copy `keyboard.preset.xml` to `~/Library/Preferences/Blackmagic Design/DaVinci Resolve/keyboard.preset.xml`.
3. Open Resolve → DaVinci Resolve menu → Keyboard Customization (Cmd+Alt+K) → pick preset "My Keyboard".

## Snapshot after deliberate changes

Copy the live file back into this folder (reverse of restore step 2), rerun the decoder, commit.
