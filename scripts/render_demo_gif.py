#!/usr/bin/env python3
"""Render docs/assets/demo-live.gif — terminal recording of the live demo story."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 960, 540
BG = (15, 23, 42)
PANEL = (2, 6, 23)
FG = (226, 232, 240)
TEAL = (45, 212, 191)
GREEN = (134, 239, 172)
BLUE = (147, 197, 253)
AMBER = (251, 191, 36)
MUTED = (148, 163, 184)
RED = (239, 68, 68)
YEL = (245, 158, 11)
OK = (34, 197, 94)

LINES: list[tuple[str, tuple[int, int, int]]] = [
    ("$ uv run sentinelrag-gate run --refresh", TEAL),
    ("Gate passed · evidence.json · junit.xml · sarif.json", FG),
    ("✓ hybrid recall@5=1.0 · faithfulness=0.83 · poison probes blocked", GREEN),
    ("$ uv run python scripts/demo_60s.py", TEAL),
    ("=== SentinelRAG 60s demo ===", FG),
    ("1) health: ok · llm=gemini/gemini-2.5-flash", FG),
    ("   embed=bge-small · rerank=ms-marco-MiniLM-L-6-v2", MUTED),
    ("2) index ready — skip ingest", FG),
    ("3) query strategy=auto …", FG),
    ("   answer: Ingest poison probes + eval gates fail CI on regressions.", BLUE),
    ("   strategy=agentic · provider=gemini · citations=5", FG),
    ("     - pc-01-triple-gate · pc-12-poison-meta · pc-13-lexical", MUTED),
    ("Done in 5.7s", AMBER),
]


def _font(size: int) -> ImageFont.ImageFont:
    for name in (
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/CascadiaMono.ttf",
        "DejaVuSansMono.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def frame(n_lines: int) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((12, 12, W - 12, H - 12), radius=14, fill=PANEL, outline=(51, 65, 85))
    draw.ellipse((32, 26, 46, 40), fill=RED)
    draw.ellipse((56, 26, 70, 40), fill=YEL)
    draw.ellipse((80, 26, 94, 40), fill=OK)
    title = _font(14)
    draw.text((W // 2, 28), "sentinelrag — live demo recording", fill=MUTED, font=title, anchor="mt")
    mono = _font(16)
    y = 78
    for i, (text, color) in enumerate(LINES[:n_lines]):
        draw.text((40, y), text, fill=color, font=mono)
        y += 30
    if n_lines < len(LINES):
        draw.text((40, y), "█", fill=TEAL, font=mono)
    return img


def main() -> int:
    out = Path(__file__).resolve().parents[1] / "docs" / "assets" / "demo-live.gif"
    out.parent.mkdir(parents=True, exist_ok=True)
    frames = [frame(i) for i in range(1, len(LINES) + 1)]
    # Hold final frame longer
    frames.extend([frames[-1]] * 6)
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=[450] * (len(LINES) - 1) + [450] + [700] * 6,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
