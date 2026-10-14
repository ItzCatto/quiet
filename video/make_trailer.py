#!/usr/bin/env python3
"""Render the Quiet DNS launch trailer: 1080x1920, 30 fps, 27 seconds, with synthesized sound.

    python3 video/make_trailer.py        # writes dist/Quiet-DNS-trailer.mp4

Needs Pillow, numpy, fonttools and brotli (to read the site's WOFF2 font), and ffmpeg on the PATH
(or the imageio-ffmpeg package). Everything on screen comes from this repo: the wave mark with the
same path as the site, the Schibsted Grotesk font, the two iPhone pictures in site/tutorial, and
text the app already shows. The phone screens are drawn here, not captured from the app.
"""

from __future__ import annotations

import math
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "dist" / "Quiet-DNS-trailer.mp4"

W, H, FPS, DURATION = 1080, 1920, 30, 27.0
FRAMES = int(round(DURATION * FPS))
SAMPLE_RATE = 48000

# Colours from site/site.css, dark theme.
BG = (12, 14, 17)          # --bg
TEXT = (238, 241, 244)     # --text
TEXT2 = (163, 172, 183)    # --text-2
MINT = (143, 216, 194)     # --on, the logo colour
TRACK = (37, 43, 52)       # --track
INK = BG

# The wave mark, exactly as in site/index.html: a 24-unit box, three cubic curves, round caps.
MARK_UNITS = 24
MARK_STROKE = 2.2
MARK_CURVES = [
    ((1.5, 12), (4, 5), (7, 5), (9.5, 12)),
    ((9.5, 12), (12, 19), (15, 19), (17.5, 12)),
    ((17.5, 12), (20, 5), (22, 5), (22.5, 12)),
]

PHONE_W, PHONE_H = 540, 1170
PHONE_X = (W - PHONE_W) // 2
PHONE_Y = 300
LOGO_SIZE = 520           # scene 2
MARK_SIZE_END = 300       # scene 5

# Copy. The middle phrase replaces "NO ADS." because DNS blocking doesn't stop every ad; see the Help page.
PHRASES = ["LESS NOISE.", "FEWER ADS.", "MORE QUIET."]

_font_file: Path | None = None
_faces: dict[tuple[int, int], ImageFont.FreeTypeFont] = {}


# ---------- type ----------

def convert_font(tmp: Path) -> Path:
    """The site ships a WOFF2 variable font. Pillow reads TTF, so convert it once."""
    ttf = tmp / "schibsted-grotesk.ttf"
    font = TTFont(SITE / "fonts" / "schibsted-grotesk-latin-wght-normal.woff2")
    font.flavor = None
    font.save(ttf)
    return ttf


def face(size: int, weight: int) -> ImageFont.FreeTypeFont:
    key = (size, weight)
    if key not in _faces:
        f = ImageFont.truetype(str(_font_file), size)
        f.set_variation_by_axes([weight])
        _faces[key] = f
    return _faces[key]


def text_width(text: str, f: ImageFont.FreeTypeFont, track: float = 0.0) -> float:
    if track == 0:
        return f.getlength(text)
    return sum(f.getlength(ch) for ch in text) + track * (len(text) - 1)


def fit_size(text: str, weight: int, max_w: float, start: int) -> int:
    size = start
    while size > 20 and text_width(text, face(size, weight)) > max_w:
        size -= 2
    return size


def wrap(text: str, f: ImageFont.FreeTypeFont, max_w: float) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if not line or f.getlength(trial) <= max_w:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def text_mask(text: str, f: ImageFont.FreeTypeFont, cx: float, baseline: float,
              alpha: float = 1.0, track: float = 0.0) -> Image.Image:
    """A full-frame mask for one line of text centred on cx and sitting on the baseline."""
    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)
    fill = int(round(255 * max(0.0, min(1.0, alpha))))
    x = cx - text_width(text, f, track) / 2
    if track == 0:
        draw.text((x, baseline), text, font=f, fill=fill, anchor="ls")
    else:
        for ch in text:
            draw.text((x, baseline), ch, font=f, fill=fill, anchor="ls")
            x += f.getlength(ch) + track
    return mask


# ---------- motion ----------

def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def ramp(t: float, start: float, length: float) -> float:
    return clamp((t - start) / length)


def ease_out(x: float) -> float:
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x: float) -> float:
    x = clamp(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)


