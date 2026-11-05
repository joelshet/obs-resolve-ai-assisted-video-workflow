#!/bin/sh
# Restore known-good OBS LongTake profile and scene collection from the working folder's rig/obs/.
set -eu
OBS="$HOME/Library/Application Support/obs-studio"
HERE="$HOME/reps/video/rig/obs"

if pgrep -x OBS >/dev/null; then
    echo "OBS is running. Quit it first; it overwrites config on exit." >&2
    exit 1
fi

mkdir -p "$OBS/basic/profiles/LongTake" "$OBS/basic/scenes"
cp "$HERE/basic.ini" "$OBS/basic/profiles/LongTake/basic.ini"
cp "$HERE/recordEncoder.json" "$OBS/basic/profiles/LongTake/recordEncoder.json"
cp "$HERE/LongTake.json" "$OBS/basic/scenes/LongTake.json"
echo "Restored LongTake profile and scene collection. Open OBS and check Profile/Scene Collection menus point at LongTake."
echo "On a new machine or monitor: the Screen source is bound to a display UUID — re-pick the display in the source's Properties if the preview is black."
