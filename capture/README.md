# capture

Next: `capture/scripts/check.sh` verifies displays and OBS config against known-good.

Tools for the long-take recording setup: Panasonic S5IIX + Shure MV7+ + OBS on the MacBook Pro (M1 Pro), edited in DaVinci Resolve (see [../cut/](../cut/README.md) and [../finish/](../finish/README.md)). The settings reference, known-good OBS files and LUTs live in the working folder, `~/reps/video/rig/`.

## Contents

- **[routine.html](routine.html)** — printable session checklist, start to ship: pre-flight, the five glances, offload, edit steps, export.
- **[s5iix-cheat-sheet.html](s5iix-cheat-sheet.html)** — printable card of the camera's custom-mode recipes: C1 best-quality video to SSD, C2 the long-take recording mode, C3-1/2/3 photo (street, birds, landscape).
- **[obs/restore.sh](obs/restore.sh)** copies `~/reps/video/rig/obs/` (the OBS "LongTake" profile, `basic.ini` and `recordEncoder.json`, and scene collection, `LongTake.json`) into OBS. **[obs/snapshot.sh](obs/snapshot.sh)** copies them back after deliberate changes. Run both with OBS quit.
- **[scripts/check.sh](scripts/check.sh)** — verifies display modes and diffs live OBS config against `~/reps/video/rig/obs/`.
- **[scripts/phone.sh](scripts/phone.sh)** — mirrors the Android phone on USB into a fixed spot on the laptop screen, with taps shown as dots. The OBS scenes with "Phone" in their name record that spot.
- **[scripts/shoot](scripts/shoot)** — `shoot NAME` starts a build-and-record session in one command: draft page, live site, Ghostty, Chrome, the phone mirror and OBS recording into `~/reps/video/inbox/`. Run it again to resume.
- **[scripts/window-id](scripts/window-id)** — prints the window number of a process's largest window.
- **[scripts/obs.py](scripts/obs.py)** — sends one obs-websocket request and prints the reply as JSON.
- **[scripts/vlt2cube.py](scripts/vlt2cube.py)** — converts the camera's .vlt LUTs to Resolve's .cube.
- **[scripts/record-session.sh](scripts/record-session.sh)** — the "start a session" one-click: opens the checklist and OBS, starts the phone mirror when a phone is on USB, pre-flights the rig, alerts on problems. Launched from the routines menu via `~/routines/record-session.sh`.

## Settings that live outside this repo

- **Camera**: saved on the camera itself in **Custom Mode C2** (camera menu: Setup → Setting → Save to Custom Mode), so a messed-up camera restores by turning the mode dial to C2. The full slot layout is on the [cheat sheet](s5iix-cheat-sheet.html).
- **Mic**: MV7+ stores its DSP and gain on the device. Reapply via Shure MOTIV Mix.
- **Displays**: verified by `scripts/check.sh`.
- **OBS, LUTs and every value**: `~/reps/video/rig/`: `setup.md`, `obs/` and `luts/`.

## New machine (up and running in minutes)

1. Install: [OBS Studio](https://obsproject.com), [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) (free), [Shure MOTIV Mix](https://www.shure.com/en-US/motiv-software), and Xcode Command Line Tools (`xcode-select --install`, needed by `scripts/check.sh`).
2. Clone this repo to `~/repos/video` and the working folder to `~/reps/video`. Run `capture/obs/restore.sh` (creates the LongTake profile and scene collection; open OBS and pick both in the Profile and Scene Collection menus).
3. Open OBS once and grant macOS the **Screen Recording** and **Microphone** permissions when prompted.
4. **Re-pick the display**: the scene's Screen source is bound to a specific monitor's UUID. On new hardware it captures black — right-click the Screen source → Properties → select the recording display. Set that display to "looks like 1920×1080" (HiDPI) if it's a 4K monitor.
5. Resolve keyboard: follow the restore steps in [../finish/README.md](../finish/README.md).
6. LUTs (only for V-Log shoots): install per `~/reps/video/rig/luts/README.md`.
7. Menu-bar routine: the hammer menu and its `record-session` launcher come with the launchers repo (`~/tools/launchers/install.sh`).
8. Phone scenes: `brew install scrcpy android-platform-tools`, then turn on USB debugging on the phone and allow this Mac when the phone asks.
9. Run `capture/scripts/check.sh`. Displays and OBS config should verify green.

The mic needs no setup on a new computer: its settings live on the device, and OBS's mic source is bound to the MV7+'s serial number, which travels with the mic. The camera likewise carries its own settings (Custom Mode C2).
