#!/bin/sh
# phone — mirror the Android phone on USB into a fixed spot on the laptop
# screen, where the Phone source in OBS's phone scenes records it.
# Taps show as dots. Runs until stopped (Ctrl+C here, Cmd+Q in the window, or
# unplugging the phone). record-session.sh starts it when a phone is on USB.
#
# usage: phone.sh
#   ANDROID_SERIAL picks the phone when more than one is plugged in.
set -u

# The window's place on the laptop screen, in points from its top-left corner.
# The Phone source's crop in capture/obs/LongTake.json is this same rectangle
# in pixels (2x), so change both together. See "Scenes" in setup.md.
X=1052 Y=48 W=488 H=1040

[ $# -eq 0 ] || { echo "usage: phone.sh" >&2; exit 2; }
for tool in adb scrcpy; do
    command -v "$tool" >/dev/null 2>&1 || { echo "phone: $tool not found" >&2; exit 1; }
done

serial="${ANDROID_SERIAL:-}"
if [ -z "$serial" ]; then
    phones=$(adb devices | awk 'NR > 1 && $2 == "device" { print $1 }')
    case $(printf '%s\n' "$phones" | grep -c .) in
        0) echo "phone: no usable phone on USB. Unlock it and allow USB debugging (adb devices shows its state)." >&2; exit 1 ;;
        1) serial="$phones" ;;
        *) echo "phone: several phones on USB; set ANDROID_SERIAL to one of:" >&2
           printf '%s\n' "$phones" >&2; exit 1 ;;
    esac
fi

# Borderless and on top so nothing else lands in the recorded rectangle. The
# aspect lock is off so the window is exactly W by H whatever the phone's shape.
exec scrcpy --serial="$serial" --window-title=Phone \
    --window-borderless --always-on-top --no-window-aspect-ratio-lock \
    --window-x="$X" --window-y="$Y" --window-width="$W" --window-height="$H" \
    --show-touches --stay-awake --no-audio
