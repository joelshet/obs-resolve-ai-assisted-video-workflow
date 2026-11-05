#!/bin/sh
# Capture the live OBS LongTake config into the working folder's rig/obs/ as the new known-good.
set -eu
OBS="$HOME/Library/Application Support/obs-studio"
HERE="$HOME/reps/video/rig/obs"

if pgrep -x OBS >/dev/null; then
    echo "OBS is running. Quit it first so the files on disk are final." >&2
    exit 1
fi

cp "$OBS/basic/profiles/LongTake/basic.ini" "$HERE/basic.ini"
cp "$OBS/basic/profiles/LongTake/recordEncoder.json" "$HERE/recordEncoder.json"
cp "$OBS/basic/scenes/LongTake.json" "$HERE/LongTake.json"
echo "Snapshot taken. Review with: git -C \"$HERE/..\" diff"
