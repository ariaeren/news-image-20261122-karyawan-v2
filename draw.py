#!/usr/bin/env python3
"""Deterministically draw the 22 Nov 2026 world-news entry image.

Build-time only: the grader never runs this file. It uses Pillow and the
system DejaVu fonts, writes one 1024x1024 PNG, and contains no timestamps,
randomness or network access.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

BG = (11, 19, 43)          # #0B132B
CARD = (15, 27, 54)        # #0F1B36
STRIP = (14, 26, 52)       # #0E1A34
GRID = (16, 28, 53)
TEXT = (247, 250, 255)
MUTED = (206, 220, 239)
DIM = (145, 167, 202)
CYAN = (86, 222, 235)
AMBER = (255, 183, 77)
RED = (255, 107, 107)
BLUE = (112, 166, 255)
VIOLET = (191, 147, 255)
TEAL = (94, 222, 185)

REG_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD_PATH if bold else REG_PATH, size)


F_TINY = font(True, 20)
F_LEAD = font(False, 28)
F_SMALL = font(True, 23)
F_DETAIL = font(False, 25)
F_HEAD = font(True, 33)
F_SUB = font(True, 38)
F_DATE = font(True, 94)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(x * t + y * (1 - t)) for x, y in zip(a, b))


def put(d: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill, maxw: int | None = None) -> None:
    if maxw is not None:
        width = fnt.getlength(text)
        if width > maxw:
            raise ValueError(f"text too wide ({width:.1f} > {maxw}): {text!r}")
    d.text(xy, text, font=fnt, fill=fill, anchor="lt")


def wrap(text: str, fnt, maxw: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if fnt.getlength(candidate) <= maxw:
            current = candidate
        else:
            if not current:
                raise ValueError(f"word does not fit: {word!r}")
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > 2:
        raise ValueError(f"detail needs more than two lines: {text!r} -> {lines!r}")
    return lines


def outlined_polygon(d: ImageDraw.ImageDraw, points, color, width: int = 2) -> None:
    d.line(list(points) + [points[0]], fill=color, width=width, joint="curve")


def icon(d: ImageDraw.ImageDraw, kind: str, cx: int, cy: int, color) -> None:
    """Small vector glyph drawn inside a 42px badge."""
    if kind == "globe":
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=color, width=2)
        d.line([cx - 14, cy, cx + 14, cy], fill=color, width=2)
        d.ellipse([cx - 6, cy - 14, cx + 6, cy + 14], outline=color, width=2)
    elif kind == "gulf":
        d.rectangle([cx - 11, cy - 8, cx - 6, cy + 12], outline=color, width=2)
        d.rectangle([cx - 2, cy - 13, cx + 3, cy + 12], outline=color, width=2)
        d.line([cx + 5, cy + 12, cx + 14, cy + 12], fill=color, width=2)
        d.line([cx + 9, cy - 15, cx + 9, cy - 5], fill=color, width=2)
        d.line([cx + 4, cy - 10, cx + 14, cy - 10], fill=color, width=2)
    elif kind == "ship":
        outlined_polygon(
            d,
            [(cx - 15, cy + 3), (cx + 15, cy + 3), (cx + 9, cy + 13), (cx - 9, cy + 13)],
            color,
        )
        d.line([cx, cy + 3, cx, cy - 7], fill=color, width=2)
        d.line([cx - 8, cy + 17, cx + 8, cy + 17], fill=color, width=2)
        d.line([cx + 7, cy - 14, cx + 13, cy - 8], fill=color, width=2)
        d.line([cx + 13, cy - 14, cx + 7, cy - 8], fill=color, width=2)
    elif kind == "capitol":
        outlined_polygon(d, [(cx - 16, cy - 1), (cx, cy - 15), (cx + 16, cy - 1)], color)
        for dx in (-11, -4, 4, 11):
            d.line([cx + dx, cy, cx + dx, cy + 10], fill=color, width=2)
        d.rectangle([cx - 15, cy + 10, cx + 15, cy + 14], outline=color, width=2)
    elif kind == "exam":
        d.rectangle([cx - 13, cy - 14, cx + 1, cy + 13], outline=color, width=2)
        for dy in (-8, -2, 4):
            d.line([cx - 9, cy + dy, cx - 3, cy + dy], fill=color, width=2)
        d.rectangle([cx + 5, cy + 1, cx + 14, cy + 10], outline=color, width=2)
        for dy in (-3, 3, 9, 15):
            if cy + dy <= cy + 14:
                d.line([cx + 7, cy + dy, cx + 12, cy + dy], fill=color, width=1)
    elif kind == "disaster":
        outlined_polygon(
            d,
            [(cx - 2, cy - 16), (cx + 6, cy - 7), (cx + 3, cy + 1), (cx - 6, cy + 1), (cx - 8, cy - 7)],
            color,
        )
        outlined_polygon(
            d,
            [(cx - 14, cy + 7), (cx + 14, cy + 7), (cx + 9, cy + 14), (cx - 9, cy + 14)],
            color,
        )
    else:
        raise ValueError(f"unknown icon: {kind}")


def big_globe(d: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    r = 45
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CYAN, width=3)
    d.line([cx - r, cy, cx + r, cy], fill=CYAN, width=2)
    d.ellipse([cx - 17, cy - r, cx + 17, cy + r], outline=CYAN, width=2)
    d.arc([cx - r, cy - 18, cx + r, cy + 18], start=195, end=345, fill=CYAN, width=2)


def draw_card(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, data: dict) -> None:
    accent = data["accent"]
    d.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=CARD, outline=accent, width=2)
    d.rounded_rectangle([x + 1, y + 15, x + 7, y + h - 15], radius=3, fill=accent)

    badge_cx = x + 40
    badge_cy = y + 40
    d.ellipse(
        [badge_cx - 21, badge_cy - 21, badge_cx + 21, badge_cy + 21],
        fill=mix(accent, CARD, 0.18),
        outline=accent,
        width=2,
    )
    icon(d, data["icon"], badge_cx, badge_cy, accent)

    put(d, (x + 70, y + 18), data["kicker"], F_SMALL, accent, maxw=w - 88)
    put(d, (x + 18, y + 60), data["headline"], F_HEAD, TEXT, maxw=w - 36)

    d.line([x + 18, y + 102, x + w - 18, y + 102], fill=mix(accent, CARD, 0.45), width=1)

    lines = wrap(data["detail"], F_DETAIL, w - 36)
    start_y = y + 112 if len(lines) == 2 else y + 126
    for i, line in enumerate(lines):
        put(d, (x + 18, start_y + i * 34), line, F_DETAIL, MUTED, maxw=w - 36)


def main() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Quiet editorial grid: structure without competing with the cards.
    for gx in range(0, W, 64):
        d.line([gx, 0, gx, H], fill=GRID, width=1)
    for gy in range(0, H, 64):
        d.line([0, gy, W, gy], fill=GRID, width=1)

    d.rectangle([0, 0, W, 8], fill=CYAN)

    put(d, (36, 20), "ONE DAY · SIX STORIES · 22 NOV 2026", F_TINY, DIM, maxw=700)
    put(d, (34, 48), "22 NOV 2026", F_DATE, TEXT, maxw=790)
    put(d, (38, 150), "SUNDAY · WORLD NEWS", F_SUB, CYAN, maxw=700)
    big_globe(d, 928, 86)

    d.line([38, 199, 986, 199], fill=(35, 57, 94), width=2)
    put(
        d,
        (38, 209),
        "UN TALKS STALL · GULF STRIKES · DEMOCRATS WIN HOUSE",
        F_LEAD,
        TEXT,
        maxw=930,
    )

    cards = [
        {
            "kicker": "CLIMATE · ANTALYA, TURKEY",
            "headline": "CLIMATE TALKS FAIL",
            "detail": "Fossil-fuel wording blocks UN deal in Antalya",
            "accent": CYAN,
            "icon": "globe",
        },
        {
            "kicker": "GULF · BAHRAIN-HORMUZ",
            "headline": "IRAN STRIKES GULF",
            "detail": "Bahrain site hit; two wounded; Hormuz tankers struck",
            "accent": AMBER,
            "icon": "gulf",
        },
        {
            "kicker": "LIBYA · UKRAINE WAR",
            "headline": "WAR REACHES LIBYA",
            "detail": "Suspected drone strike hits Russian corvette at Benghazi",
            "accent": RED,
            "icon": "ship",
        },
        {
            "kicker": "USA · ELECTION",
            "headline": "US BLUE WAVE",
            "detail": "Democrats take 258+ House seats, largest since 1992",
            "accent": BLUE,
            "icon": "capitol",
        },
        {
            "kicker": "SOUTH KOREA · AI",
            "headline": "AI EXAM SCANDAL",
            "detail": "South Korean education minister resigns",
            "accent": VIOLET,
            "icon": "exam",
        },
        {
            "kicker": "ASIA + AFRICA · DISASTERS",
            "headline": "DISASTERS",
            "detail": "Indonesia factory fire: 3 dead, 36 missing; Nigeria boat toll 24",
            "accent": TEAL,
            "icon": "disaster",
        },
    ]

    card_w, card_h, gap = 464, 196, 14
    xs = (32, 528)
    ys = (252, 462, 672)
    for i, data in enumerate(cards):
        draw_card(d, xs[i % 2], ys[i // 2], card_w, card_h, data)

    # Source strip.
    d.rectangle([0, 892, W, H], fill=STRIP)
    d.line([0, 892, W, 892], fill=CYAN, width=3)
    put(d, (38, 908), "SIX STORIES · SIX REGIONS", F_TINY, DIM, maxw=400)
    accents = (CYAN, AMBER, RED, BLUE, VIOLET, TEAL)
    for i, color in enumerate(accents):
        dx = 340 + i * 22
        d.ellipse([dx - 5, 916, dx + 5, 926], fill=color)
    put(
        d,
        (38, 948),
        "SOURCES: REUTERS · AP · AFP · ARAB NEWS · 22 NOV 2026",
        F_SMALL,
        MUTED,
        maxw=940,
    )

    out = Path(__file__).with_name("entry.png")
    img.save(out, format="PNG", optimize=True, compress_level=9)


if __name__ == "__main__":
    main()
