"""Convert Panasonic .vlt 3D LUTs to Resolve .cube files.

.vlt: integer triplets 0-4095 (12-bit), red index fastest.
.cube: float triplets 0-1, same ordering. Direct line-for-line mapping.
"""
import sys
from pathlib import Path

src_dir = Path(sys.argv[1])
dst_dir = Path(sys.argv[2])
dst_dir.mkdir(parents=True, exist_ok=True)

for vlt in sorted(src_dir.glob("*.vlt")):
    if vlt.name.startswith("._"):
        continue
    lines = vlt.read_text().splitlines()
    size = None
    data = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("LUT_3D_SIZE"):
            size = int(line.split()[1])
            continue
        vals = [int(v) for v in line.split()]
        if len(vals) != 3 or not all(0 <= v <= 4095 for v in vals):
            sys.exit(f"{vlt.name}: bad data line: {line!r}")
        data.append(vals)
    if size is None or len(data) != size ** 3:
        sys.exit(f"{vlt.name}: expected {size}^3 entries, got {len(data)}")
    name = vlt.stem.replace("&", "") + ".cube"
    out = [f'TITLE "{vlt.stem.replace("&", "")}"', f"LUT_3D_SIZE {size}", ""]
    out += [" ".join(f"{v / 4095:.6f}" for v in triplet) for triplet in data]
    (dst_dir / name).write_text("\n".join(out) + "\n")
    print(f"{name}: {size}^3 = {len(data)} entries OK")
