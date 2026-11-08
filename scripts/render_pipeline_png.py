#!/usr/bin/env python3
"""Render docs/assets/pipeline.png — GitHub-safe diagram (no SVG)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1100, 280
STEPS = [
    ("1. Corpus", "docs + golden Qs", (255, 255, 255), (203, 213, 225)),
    ("2. Defend", "hygiene · poison", (240, 253, 250), (20, 184, 166)),
    ("3. Measure", "recall · faith.", (240, 249, 255), (56, 189, 248)),
    ("4. Gate", "policy floors", (255, 251, 235), (245, 158, 11)),
    ("5. CI proof", "JSON·JUnit·SARIF", (236, 253, 245), (34, 197, 94)),
]


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for name in (
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> int:
    img = Image.new("RGB", (W, H), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.text((28, 22), "How a SentinelRAG gate run works", fill=(15, 23, 42), font=_font(20, True))
    draw.text(
        (28, 52),
        "Corpus is defended and measured → policy gate → CI artifacts (or a failed PR).",
        fill=(100, 116, 139),
        font=_font(14),
    )

    box_w, box_h, gap = 170, 78, 28
    x0 = 28
    y = 100
    for i, (title, sub, fill, stroke) in enumerate(STEPS):
        x = x0 + i * (box_w + gap)
        draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=14, fill=fill, outline=stroke, width=2)
        draw.text((x + box_w / 2, y + 24), title, fill=(15, 23, 42), font=_font(16, True), anchor="mt")
        draw.text((x + box_w / 2, y + 50), sub, fill=(100, 116, 139), font=_font(13), anchor="mt")
        if i < len(STEPS) - 1:
            ax = x + box_w + 4
            draw.line((ax, y + box_h / 2, ax + gap - 8, y + box_h / 2), fill=(100, 116, 139), width=3)
            draw.polygon(
                [
                    (ax + gap - 8, y + box_h / 2),
                    (ax + gap - 18, y + box_h / 2 - 6),
                    (ax + gap - 18, y + box_h / 2 + 6),
                ],
                fill=(100, 116, 139),
            )

    draw.text(
        (28, H - 36),
        "Optional inputs to step 4: promptfoo / Ragas / DeepEval score imports.",
        fill=(100, 116, 139),
        font=_font(13),
    )

    out = Path(__file__).resolve().parents[1] / "docs" / "assets" / "pipeline.png"
    img.save(out, "PNG", optimize=True)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
