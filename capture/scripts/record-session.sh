#!/bin/sh
# record-session — start a recording session: open the checklist and OBS,
# mirror the phone if one is on USB, then pre-flight the rig. Problems go to
# stderr so the routines menu alerts.
set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"

# As a login item the routines menu has a bare PATH; adb and scrcpy are Homebrew's.
PATH="$PATH:/opt/homebrew/bin:/usr/local/bin"
export PATH

open "$REPO/capture/routine.html"
open -a OBS

problems=""

# The mirror outlives this script, so its complaints go to a file that is read
# once it has had time to fail. A second click leaves a running mirror alone.
phone_pid="" phone_err=""
if command -v adb >/dev/null 2>&1 && adb devices | awk -F'\t' 'NF == 2' | grep -q . \
        && ! pgrep -f 'scrcpy .*--window-title=Phone' >/dev/null; then
    phone_err=$(mktemp)
    nohup "$REPO/capture/scripts/phone.sh" </dev/null >/dev/null 2>"$phone_err" &
    phone_pid=$!
fi

if ! check_out=$("$REPO/capture/scripts/check.sh" 2>&1); then
    problems=$(printf '%s\n' "$check_out" | grep -E "WRONG|DIFFERS|not found|problems")
    [ -n "$problems" ] || problems="$check_out"
fi
if ! system_profiler SPUSBDataType 2>/dev/null | grep -q "Shure MV7"; then
    problems="$problems
MV7+ is not on USB - plug the mic in."
fi

if [ -n "$phone_pid" ]; then
    sleep 3
    if ! kill -0 "$phone_pid" 2>/dev/null; then
        problems="$problems
$(cat "$phone_err")"
    fi
    rm -f "$phone_err"
fi

if [ -n "$problems" ]; then
    printf '%s\n' "$problems" >&2
    exit 1
fi
