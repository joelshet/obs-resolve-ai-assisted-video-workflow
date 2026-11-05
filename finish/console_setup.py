# LongTake project bootstrapper for DaVinci Resolve.
# Use: Workspace > Console > Py3, paste this whole file, press Enter.
#
# Creates a UHD 29.97 project, imports the newest OBS recording and the
# newest camera file it can find, and stacks them on a timeline
# (screen on V1, camera on V2). Sync and edit are yours from there.
#
# Override the search locations here if files live somewhere else.
# WORK is the working folder that holds inbox/.
import os
WORK = os.path.expanduser("~/reps/video")
OBS_DIR = os.path.join(WORK, "inbox")
CAMERA_GLOBS = [
    "/Volumes/*/P1*.MOV",
    "/Volumes/*/DCIM/*/P1*.MOV",
]

import datetime
import glob
import os

ok = lambda msg: print("  OK  " + msg)
warn = lambda msg: print("  !!  " + msg)

if "resolve" not in dir():
    raise SystemExit("No 'resolve' object - run this inside Resolve's Py3 console.")

pm = resolve.GetProjectManager()
name = "LongTake " + datetime.date.today().isoformat()
proj = pm.CreateProject(name)
if not proj:
    name += datetime.datetime.now().strftime(" %H%M")
    proj = pm.CreateProject(name)
ok("project: " + name)

# Settings must land before the first timeline exists.
for key, val in [
    ("timelineResolutionWidth", "3840"),
    ("timelineResolutionHeight", "2160"),
    ("timelineFrameRate", "29.97"),
    ("timelinePlaybackFrameRate", "29.97"),
]:
    if proj.SetSetting(key, val):
        ok(key + " = " + val)
    else:
        warn(key + " refused " + val)

def newest(paths):
    paths = [p for p in paths if os.path.isfile(p)]
    return max(paths, key=os.path.getmtime) if paths else None

screen_path = newest(glob.glob(os.path.join(OBS_DIR, "*.mov")))
cam_candidates = [p for pat in CAMERA_GLOBS for p in glob.glob(pat)]
cam_path = newest(cam_candidates)

media = resolve.GetMediaStorage()
pool = proj.GetMediaPool()
clips = {}
for label, path in [("screen", screen_path), ("camera", cam_path)]:
    if not path:
        warn("no %s file found - import it by hand" % label)
        continue
    added = media.AddItemListToMediaPool([path])
    if added:
        clips[label] = added[0]
        ok("imported %s: %s" % (label, os.path.basename(path)))
    else:
        warn("import failed for " + path)

timeline = pool.CreateEmptyTimeline("Main")
ok("timeline: Main (3840x2160 @ 29.97)")

if "screen" in clips:
    pool.AppendToTimeline([clips["screen"]])
    ok("screen on V1")
if "camera" in clips:
    timeline.AddTrack("video")
    placed = pool.AppendToTimeline([{
        "mediaPoolItem": clips["camera"],
        "trackIndex": 2,
        "recordFrame": timeline.GetStartFrame(),
    }])
    if placed:
        ok("camera on V2")
    else:
        warn("stacking on V2 not supported here - drag the camera clip onto V2 by hand")

pm.SaveProject()
ok("saved")
print("")
print("Next, by hand (not scriptable): select both clips, right-click >")
print("Auto Align Clips > Based on Waveform; mute the OBS audio track;")
print("Playback > Timeline Proxy Resolution > Half if scrubbing drags.")
