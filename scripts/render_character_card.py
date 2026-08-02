#!/usr/bin/env python3
"""Render a distortion-free Regalia character card at 720x1200."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


CANVAS_SIZE = (720, 1200)
ART_BOX = (18, 18, 702, 1044)  # 684x1026, an exact 2:3 art window
NAME_BOX = (38, 1052, 682, 1148)  # fixed 96px name frame
FONT_PATH = Path("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc")
FONT_INDEX = 2  # Hiragino Mincho ProN W6
TEXT_COLOR = (244, 228, 190)
TEXT_STROKE = (53, 31, 24)
MAX_TEXT_WIDTH = 600
MAX_FONT_SIZE = 36
MIN_FONT_SIZE = 21

GOLD = (194, 151, 76)
GOLD_LIGHT = (232, 201, 133)
GOLD_DARK = (92, 60, 31)
RED = (91, 24, 22)
INK = (7, 8, 15)


def fit_font(text: str) -> ImageFont.FreeTypeFont:
    for size in range(MAX_FONT_SIZE, MIN_FONT_SIZE - 1, -1):
        font = ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX)
        if font.getlength(text) <= MAX_TEXT_WIDTH:
            return font
    return ImageFont.truetype(FONT_PATH, MIN_FONT_SIZE, index=FONT_INDEX)


def draw_corner(draw: ImageDraw.ImageDraw, x: int, y: int, sx: int, sy: int) -> None:
    """Draw a compact, deterministic corner ornament."""
    draw.line((x, y + 38 * sy, x, y, x + 38 * sx, y), fill=GOLD_LIGHT, width=2)
    draw.line((x + 7 * sx, y + 30 * sy, x + 7 * sx, y + 7 * sy, x + 30 * sx, y + 7 * sy), fill=GOLD_DARK, width=2)
    draw.polygon(
        ((x + 10 * sx, y), (x + 17 * sx, y + 7 * sy), (x + 10 * sx, y + 14 * sy), (x + 3 * sx, y + 7 * sy)),
        outline=GOLD,
    )
    draw.line((x, y + 23 * sy, x + 23 * sx, y), fill=GOLD, width=1)


def draw_frame(draw: ImageDraw.ImageDraw) -> None:
    """Draw the shared narrow Machina card frame and compact name plaque."""
    draw.rectangle((7, 7, 712, 1192), outline=GOLD_DARK, width=2)
    draw.rectangle((12, 12, 707, 1187), outline=GOLD, width=1)
    draw.rectangle(ART_BOX, outline=GOLD_LIGHT, width=2)

    draw_corner(draw, 13, 13, 1, 1)
    draw_corner(draw, 706, 13, -1, 1)
    draw_corner(draw, 13, 1186, 1, -1)
    draw_corner(draw, 706, 1186, -1, -1)

    # Small top crest and the art/name separator.
    draw.polygon(((360, 8), (370, 18), (360, 28), (350, 18)), fill=INK, outline=GOLD_LIGHT)
    draw.line((302, 1048, 348, 1048), fill=GOLD_DARK, width=1)
    draw.polygon(((360, 1040), (368, 1048), (360, 1056), (352, 1048)), fill=INK, outline=GOLD_LIGHT)
    draw.line((372, 1048, 418, 1048), fill=GOLD_DARK, width=1)

    # Compact fixed-height name frame: exactly 96px tall.
    x0, y0, x1, y1 = NAME_BOX
    draw.rounded_rectangle(NAME_BOX, radius=8, fill=(6, 7, 16), outline=GOLD_DARK, width=4)
    draw.rounded_rectangle((x0 + 5, y0 + 5, x1 - 5, y1 - 5), radius=5, outline=GOLD, width=1)
    draw.line((x0 + 18, y0 + 11, x1 - 18, y0 + 11), fill=RED, width=1)
    draw.line((x0 + 18, y1 - 11, x1 - 18, y1 - 11), fill=RED, width=1)

    # Restrained bottom ornament, kept outside the name box.
    draw.line((288, 1170, 342, 1170), fill=GOLD_DARK, width=1)
    draw.polygon(((360, 1158), (372, 1170), (360, 1182), (348, 1170)), fill=INK, outline=GOLD)
    draw.line((378, 1170, 432, 1170), fill=GOLD_DARK, width=1)


def render(source: Path, output: Path, name: str) -> None:
    with Image.open(source) as opened:
        art = ImageOps.fit(
            opened.convert("RGB"),
            (ART_BOX[2] - ART_BOX[0], ART_BOX[3] - ART_BOX[1]),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

    card = Image.new("RGB", CANVAS_SIZE, INK)
    card.paste(art, (ART_BOX[0], ART_BOX[1]))

    draw = ImageDraw.Draw(card)
    draw_frame(draw)
    font = fit_font(name)
    text_box = draw.textbbox((0, 0), name, font=font, stroke_width=1)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    text_x = (CANVAS_SIZE[0] - text_width) / 2
    text_y = NAME_BOX[1] + (NAME_BOX[3] - NAME_BOX[1] - text_height) / 2 - text_box[1]
    draw.text(
        (text_x, text_y),
        name,
        font=font,
        fill=TEXT_COLOR,
        stroke_width=1,
        stroke_fill=TEXT_STROKE,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    card.save(output, "WEBP", quality=88, method=6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    render(args.input, args.output, args.name)


if __name__ == "__main__":
    main()
