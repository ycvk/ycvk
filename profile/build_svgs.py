"""生成主页 README 的动画 SVG：打字机标题与页脚波浪。

用法：uv run profile/build_svgs.py
"""

import math
import random
from html import escape
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
W = 840

LINES = (
    "Hi, I'm Ycvk ~",
    "Go / Rust / TypeScript / Python",
    "Building AI proxies & agents",
    "Software & Content Creation",
    "status: tired... but still shipping",
)
FOOTER_TEXT = "thanks for stopping by ~ OwO"

THEMES = {
    "light": {
        "title": "#96613D",
        "shine": "#E8B47A",
        "accent": "#C58B50",
        "glow": "#FFE1BC",
        "glow_opacity": 0.8,
        "spark": "#D9A066",
        "waves": ("#F6E7D5", "#E6C29A", "#B67B45"),
        "wave_text": "#FFF8EF",
        "paw": "#C58B50",
    },
    "dark": {
        "title": "#E7B98A",
        "shine": "#FFF0DC",
        "accent": "#D3A16D",
        "glow": "#E7B98A",
        "glow_opacity": 0.16,
        "spark": "#F0C999",
        "waves": ("#2B241F", "#4A392B", "#8A6240"),
        "wave_text": "#FFF1E0",
        "paw": "#D3A16D",
    },
}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"

HEADER_H = 120
FONT_SIZE = 28
# 每行用 textLength 锁定为 字数 × CHAR_W，打字遮罩和光标才能在任何等宽字体下对齐
CHAR_W = FONT_SIZE * 0.6
BASELINE = 70
TYPE_MS, HOLD_MS, ERASE_MS, GAP_MS = 85, 1800, 35, 400

FOOTER_H = 150


def num(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def svg(width: int, height: int, defs: list[str], body: list[str]) -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            "<defs>",
            *defs,
            "</defs>",
            *body,
            "</svg>",
            "",
        ]
    )


def discrete(attr: str, frames: list[tuple[int, float]], total: int) -> str:
    times = ";".join(f"{ms / total:.5f}" for ms, _ in frames)
    values = ";".join(num(v) for _, v in frames)
    return (
        f'<animate attributeName="{attr}" calcMode="discrete" dur="{total}ms" '
        f'repeatCount="indefinite" keyTimes="{times}" values="{values}"/>'
    )


def typing_timeline(lines: tuple[str, ...]) -> tuple[list[list[tuple[int, int]]], int]:
    """每行在整个循环里的 (毫秒, 可见字数) 关键帧，以及循环总时长。"""
    tracks = []
    t = 0
    for text in lines:
        n = len(text)
        frames = [(t + i * TYPE_MS, i) for i in range(n + 1)]
        erase_start = t + n * TYPE_MS + HOLD_MS
        frames += [(erase_start + (n - i) * ERASE_MS, i) for i in range(n - 1, -1, -1)]
        tracks.append(frames)
        t = erase_start + n * ERASE_MS + GAP_MS
    return tracks, t


def sparkle_star(x: float, y: float, size: float, color: str, dur: float, begin: float) -> str:
    s = size
    d = f"M0,{-s} Q0,0 {s},0 Q0,0 0,{s} Q0,0 {-s},0 Q0,0 0,{-s}Z"
    return (
        f'<g transform="translate({num(x)},{num(y)})"><path d="{d}" fill="{color}">'
        f'<animateTransform attributeName="transform" type="scale" values="0;1;0;0" keyTimes="0;0.25;0.5;1" '
        f'dur="{num(dur)}s" begin="{num(-begin)}s" repeatCount="indefinite"/></path></g>'
    )


def header_svg(c: dict) -> str:
    tracks, total = typing_timeline(LINES)
    rnd = random.Random(7)

    defs = [
        f'<radialGradient id="glow"><stop offset="0" stop-color="{c["glow"]}" stop-opacity="{c["glow_opacity"]}"/>'
        f'<stop offset="1" stop-color="{c["glow"]}" stop-opacity="0"/></radialGradient>',
        f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">'
        f'<stop offset="0" stop-color="{c["title"]}"/><stop offset="0.44" stop-color="{c["title"]}"/>'
        f'<stop offset="0.5" stop-color="{c["shine"]}"/><stop offset="0.56" stop-color="{c["title"]}"/>'
        f'<stop offset="1" stop-color="{c["title"]}"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" from="-{W} 0" to="{W} 0" '
        f'dur="6s" repeatCount="indefinite"/></linearGradient>',
    ]
    body = [
        f'<ellipse cx="{W / 2}" cy="{BASELINE - 10}" rx="340" ry="56" fill="url(#glow)">'
        f'<animate attributeName="opacity" values="0.55;1;0.55" dur="6s" repeatCount="indefinite"/></ellipse>'
    ]

    for _ in range(18):
        x, y = rnd.uniform(40, W - 40), rnd.uniform(60, HEADER_H - 6)
        r, rise, drift = rnd.uniform(1.0, 2.6), rnd.uniform(35, 65), rnd.uniform(-14, 14)
        dur, peak = rnd.uniform(6, 11), rnd.uniform(0.45, 0.9)
        timing = f'dur="{num(dur)}s" begin="{num(-rnd.uniform(0, dur))}s" repeatCount="indefinite"'
        body.append(
            f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="{c["spark"]}" opacity="0">'
            f'<animate attributeName="cy" from="{num(y)}" to="{num(y - rise)}" {timing}/>'
            f'<animate attributeName="cx" from="{num(x)}" to="{num(x + drift)}" {timing}/>'
            f'<animate attributeName="opacity" values="0;{num(peak)};0" {timing}/></circle>'
        )

    for x, y, size, dur, begin in ((92, 44, 7, 3.2, 0), (750, 38, 8, 3.8, 1.4), (180, 100, 5, 2.9, 2.1), (664, 104, 6, 3.4, 0.7)):
        body.append(sparkle_star(x, y, size, c["accent"], dur, begin))

    body.append(f'<g font-family="{MONO}" font-size="{FONT_SIZE}" font-weight="600" fill="url(#ink)">')
    cursor_frames = []
    for k, (text, frames) in enumerate(zip(LINES, tracks)):
        n = len(text)
        x0 = (W - n * CHAR_W) / 2
        clip_frames = [(ms, v * CHAR_W + (3 if v else 0)) for ms, v in frames]
        if frames[0][0] != 0:
            clip_frames.insert(0, (0, 0))
        defs.append(
            f'<clipPath id="line{k}"><rect x="{num(x0 - 2)}" y="{BASELINE - FONT_SIZE - 2}" '
            f'width="0" height="{FONT_SIZE + 14}">{discrete("width", clip_frames, total)}</rect></clipPath>'
        )
        body.append(
            f'<text x="{num(x0)}" y="{BASELINE}" textLength="{num(n * CHAR_W)}" lengthAdjust="spacing" '
            f'clip-path="url(#line{k})">{escape(text)}</text>'
        )
        cursor_frames += [(ms, x0 + v * CHAR_W + 3) for ms, v in frames]
    body.append("</g>")

    body.append(
        f'<rect x="{num(cursor_frames[0][1])}" y="{BASELINE - FONT_SIZE + 3}" width="3" height="{FONT_SIZE + 2}" '
        f'rx="1.5" fill="{c["accent"]}">{discrete("x", cursor_frames, total)}'
        f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" calcMode="discrete" '
        f'dur="1s" repeatCount="indefinite"/></rect>'
    )
    return svg(W, HEADER_H, defs, body)


