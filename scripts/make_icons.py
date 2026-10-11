"""Draws the Quiet DNS home-screen icons into site/icons/.

Run from the project folder:  python3 scripts/make_icons.py

A single clean sine trace on a solid blue square: the tone that Quiet DNS leaves
when the noise is blocked. iOS applies its own corner mask, so the icons are
full-bleed squares with no transparency.
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "site" / "icons"

BACKGROUND = (28, 43, 168)   # #1C2BA8, the signal colour
FOREGROUND = (255, 255, 255)
SUPERSAMPLE = 3              # sub-pixel samples per axis, for smooth edges
CYCLES = 1.5                 # the trace runs one and a half cycles across the icon


def _coverage_rows(size: int) -> list[list[float]]:
    half = 0.04 * size                      # half the stroke width
    amp = 0.17 * size                       # height of the trace above and below the middle
    x0, x1 = 0.17 * size, 0.83 * size       # the trace stops short of the edges
    mid = size / 2
    k = 2 * math.pi * CYCLES / (x1 - x0)    # phase per pixel along the trace
    steps = SUPERSAMPLE * SUPERSAMPLE
    rows = []
    for y in range(size):
        row = []
        for x in range(size):
            hits = 0
            for sy in range(SUPERSAMPLE):
                for sx in range(SUPERSAMPLE):
                    px = x + (sx + 0.5) / SUPERSAMPLE
                    py = y + (sy + 0.5) / SUPERSAMPLE
                    if px < x0:                         # round cap at the start
                        inside = math.hypot(px - x0, py - mid) <= half
                    elif px > x1:                       # round cap at the end
                        inside = math.hypot(px - x1, py - mid) <= half
                    else:
                        phase = k * (px - x0)
                        centre_y = mid - amp * math.sin(phase)
                        slope = -amp * k * math.cos(phase)
                        # distance from the point to the curve, measured across the stroke
                        distance = abs(py - centre_y) / math.sqrt(1 + slope * slope)
                        inside = distance <= half
                    if inside:
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
