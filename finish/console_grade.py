# Grade setup for a LongTake timeline. Paste into Workspace > Console > Py3.
#
# Does two things to the CURRENT timeline:
#   1. Applies the Nicest 709 LUT to every camera clip.
#   2. Assigns clips to color groups ("Camera" / "Screen"), so one manual
#      grade covers every clip of a kind.
#
# Clips are identified by their source file, on any video track: camera
# files are P1*.MOV (Panasonic naming), screen recordings live in the
# working folder (inbox/ or videos/). Unrecognized clips are listed and left alone.
#
# Brightness/white balance the right way after running this: Color page,
# select any camera clip, node graph dropdown > Group Pre-Clip, grade there
# once. Group Pre-Clip runs BEFORE each clip's LUT node, so the LUT keeps
# getting clean input, and every camera clip inherits the fix. (The API
# cannot create per-clip nodes, but group pre-clip is the better tool here
# anyway.)

# WORK is the working folder: screen recordings live under it, and its
# rig/luts/cube/ is the second place to look for the LUT.
import os
WORK = os.path.expanduser("~/reps/video")
LUT_NAME_CONTAINS = "nicest"
SCREEN_PATH_CONTAINS = WORK + "/"
LUT_DIRS = [
    "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/VLTs E-L",
    os.path.join(WORK, "rig", "luts", "cube"),
]

import glob
import os

ok = lambda msg: print("  OK  " + msg)
warn = lambda msg: print("  !!  " + msg)

if "resolve" not in dir():
    raise SystemExit("No 'resolve' object - run this inside Resolve's Py3 console.")

proj = resolve.GetProjectManager().GetCurrentProject()
timeline = proj.GetCurrentTimeline()
if not timeline:
    raise SystemExit("No current timeline - open the project/timeline first.")
ok("timeline: " + timeline.GetName())

lut_path = None
for d in LUT_DIRS:
    hits = [p for p in glob.glob(os.path.join(d, "*.cube"))
            if LUT_NAME_CONTAINS in os.path.basename(p).lower()]
    if hits:
        lut_path = hits[0]
        break
if lut_path:
    ok("LUT: " + lut_path)
else:
    warn("no LUT matching '%s' found - LUT step skipped" % LUT_NAME_CONTAINS)

cam_items, scr_items, unknown = [], [], []
for track in range(1, timeline.GetTrackCount("video") + 1):
    for item in timeline.GetItemListInTrack("video", track) or []:
        mpi = item.GetMediaPoolItem()
        path = (mpi.GetClipProperty("File Path") if mpi else "") or ""
        base = os.path.basename(path)
        if base.upper().startswith("P1") and base.upper().endswith(".MOV"):
            cam_items.append(item)
        elif SCREEN_PATH_CONTAINS in path:
            scr_items.append(item)
        else:
            unknown.append(base or item.GetName())
ok("clips: %d camera, %d screen across %d video tracks"
   % (len(cam_items), len(scr_items), timeline.GetTrackCount("video")))
if unknown:
    warn("unrecognized, untouched: " + ", ".join(unknown))

if lut_path:
    try:
        proj.RefreshLUTList()
    except (AttributeError, TypeError):
        pass
    # SetLUT accepts different path forms depending on version; try in order.
    candidates = [
        lut_path,
        os.path.join(os.path.basename(os.path.dirname(lut_path)),
                     os.path.basename(lut_path)),
        os.path.basename(lut_path),
    ]
    applied = 0
    for item in cam_items:
        for cand in candidates:
            if item.SetLUT(1, cand):
                applied += 1
                ok("LUT applied via path form: " + cand)
                break
        else:
            warn("SetLUT refused every path form for " + item.GetName())
    (ok if applied == len(cam_items) else warn)(
        "LUT applied to %d/%d camera clips" % (applied, len(cam_items)))
    if applied < len(cam_items):
        warn("manual fallback: Color page > camera clip > right-click node 1 >"
             " LUT > VLTs E-L > Nicest 709 E-L; if the folder is missing there,"
             " Project Settings > Color Management > Update Lists")

def assign_group(name, items):
    if not items:
        return
    try:
        groups = {g.GetName(): g for g in (proj.GetColorGroupsList() or [])}
        group = groups.get(name) or proj.AddColorGroup(name)
        done = sum(1 for item in items if item.AssignToColorGroup(group))
        (ok if done == len(items) else warn)(
            "group '%s': %d/%d clips" % (name, done, len(items)))
    except (AttributeError, TypeError):
        warn("color group API missing in this Resolve - assign groups by hand "
             "(Color page, select clips, right-click > Assign to New Group)")

assign_group("Camera", cam_items)
assign_group("Screen", scr_items)

print("")
print("Grade once, everywhere: Color page > any camera clip > node graph")
print("dropdown > Group Pre-Clip > fix exposure/white balance there.")
