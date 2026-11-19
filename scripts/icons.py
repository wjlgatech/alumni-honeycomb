"""Rasterize the app icon (an open door with two people in it) without any image library.

Pure Python (zlib + struct) so it runs on any machine; output is deterministic.
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

ORANGE, IVORY = (0xD9, 0x77, 0x57), (0xFA, 0xF9, 0xF5)


def pixel(x: float, y: float, inset: float) -> tuple[int, int, int]:
    """Colour at (x, y) in a 512-unit canvas; `inset` shrinks the mark toward the centre (maskable)."""
    c = 256
    x, y = c + (x - c) / inset, c + (y - c) / inset
    in_door = 156 <= x <= 356 and ((y >= 236 and y <= 420) or (x - 256) ** 2 + (y - 236) ** 2 <= 100 ** 2)
    in_person = (x - 226) ** 2 + (y - 330) ** 2 <= 22 ** 2 or (x - 286) ** 2 + (y - 330) ** 2 <= 22 ** 2
    return IVORY if in_door and not in_person else ORANGE


def png(size: int, inset: float = 1.0) -> bytes:
    """Return PNG bytes of the icon at `size` px."""
    rows = bytearray()
    for j in range(size):
        rows.append(0)
        for i in range(size):
            rows.extend(pixel((i + 0.5) * 512 / size, (j + 0.5) * 512 / size, inset))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    head = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head) + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b"")


def main(out: Path) -> None:
    """Write every icon size the manifest and head tags name."""
    for name, size, inset in (("icon-192.png", 192, 1.0), ("icon-512.png", 512, 1.0),
                              ("icon-512-maskable.png", 512, 1.25), ("apple-touch-icon.png", 180, 1.0),
                              ("favicon.png", 48, 1.0)):
        (out / name).write_bytes(png(size, inset))
        print(f"wrote {name}")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "web"))
