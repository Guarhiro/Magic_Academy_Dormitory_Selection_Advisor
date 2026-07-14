#!/usr/bin/env python3
"""Render a Regalia diagnosis card label and export a 720x1200 WebP."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CANVAS_SIZE = (720, 1200)
FONT_PATH = Path("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc")
FONT_INDEX = 2  # Hiragino Mincho ProN W6
TEXT_COLOR = (244, 228, 190)
TEXT_STROKE = (53, 31, 24)
MAX_TEXT_WIDTH = 620
MAX_FONT_SIZE = 48
MIN_FONT_SIZE = 30
TEXT_TOP = 1043


def fit_font(text: str) -> ImageFont.FreeTypeFont:
    for size in range(MAX_FONT_SIZE, MIN_FONT_SIZE - 1, -1):
        font = ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX)
        if font.getlength(text) <= MAX_TEXT_WIDTH:
            return font
    return ImageFont.truetype(FONT_PATH, MIN_FONT_SIZE, index=FONT_INDEX)


def render(source: Path, output: Path, name: str) -> None:
    with Image.open(source) as opened:
        card = opened.convert("RGB").resize(CANVAS_SIZE, Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(card)
    font = fit_font(name)
    text_width = font.getlength(name)
    text_x = (CANVAS_SIZE[0] - text_width) / 2
    draw.text(
        (text_x, TEXT_TOP),
        name,
        font=font,
        fill=TEXT_COLOR,
        stroke_width=1,
        stroke_fill=TEXT_STROKE,
    )

    # Small downward marker used by the reference Shion card.
    draw.polygon(((347, 1121), (373, 1121), (360, 1130)), fill=(177, 119, 48))

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