# ---------- the logo ----------

def bezier(p0, c1, c2, p1, t: float) -> tuple[float, float]:
    mt = 1 - t
    x = mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t ** 3 * p1[0]
    y = mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t ** 3 * p1[1]
    return x, y


def logo_mask(size: int, progress: float = 1.0, ss: int = 3) -> Image.Image:
    """The wave mark in a size x size mask. progress below 1 draws the start of the line, left to right."""
    n = size * ss
    k = n / MARK_UNITS
    pts: list[tuple[float, float]] = []
    for p0, c1, c2, p1 in MARK_CURVES:
        for i in range(201):
            pts.append(bezier(p0, c1, c2, p1, i / 200))
    pts = [(x * k, y * k) for x, y in pts]
    shown = max(2, int(round(len(pts) * clamp(progress))))
    visible = pts[:shown]

    mask = Image.new("L", (n, n), 0)
    draw = ImageDraw.Draw(mask)
    # A disc at every point of the path. Overlapping discs give a clean edge and round caps at both ends;
    # a single thick polyline leaves slivers at its joints.
    r = MARK_STROKE * k / 2
    for x, y in visible:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=255)
    return mask.resize((size, size), Image.LANCZOS)


def paste_logo(frame: Image.Image, cx: float, cy: float, size: int, alpha: float = 1.0,
               progress: float = 1.0) -> None:
    if alpha <= 0 or progress <= 0:
        return
    mask = logo_mask(size, progress)
    if alpha < 1:
        mask = mask.point(lambda v: int(v * alpha))
    x0 = int(round(cx - size / 2))
    y0 = int(round(cy - size / 2))
    frame.paste(MINT, (x0, y0, x0 + size, y0 + size), mask)


def paint(frame: Image.Image, mask: Image.Image, color=TEXT) -> None:
    frame.paste(color, (0, 0, W, H), mask)


# ---------- phone mockups (drawn at 2x, then reduced for smooth edges) ----------

def ink(color) -> tuple[int, int, int, int]:
    return tuple(color) + (255,)


def phone_screen_dashboard(scr: Image.Image, S: int) -> None:
    d = ImageDraw.Draw(scr)

    def P(v: float) -> int:
        return int(round(v * S))

    def label(x, y, text, size, weight, color, anchor="ls"):
        d.text((P(x), P(y)), text, font=face(P(size), weight), fill=ink(color), anchor=anchor)

    scr.paste(ink(MINT), (P(40), P(100), P(84), P(144)), logo_mask(P(44)))
    label(100, 134, "Quiet DNS", 38, 700, TEXT)

    d.rounded_rectangle((P(84), P(250), P(424), P(394)), radius=P(72), fill=ink(MINT))
    label(124, 322, "On", 40, 700, INK, anchor="lm")
    d.ellipse((P(298), P(282), P(378), P(362)), fill=ink(TEXT))

    label(254, 466, "Quiet DNS is on", 44, 700, TEXT, anchor="ms")
    label(254, 512, "Standard filter, HTTPS", 28, 400, TEXT2, anchor="ms")

    label(40, 600, "Filter", 26, 600, TEXT2)
    x = 40
    for name, selected in (("Standard", True), ("Family", False), ("Unfiltered", False)):
        chip_w = 136
        d.rounded_rectangle((P(x), P(624), P(x + chip_w), P(688)), radius=P(32),
                            fill=ink(TEXT if selected else TRACK))
        label(x + chip_w / 2, 666, name, 24, 600, BG if selected else TEXT, anchor="ms")
        x += chip_w + 12

    note = "Recommended for most people. Blocks ads, trackers and phishing sites."
    for i, line in enumerate(wrap(note, face(P(26), 400), P(428))):
        label(40, 740 + i * 36, line, 26, 400, TEXT2)


