#!/bin/sh
# Verify capture rig state: display modes and OBS config vs known-good.
# The known-good copies are in the working folder's rig/obs/.
# Exits nonzero if anything is off.
set -u
GOOD="$HOME/reps/video/rig/obs"
OBS="$HOME/Library/Application Support/obs-studio"
fail=0

echo "== displays =="
if ! command -v swift >/dev/null 2>&1; then
    echo "swift not found (install Xcode Command Line Tools: xcode-select --install); skipping display check"
    fail=1
fi
modes=$(swift -e '
import CoreGraphics
var ids = [CGDirectDisplayID](repeating: 0, count: 8); var n: UInt32 = 0
CGGetActiveDisplayList(8, &ids, &n)
for i in 0..<Int(n) {
  let kind = CGDisplayIsBuiltin(ids[i]) == 1 ? "builtin" : "external"
  if let m = CGDisplayCopyDisplayMode(ids[i]) {
    print("\(kind) \(m.width)x\(m.height) fb \(m.pixelWidth)x\(m.pixelHeight)")
  }
}' 2>/dev/null)
echo "$modes"
if echo "$modes" | grep -q "external"; then
    if echo "$modes" | grep -q "external 1920x1080 fb 3840x2160"; then
        echo "OK: external monitor in correct HiDPI mode (3840x2160 framebuffer)"
    else
        echo "WRONG: external monitor should be 'looks like 1920x1080' (fb 3840x2160)"
        fail=1
    fi
else
    echo "note: no external monitor connected (laptop-only recording wants builtin 1728x1080, fb 3456x2160)"
fi

echo "== obs config vs known-good =="
# The selected scene, the Chrome window the Browser source points at, and the
# folder shoot picks inside inbox/ change every session, so they don't count as
# differences.
settled() { grep -v -E '"(current_scene|current_program_scene|window)":' "$1" | sed -E 's#(FilePath=.*/inbox)/.*#\1#'; }
for pair in "basic/profiles/LongTake/basic.ini:basic.ini" \
            "basic/profiles/LongTake/recordEncoder.json:recordEncoder.json" \
            "basic/scenes/LongTake.json:LongTake.json"; do
    live="$OBS/${pair%%:*}"
    good="$GOOD/${pair##*:}"
    if [ -r "$live" ] && [ -r "$good" ] && [ "$(settled "$live")" = "$(settled "$good")" ]; then
        echo "OK: ${pair%%:*}"
    else
        echo "DIFFERS: ${pair%%:*}  (diff \"$live\" \"$good\")"
        fail=1
    fi
done

[ "$fail" -eq 0 ] && echo "== all good ==" || echo "== problems found =="
exit "$fail"
