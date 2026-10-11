"""Draws the Quiet DNS home-screen icons into site/icons/.

Run from the project folder:  python3 scripts/make_icons.py

The icon draws the same wave as the logo on the website, in mint on a near-black square, the colours of the
dark page. iOS applies its own rounded corners, so the icons are full-bleed squares with no transparency.
"""

from __future__ import annotations

import math
import re
import struct
import zlib
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "site" / "icons"

# The logo path from site/index.html. The page's logo and favicon use it too, and a test checks they match.
MARK = "M1.5 12C4 5 7 5 9.5 12S15 19 17.5 12 22 5 22.5 12"
MARK_SCALE = 0.7                 # the logo's 24-unit grid is shown at 70%, which leaves room around it
STROKE = 2.4                     # line width in logo units; a little heavier than the page logo, for small sizes
BACKGROUND = (12, 14, 17)        # #0C0E11, the dark page
FOREGROUND = (143, 216, 194)     # #8FD8C2, the "on" colour
SAMPLES_PER_CURVE = 400          # points along each curve; close together, so the stroke edge is smooth

Point = tuple[float, float]


def _curves(d: str) -> list[tuple[Point, Point, Point, Point]]:
    """The cubic curves of a path made only of absolute M, C and S commands."""
    tokens = re.findall(r"[MCS]|-?\d*\.?\d+", d)
    curves = []
    command = ""
    start: Point = (0.0, 0.0)
    previous_control: Point | None = None
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in ("M", "C", "S"):
            command = token
            i += 1
        elif command == "M":
            start = (float(tokens[i]), float(tokens[i + 1]))
            previous_control = None
            command = ""
            i += 2
        elif command == "C":
            first = (float(tokens[i]), float(tokens[i + 1]))
            second = (float(tokens[i + 2]), float(tokens[i + 3]))
            end = (float(tokens[i + 4]), float(tokens[i + 5]))
            i += 6
            curves.append((start, first, second, end))
            start, previous_control = end, second
        elif command == "S":
            # A smooth curve starts with the reflection of the last control point.
            if previous_control is None:
                first = start
            else:
                first = (2 * start[0] - previous_control[0], 2 * start[1] - previous_control[1])
            second = (float(tokens[i]), float(tokens[i + 1]))
            end = (float(tokens[i + 2]), float(tokens[i + 3]))
            i += 4
            curves.append((start, first, second, end))
            start, previous_control = end, second
        else:
            raise ValueError(f"unsupported path command in the logo: {token!r}")
    return curves


def _point_on(curve: tuple[Point, Point, Point, Point], t: float) -> Point:
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = curve
    u = 1 - t
    a, b, c, d = u * u * u, 3 * u * u * t, 3 * u * t * t, t * t * t
    return (a * x0 + b * x1 + c * x2 + d * x3, a * y0 + b * y1 + c * y2 + d * y3)


def _coverage(size: int) -> list[float]:
    """How much of each pixel the stroke covers, from 0 to 1, in rows from the top."""
    scale = MARK_SCALE * size / 24           # pixels per logo unit
    half = STROKE * scale / 2                # half the stroke width, in pixels
    reach = math.ceil(half) + 2              # how far from a sample point a pixel can be and still matter
    nearest = [math.inf] * (size * size)     # distance from each pixel centre to the nearest point of the line
    for curve in _curves(MARK):
        for n in range(SAMPLES_PER_CURVE + 1):
            x, y = _point_on(curve, n / SAMPLES_PER_CURVE)
            px = size / 2 + (x - 12) * scale
            py = size / 2 + (y - 12) * scale
            for row in range(max(0, int(py) - reach), min(size, int(py) + reach + 1)):
                for col in range(max(0, int(px) - reach), min(size, int(px) + reach + 1)):
                    distance = math.hypot(col + 0.5 - px, row + 0.5 - py)
                    index = row * size + col
                    if distance < nearest[index]:
                        nearest[index] = distance
    # Round ends come for free: the first and last samples are the ends of the line.
    return [min(1.0, max(0.0, half - distance + 0.5)) for distance in nearest]


def _png(size: int, coverage: list[float]) -> bytes:
    raw = bytearray()
    for row in range(size):
        raw.append(0)  # filter type: none
        for col in range(size):
            t = coverage[row * size + col]
            for i in range(3):
                raw += bytes([round(BACKGROUND[i] + (FOREGROUND[i] - BACKGROUND[i]) * t)])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit RGB, no transparency
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, size in [("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]:
        (OUT / name).write_bytes(_png(size, _coverage(size)))
        print(f"wrote {OUT / name} ({size}x{size})")


if __name__ == "__main__":
    main()