def phone_screen_profile(scr: Image.Image, S: int) -> None:
    d = ImageDraw.Draw(scr)

    def P(v: float) -> int:
        return int(round(v * S))

    def label(x, y, text, size, weight, color, anchor="ls"):
        d.text((P(x), P(y)), text, font=face(P(size), weight), fill=ink(color), anchor=anchor)

    label(40, 130, "Profile", 52, 700, TEXT)
    summary = "Encrypted DNS through AdGuard DNS. It blocks ads, trackers and phishing sites."
    for i, line in enumerate(wrap(summary, face(P(28), 400), P(428))):
        label(40, 184 + i * 38, line, 28, 400, TEXT2)

    rows = [("Status", "On, Standard"),
            ("Server", "dns.adguard-dns.com, port 443"),
            ("Protocol", "HTTPS"),
            ("Addresses", "4 included")]
    y = 330
    for key, value in rows:
        label(40, y, key, 22, 600, TEXT2)
        size = fit_size(value, 600, 428, 30)
        label(40, y + 42, value, size, 600, TEXT)
        d.line((P(40), P(y + 72), P(468), P(y + 72)), fill=ink(TRACK), width=P(2))
        y += 110

    d.rounded_rectangle((P(40), P(800), P(468), P(872)), radius=P(36), fill=ink(TEXT))
    label(254, 836, "Download profile", 28, 700, BG, anchor="ms")


PHOTO = None  # set in main from site/tutorial


def phone_screen_photo(scr: Image.Image, S: int) -> None:
    margin = int(round(24 * S))
    width = scr.width - 2 * margin
    img = PHOTO.resize((width, int(round(PHOTO.height * width / PHOTO.width))), Image.LANCZOS)
    corner = Image.new("L", img.size, 0)
    ImageDraw.Draw(corner).rounded_rectangle((0, 0, img.width - 1, img.height - 1),
                                             radius=int(round(40 * S)), fill=255)
    top = (scr.height - img.height) // 2
    scr.paste(img.convert("RGBA"), (margin, top), corner)


