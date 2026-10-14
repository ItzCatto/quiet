# Quiet DNS launch trailer

A 24-second vertical video for phones: 1080 × 1920, 30 fps, H.264 with AAC sound. `make_trailer.py` renders every frame and the sound from the project's own files, then encodes the MP4 with ffmpeg.

```
python3 video/make_trailer.py      # writes dist/Quiet-DNS-trailer.mp4
```

You need Python 3 with Pillow, numpy, fonttools and brotli (`pip install pillow numpy fonttools brotli`), and ffmpeg on the PATH. If ffmpeg isn't installed, `pip install imageio-ffmpeg` is used instead. The render takes under a minute.

## Editing plan

### Assets inspected

| Asset | What it is | Used for |
|---|---|---|
| The wave mark in `site/index.html` | The logo: a 24-unit box with three cubic curves and round ends. The same path as the site and the home-screen icon. | Scenes 2, 3 and 5. Drawn from the same coordinates, not retraced. |
| `site/fonts/schibsted-grotesk-latin-wght-normal.woff2` | The site's bundled variable font. | All text. Converted to TTF once so Pillow can read it. |
| `site/site.css` (dark theme) | Background, text, secondary text, the mint "on" colour, the track colour. | The palette. |
| `site/tutorial/vpn-device-management.jpg` | A real iPhone screenshot of Settings › VPN & Device Management. | Not used in this cut. |
| `site/tutorial/settings-general.jpg` | A second Settings screenshot. | Not used. It is blurry at the size needed. |

No separate logo file was supplied, so the wave mark from the site is the logo. It is the same path the app uses.

### Storyboard as built

| Time | Scene | What happens |
|---|---|---|
| 0–2 s | Hook | "YOUR PHONE.", "WITHOUT THE", "NOISE." land one per half-second, each with a hard snap. |
| 2–4 s | Logo | The wave draws on fast from left to right in mint, then snaps away. |
| 4–9 s | Wave rows | The wave mark in three rows, moving at different speeds. The middle row is mint, the outer rows are muted. No app screens are shown. |
| 9–15 s | Promise | "LESS NOISE.", "FEWER ADS.", "MORE QUIET.", two seconds each. Each opens a mint hairline from the centre, then the words land above it. |
| 15–23.2 s | Close | The logo settles into place from slightly larger, then "QUIET DNS", "Your phone, the way you deserve it.", and "COMING SOON" in mint at 21 s. |
| 23.2–24 s | End | Fades to a plain black final frame. |

### Copy decisions

- The middle phrase is "FEWER ADS.", not "NO ADS.". DNS blocking can't stop every ad, because some ads are served from the same site as the content. The app's Help page says this, so the trailer doesn't claim more.
- "COMING SOON" sits under the closing line, in place of any app screens.
- No feature is mentioned that the app doesn't have.

### Look and sound

- Dark background, mint only for the logo, the bars, and the one "on" colour. No stock footage, no glow, no particles.
- Pace: every cut lands on a 120 BPM grid (0.5 s). Lines snap in with a fast ease-out and no bounce.
- Luxury comes from restraint: wide negative space, a thin mint hairline, a tracked-out name, and a logo that settles slowly at the end before the picture fades to black.
- Sound is synthesized: a falling low thump on each cut, ticks as lines land and on each half-beat through the wave rows, a rising sweep as the logo draws, short whooshes before the wave rows and the promises, a tick when COMING SOON lands, and a chime when the name lands. It peaks around −12 dB.

### Limits

- No app screens appear in this cut. The 4–9 s wave rows use the logo mark only.
- The sound is generated, not recorded or licensed music.
- The video has no captions or voice-over.

## Files

- `make_trailer.py`: the whole renderer. Constants at the top (sizes, timings, copy, colours) are the first place to edit.
- `README.md`: this file.
- `dist/Quiet-DNS-trailer.mp4`: the output. It is built, not committed.