def wave_d(base: float, amp: float, wavelength: int, phase: float) -> str:
    length = W + wavelength
    steps = length // 6
    pts = []
    for i in range(steps + 1):
        x = length * i / steps
        y = base + amp * math.sin(2 * math.pi * x / wavelength + phase)
        pts.append(f"{num(x)},{num(y)}")
    return "M" + " L".join(pts) + f" L{length},{FOOTER_H} L0,{FOOTER_H} Z"


def paw(x: float, y: float, color: str, appear: float, cycle: float) -> str:
    t_in, t_full = appear / cycle, (appear + 0.25) / cycle
    t_hold, t_out = (appear + 2.4) / cycle, (appear + 2.9) / cycle
    times = ";".join(f"{t:.4f}" for t in (0, t_in, t_full, t_hold, t_out, 1))
    toes = "".join(
        f'<ellipse cx="{tx}" cy="{ty}" rx="2.3" ry="2.9" transform="rotate({rot} {tx} {ty})"/>'
        for tx, ty, rot in ((-6.2, -3.4, -28), (-2.3, -7.4, -8), (2.3, -7.4, 8), (6.2, -3.4, 28))
    )
    return (
        f'<g transform="translate({num(x)},{num(y)}) rotate(90)" fill="{color}" opacity="0">'
        f'<path d="M0,-0.5 C4.6,-0.5 7.4,3.6 7.4,6.2 C7.4,8.8 5,9.6 3.2,9.2 C1.8,8.9 0.9,8.4 0,8.4 '
        f'C-0.9,8.4 -1.8,8.9 -3.2,9.2 C-5,9.6 -7.4,8.8 -7.4,6.2 C-7.4,3.6 -4.6,-0.5 0,-0.5Z"/>{toes}'
        f'<animate attributeName="opacity" values="0;0;0.9;0.9;0;0" keyTimes="{times}" '
        f'dur="{cycle}s" repeatCount="indefinite"/></g>'
    )


def footer_svg(c: dict) -> str:
    back, mid, front = c["waves"]
    body = []
    for color, base, amp, wavelength, phase, dur, rightward in (
        (back, 86, 8, 280, 0.0, 14, True),
        (mid, 98, 7, 210, 1.3, 10, False),
        (front, 110, 6, 168, 2.1, 7, True),
    ):
        start, end = (-wavelength, 0) if rightward else (0, -wavelength)
        body.append(
            f'<path d="{wave_d(base, amp, wavelength, phase)}" fill="{color}">'
            f'<animateTransform attributeName="transform" type="translate" from="{start} 0" to="{end} 0" '
            f'dur="{dur}s" repeatCount="indefinite"/></path>'
        )

    cycle, step, count = 7, 75, 8
    x_start = (W - step * (count - 1)) / 2
    for i in range(count):
        y = 46 + (-7 if i % 2 == 0 else 7)
        body.append(paw(x_start + i * step, y, c["paw"], 0.3 + i * 0.45, cycle))

    body.append(
        f'<text x="{W / 2}" y="{FOOTER_H - 14}" text-anchor="middle" font-family="{SANS}" font-size="14" '
        f'font-weight="600" letter-spacing="2" fill="{c["wave_text"]}">{escape(FOOTER_TEXT)}</text>'
    )
    return svg(W, FOOTER_H, [], body)


def main() -> None:
    for name, colors in THEMES.items():
        (OUT_DIR / f"header-{name}.svg").write_text(header_svg(colors), encoding="utf-8")
        (OUT_DIR / f"footer-{name}.svg").write_text(footer_svg(colors), encoding="utf-8")


if __name__ == "__main__":
    main()