def build_phone(draw_screen) -> tuple[Image.Image, Image.Image]:
    """Returns the phone as an RGB image and its alpha, ready to paste onto a frame."""
    S = 2
    w, h = PHONE_W * S, PHONE_H * S
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=96 * S, fill=(24, 27, 32, 255),
                           outline=(52, 58, 67, 255), width=3 * S)
    inset = 16 * S
    sw, sh = w - 2 * inset, h - 2 * inset
    screen = Image.new("RGBA", (sw, sh), ink(BG))
    draw_screen(screen, S)
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh - 1), radius=80 * S, fill=255)
    screen.putalpha(mask)
    img.alpha_composite(screen, (inset, inset))
    draw.rounded_rectangle((w // 2 - 66 * S, inset + 22 * S, w // 2 + 66 * S, inset + 56 * S),
                           radius=17 * S, fill=(0, 0, 0, 255))
    img = img.resize((PHONE_W, PHONE_H), Image.LANCZOS)
    return img.convert("RGB"), img.getchannel("A")


PHONES: dict[str, tuple[Image.Image, Image.Image]] = {}


def paste_phone(frame: Image.Image, name: str, dx: float, dy: float, alpha: float) -> None:
    if alpha <= 0:
        return
    rgb, a = PHONES[name]
    if alpha < 1:
        a = a.point(lambda v: int(v * alpha))
    frame.paste(rgb, (int(round(PHONE_X + dx)), int(round(PHONE_Y + dy))), a)


# ---------- scenes ----------

HERO_SIZE = 0
PHRASE_SIZE = 0


HERO_LEADING = 1.06  # line spacing as a multiple of the hero size


def scene1(frame: Image.Image, t: float) -> None:
    """0-3 s: the hook. Three lines, with the storyboard's words in order."""
    out = 1 - ease_in_out(ramp(t, 2.7, 0.3))
    a1 = ease_out(ramp(t, 0.35, 0.6)) * out
    a2 = ease_out(ramp(t, 1.1, 0.6)) * out
    rise1 = (1 - ease_out(ramp(t, 0.35, 0.6))) * 18
    rise2 = (1 - ease_out(ramp(t, 1.1, 0.6))) * 18
    f = face(HERO_SIZE, 800)
    step = HERO_SIZE * HERO_LEADING
    paint(frame, text_mask("YOUR PHONE.", f, W / 2, H / 2 - step + rise1, a1))
    paint(frame, text_mask("WITHOUT THE", f, W / 2, H / 2 + rise2, a2))
    paint(frame, text_mask("NOISE.", f, W / 2, H / 2 + step + rise2, a2))


def scene2(frame: Image.Image, t: float) -> None:
    """3-7 s: the logo draws itself on, then leaves."""
    draw = ease_in_out(ramp(t, 3.2, 1.5))
    fade = 1 - ease_in_out(ramp(t, 6.6, 0.4))
    paste_logo(frame, W / 2, 960, LOGO_SIZE, alpha=fade, progress=draw)


def phone_motion(t: float, enter_at: float, leave_at: float | None, enter: str):
    """Where a phone is at time t: (dx, dy, alpha), or None when it is not on screen yet."""
    if t < enter_at:
        return None
    e = ease_in_out(ramp(t, enter_at, 0.8))
    dx, dy, alpha = 0.0, 0.0, e
    if enter == "right":
        dx = (1 - e) * 520
    elif enter == "below":
        dy = (1 - e) * 40
    if leave_at is not None:
        l = ease_in_out(ramp(t, leave_at, 0.8))
        dx -= l * 520
        alpha *= 1 - l
    return dx, dy, alpha


def scene3(frame: Image.Image, t: float) -> None:
    """7-13 s: three phone screens, one at a time, with restrained slides."""
    out = 1 - ease_in_out(ramp(t, 12.7, 0.3))
    shows = [
        ("dashboard", "Quiet DNS", 7.0, 8.8, "below"),
        ("profile", "Profile", 8.8, 10.9, "right"),
        ("photo", "VPN & Device Management", 10.9, None, "right"),
    ]
    caption_font = face(34, 600)
    for name, caption, enter_at, leave_at, enter in shows:
        motion = phone_motion(t, enter_at, leave_at, enter)
        if motion is None:
            continue
        dx, dy, alpha = motion
        alpha *= out
        paste_phone(frame, name, dx, dy, alpha)
        paint(frame, text_mask(caption, caption_font, W / 2 + dx, 262, alpha * 0.9), TEXT2)


def scene4(frame: Image.Image, t: float) -> None:
    """13-20 s: three phrases, one at a time."""
    slot = 7.0 / len(PHRASES)
    for i, phrase in enumerate(PHRASES):
        t0 = 13.0 + i * slot
        if t < t0 or t > t0 + slot:
            continue
        a_in = ease_out(ramp(t, t0, 0.35))
        a_out = 1 - ease_in_out(ramp(t, t0 + slot - 0.35, 0.35))
        a = min(a_in, a_out)
        rise = (1 - a_in) * 14
        bar = Image.new("L", (W, H), 0)
        x0 = (W - 120) // 2
        ImageDraw.Draw(bar).rectangle((x0, int(896 + rise), x0 + 120, int(904 + rise)), fill=int(255 * a))
        paint(frame, bar, MINT)
        paint(frame, text_mask(phrase, face(PHRASE_SIZE, 800), W / 2, 1010 + rise, a))


def scene5(frame: Image.Image, t: float) -> None:
    """20-27 s: the logo returns, then the name and the line. Ends on black."""
    out = 1 - ease_in_out(ramp(t, 26.2, 0.7))
    logo_a = ease_in_out(ramp(t, 20.0, 0.6)) * out
    paste_logo(frame, W / 2, 680, MARK_SIZE_END, alpha=logo_a)

    name_a = ease_out(ramp(t, 20.7, 0.5)) * out
    name_rise = (1 - ease_out(ramp(t, 20.7, 0.5))) * 16
    paint(frame, text_mask("QUIET DNS", face(118, 800), W / 2, 1010 + name_rise, name_a, track=12))

    line_a = ease_out(ramp(t, 21.4, 0.5)) * out
    paint(frame, text_mask("Your phone, the way you deserve it.", face(44, 400), W / 2, 1100, line_a), TEXT2)


def frame_at(t: float) -> Image.Image:
    frame = Image.new("RGB", (W, H), BG)
    if t < 3.0:
        scene1(frame, t)
    elif t < 7.0:
        scene2(frame, t)
    elif t < 13.0:
        scene3(frame, t)
    elif t < 20.0:
        scene4(frame, t)
    else:
        scene5(frame, t)
    return frame


# ---------- sound ----------

def _add(buf: np.ndarray, sig: np.ndarray, t0: float) -> None:
    start = int(round(t0 * SAMPLE_RATE))
    end = min(len(buf), start + len(sig))
    if start < len(buf) and end > start:
        buf[start:end] += sig[: end - start]


def _tick(freq: float, dur: float, amp: float) -> np.ndarray:
    n = int(dur * SAMPLE_RATE)
    t = np.arange(n) / SAMPLE_RATE
    env = np.minimum(t / 0.003, 1.0) * np.exp(-t / (dur / 4))
    return amp * np.sin(2 * np.pi * freq * t) * env


def _whoosh(dur: float, amp: float, seed: int) -> np.ndarray:
    n = int(dur * SAMPLE_RATE)
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(n)
    # A band from roughly 300 Hz to 3 kHz: smooth it, then subtract the smoother part.
    low = np.convolve(noise, np.ones(40) / 40, mode="same")
    mid = np.convolve(noise, np.ones(4) / 4, mode="same")
    band = mid - low
    t = np.arange(n) / n
    env = np.sin(np.pi * t) ** 2
    return amp * band / (np.max(np.abs(band)) + 1e-9) * env


def make_sound() -> np.ndarray:
    n = int(DURATION * SAMPLE_RATE)
    buf = np.zeros(n)
    t = np.arange(n) / SAMPLE_RATE

    # A low drone that swells slowly and fades out with the picture.
    env = np.clip(t / 1.2, 0, 1) * np.clip((DURATION - t) / 1.4, 0, 1)
    swell = 0.7 + 0.3 * np.sin(2 * np.pi * 0.09 * t)
    buf += env * swell * (0.028 * np.sin(2 * np.pi * 82.4 * t) + 0.016 * np.sin(2 * np.pi * 123.5 * t))

    _add(buf, _tick(55, 0.7, 0.12), 0.0)                   # a soft opening thud
    _add(buf, _tick(2200, 0.09, 0.045), 3.2)               # the logo starts to draw
    sweep_n = int(1.5 * SAMPLE_RATE)
    st = np.arange(sweep_n) / SAMPLE_RATE
    freq = 320 + (880 - 320) * st / 1.5
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    _add(buf, 0.012 * np.sin(phase) * np.sin(np.pi * st / 1.5), 3.2)
    _add(buf, _whoosh(0.6, 0.03, seed=1), 6.6)
    _add(buf, _tick(1400, 0.05, 0.02), 8.8)
    _add(buf, _tick(1400, 0.05, 0.02), 10.9)
    _add(buf, _whoosh(0.6, 0.03, seed=2), 12.7)
    for i in range(len(PHRASES)):
        _add(buf, _tick(1600, 0.06, 0.035), 13.0 + i * 7.0 / len(PHRASES))
    _add(buf, _whoosh(0.6, 0.03, seed=3), 19.7)
    _add(buf, _tick(1800, 0.07, 0.03), 20.7)
    chime_n = int(2.0 * SAMPLE_RATE)
    ct = np.arange(chime_n) / SAMPLE_RATE
    chime = np.exp(-ct / 0.7) * (0.03 * np.sin(2 * np.pi * 660 * ct) + 0.015 * np.sin(2 * np.pi * 990 * ct))
    _add(buf, chime, 21.4)

    peak = np.max(np.abs(buf))
    if peak > 0.8:
        buf *= 0.8 / peak
    return np.stack([buf, buf], axis=1)


def write_wav(path: Path, stereo: np.ndarray) -> None:
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm.tobytes())


