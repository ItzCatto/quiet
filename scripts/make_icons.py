"""Draws the Quiet DNS home-screen icons into site/icons/.

Run from the project folder:  python3 scripts/make_icons.py

A ring with a centre dot on a solid teal square. iOS applies its own corner mask,
so the icons are full-bleed squares with no transparency.
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "site" / "icons"

BACKGROUND = (11, 110, 106)  # #0B6E6A, the accent colour
FOREGROUND = (255, 255, 255)
SUPERSAMPLE = 3              # sub-pixel samples per axis, for smooth edges


def _coverage_rows(size: int) -> list[list[float]]:
    centre = size / 2
    outer = 0.30 * size
    inner = 0.205 * size
    dot = 0.085 * size
    steps = SUPERSAMPLE * SUPERSAMPLE
    rows = []
    for y in range(size):
        row = []
        for x in range(size):
            hits = 0
            for sy in range(SUPERSAMPLE):
                for sx in range(SUPERSAMPLE):
                    px = x + (sx + 0.5) / SUPERSAMPLE - centre
                    py = y + (sy + 0.5) / SUPERSAMPLE - centre
                    d = math.hypot(px, py)
                    if inner <= d <= outer or d <= dot:
                        hits += 1
            row.append(hits / steps)
        rows.append(row)
    return rows


def _png(size: int, coverage: list[list[float]]) -> bytes:
    raw = bytearray()
    for row in coverage:
        raw.append(0)  # filter type: none
        for t in row:
            for i in range(3):
                raw += bytes([round(BACKGROUND[i] + (FOREGROUND[i] - BACKGROUND[i]) * t)])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit RGB
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, size in [("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]:
        (OUT / name).write_bytes(_png(size, _coverage_rows(size)))
        print(f"wrote {OUT / name} ({size}x{size})")


if __name__ == "__main__":
    main()
