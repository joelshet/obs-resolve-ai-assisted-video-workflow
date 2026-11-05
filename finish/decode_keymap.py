#!/usr/bin/env python3
"""Decode DaVinci Resolve keyboard.preset.xml blob into action -> key list."""
import re
import struct
import sys

QT_SPECIAL = {
    0x01000000: "Esc", 0x01000001: "Tab", 0x01000003: "Backspace", 0x01000004: "Return",
    0x01000005: "Enter", 0x01000006: "Insert", 0x01000007: "Delete", 0x01000010: "Home",
    0x01000011: "End", 0x01000012: "Left", 0x01000013: "Up", 0x01000014: "Right",
    0x01000015: "Down", 0x01000016: "PageUp", 0x01000017: "PageDown", 0x20: "Space",
}
for i in range(1, 25):
    QT_SPECIAL[0x01000030 + i - 1] = f"F{i}"

MODS = [(0x02000000, "Shift"), (0x04000000, "Cmd"), (0x08000000, "Alt"), (0x10000000, "Ctrl")]


def combo_name(v):
    mods = [name for bit, name in MODS if v & bit]
    key = v & 0x01FFFFFF
    if key in QT_SPECIAL:
        k = QT_SPECIAL[key]
    elif 0x20 <= key <= 0x7E:
        k = chr(key)
    else:
        k = f"0x{key:x}"
    return "+".join(mods + [k])


def main():
    xml = open(sys.argv[1]).read()
    blob = bytes.fromhex(re.search(r"<PresetListBA>([0-9a-fA-F]+)", xml).group(1))

    def u32(off):
        return struct.unpack(">I", blob[off:off + 4])[0]

    # find record boundaries: u32 length followed by that many bytes of UTF-16BE ASCII
    records = []
    off = 0
    while off < len(blob) - 8:
        n = u32(off)
        if 4 <= n <= 200 and n % 2 == 0 and off + 4 + n <= len(blob):
            raw = blob[off + 4:off + 4 + n]
            if all(raw[i] == 0 and 0x20 <= raw[i + 1] <= 0x7E for i in range(0, n, 2)):
                name = raw.decode("utf-16-be")
                records.append((off, name))
                off += 4 + n
                continue
        off += 1

    # ints between end of one name and start of next record hold the bindings
    out = []
    for idx, (off, name) in enumerate(records):
        start = off + 4 + len(name) * 2
        end = records[idx + 1][0] if idx + 1 < len(records) else len(blob)
        ints = [u32(i) for i in range(start, end - 3, 4)]
        combos = [v for v in ints if (v & 0x01FFFFFF) and (
            (0x20 <= (v & 0x01FFFFFF) <= 0x7E) or (v & 0x01FFFFFF) in QT_SPECIAL)
            and v not in (1,)]
        out.append((name, [combo_name(v) for v in combos]))
    for name, combos in out:
        print(f"{name}\t{', '.join(combos) if combos else '-'}")


if __name__ == "__main__":
    main()