# ---------- encode ----------

def ffmpeg_exe() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
    except ImportError:
        sys.exit("ffmpeg was not found. Install it, or pip install imageio-ffmpeg.")
    return imageio_ffmpeg.get_ffmpeg_exe()


def render(out: Path, tmp: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    sound = tmp / "sound.wav"
    write_wav(sound, make_sound())
    cmd = [
        ffmpeg_exe(), "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(sound),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{DURATION}", "-movflags", "+faststart",
        str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(FRAMES):
            proc.stdin.write(frame_at(i / FPS).tobytes())
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed. Run this again to see its message.")


def main() -> None:
    global _font_file, PHOTO, HERO_SIZE, PHRASE_SIZE
    with tempfile.TemporaryDirectory(prefix="quiet-trailer-") as tmp_name:
        tmp = Path(tmp_name)
        _font_file = convert_font(tmp)
        PHOTO = Image.open(SITE / "tutorial" / "vpn-device-management.jpg").convert("RGB")

        HERO_SIZE = fit_size("WITHOUT THE", 800, 920, 240)
        PHRASE_SIZE = min(fit_size(p, 800, 920, 170) for p in PHRASES)

        PHONES["dashboard"] = build_phone(phone_screen_dashboard)
        PHONES["profile"] = build_phone(phone_screen_profile)
        PHONES["photo"] = build_phone(phone_screen_photo)

        render(OUT, tmp)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
