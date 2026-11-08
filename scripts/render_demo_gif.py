#!/usr/bin/env python3
"""Render docs/assets/demo-live.gif — browser-style live product preview."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1100, 640
BG = (226, 232, 240)
CHROME = (248, 250, 252)
PANEL = (255, 255, 255)
INK = (15, 23, 42)
MUTED = (100, 116, 139)
TEAL = (13, 148, 136)
TEAL_SOFT = (204, 251, 241)
AMBER = (217, 119, 6)
GREEN = (22, 163, 74)
BORDER = (203, 213, 225)
BLUE = (37, 99, 235)

QUERY = "What ingest-time defenses stop corpus poisoning in CI?"
ANSWER = (
    "SentinelRAG blocks poison at ingest (lexical + metadata defenses) "
    "and fails CI when poison probes or eval gates regress."
)
CITES = [
    ("pc-01-triple-gate", "Fails CI on recall, faithfulness, poison probes"),
    ("pc-12-poison-meta", "Metadata trust inflation blocked at ingest"),
    ("pc-13-lexical-defense", "Blocks sleeper trigger phrases"),
]


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = (
        ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf")
        if bold
        else ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/calibri.ttf")
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _chrome(draw: ImageDraw.ImageDraw, url: str) -> None:
    draw.rounded_rectangle((24, 24, W - 24, H - 24), radius=18, fill=PANEL, outline=BORDER, width=2)
    draw.rounded_rectangle((24, 24, W - 24, 78), radius=18, fill=CHROME, outline=BORDER, width=1)
    draw.rectangle((24, 60, W - 24, 78), fill=CHROME)
    for i, c in enumerate(((239, 68, 68), (245, 158, 11), (34, 197, 94))):
        x = 48 + i * 22
        draw.ellipse((x, 40, x + 12, 52), fill=c)
    draw.rounded_rectangle((140, 36, W - 48, 66), radius=10, fill=(255, 255, 255), outline=BORDER)
    draw.text((156, 42), url, fill=MUTED, font=_font(15))


def _sidebar(draw: ImageDraw.ImageDraw, *, health_on: bool, gate_on: bool, models_on: bool) -> None:
    x0, y0, x1, y1 = 48, 100, 300, H - 48
    draw.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=(248, 250, 252), outline=BORDER)
    draw.text((x0 + 18, y0 + 16), "SentinelRAG", fill=INK, font=_font(18, bold=True))
    draw.text((x0 + 18, y0 + 44), "Live preview", fill=TEAL, font=_font(13))

    def pill(y: int, label: str, on: bool) -> None:
        fill = TEAL_SOFT if on else (241, 245, 249)
        ink = TEAL if on else MUTED
        draw.rounded_rectangle((x0 + 16, y, x1 - 16, y + 36), radius=10, fill=fill, outline=BORDER)
        dot = GREEN if on else (148, 163, 184)
        draw.ellipse((x0 + 28, y + 12, x0 + 40, y + 24), fill=dot)
        draw.text((x0 + 50, y + 9), label, fill=ink, font=_font(14))

    pill(y0 + 80, "API /health", health_on)
    pill(y0 + 128, "Gate evidence", gate_on)
    pill(y0 + 176, "Gemini + bge + CE", models_on)
    draw.text((x0 + 18, y1 - 70), "strategy: agentic", fill=MUTED, font=_font(13))
    draw.text((x0 + 18, y1 - 48), "provider: gemini", fill=MUTED, font=_font(13))


def _main_panel(
    draw: ImageDraw.ImageDraw,
    *,
    typed: str,
    show_answer: bool,
    cite_n: int,
    latency: str | None,
) -> None:
    x0, y0, x1, y1 = 320, 100, W - 48, H - 48
    draw.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=PANEL, outline=BORDER)
    draw.text((x0 + 20, y0 + 16), "Ask the indexed corpus", fill=INK, font=_font(18, bold=True))
    draw.text((x0 + 20, y0 + 44), "POST /query?strategy=auto", fill=MUTED, font=_font(13))

    # Query box
    draw.rounded_rectangle((x0 + 20, y0 + 78, x1 - 20, y0 + 128), radius=10, fill=(248, 250, 252), outline=TEAL)
    qfont = _font(15)
    draw.text((x0 + 34, y0 + 94), typed + ("|" if len(typed) < len(QUERY) else ""), fill=INK, font=qfont)
    draw.rounded_rectangle((x1 - 120, y0 + 86, x1 - 32, y0 + 120), radius=8, fill=TEAL)
    draw.text((x1 - 98, y0 + 94), "Ask", fill=(255, 255, 255), font=_font(15, bold=True))

    if not show_answer:
        draw.text((x0 + 20, y0 + 160), "Waiting for grounded answer…", fill=MUTED, font=_font(14))
        return

    draw.text((x0 + 20, y0 + 152), "Answer", fill=AMBER, font=_font(13, bold=True))
    y = y0 + 174
    for line in _wrap(draw, ANSWER, _font(15), x1 - x0 - 50):
        draw.text((x0 + 20, y), line, fill=INK, font=_font(15))
        y += 22

    if latency:
        draw.text((x0 + 20, y + 8), f"Done in {latency}  ·  citations={cite_n}", fill=GREEN, font=_font(14, bold=True))
        y += 36

    draw.text((x0 + 20, y), "Citations", fill=MUTED, font=_font(13, bold=True))
    y += 24
    for i, (cid, snip) in enumerate(CITES[:cite_n]):
        draw.rounded_rectangle((x0 + 20, y, x1 - 20, y + 48), radius=8, fill=(248, 250, 252), outline=BORDER)
        draw.text((x0 + 34, y + 8), cid, fill=BLUE, font=_font(13, bold=True))
        draw.text((x0 + 34, y + 26), snip, fill=MUTED, font=_font(12))
        y += 56


def frame(
    *,
    url: str,
    typed: str,
    health_on: bool,
    gate_on: bool,
    models_on: bool,
    show_answer: bool,
    cite_n: int,
    latency: str | None,
) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _chrome(draw, url)
    _sidebar(draw, health_on=health_on, gate_on=gate_on, models_on=models_on)
    _main_panel(draw, typed=typed, show_answer=show_answer, cite_n=cite_n, latency=latency)
    return img


def main() -> int:
    out = Path(__file__).resolve().parents[1] / "docs" / "assets" / "demo-live.gif"
    out.parent.mkdir(parents=True, exist_ok=True)
    frames: list[Image.Image] = []
    durations: list[int] = []

    # Boot / health
    for step in range(3):
        frames.append(
            frame(
                url="http://127.0.0.1:8000/health",
                typed="",
                health_on=step >= 0,
                gate_on=step >= 1,
                models_on=step >= 2,
                show_answer=False,
                cite_n=0,
                latency=None,
            )
        )
        durations.append(500)

    # Navigate to query UI
    frames.append(
        frame(
            url="http://127.0.0.1:8000/docs#/query",
            typed="",
            health_on=True,
            gate_on=True,
            models_on=True,
            show_answer=False,
            cite_n=0,
            latency=None,
        )
    )
    durations.append(600)

    # Type query
    for i in range(1, len(QUERY) + 1, 3):
        frames.append(
            frame(
                url="http://127.0.0.1:8000/query?strategy=auto",
                typed=QUERY[:i],
                health_on=True,
                gate_on=True,
                models_on=True,
                show_answer=False,
                cite_n=0,
                latency=None,
            )
        )
        durations.append(70)
    frames.append(
        frame(
            url="http://127.0.0.1:8000/query?strategy=auto",
            typed=QUERY,
            health_on=True,
            gate_on=True,
            models_on=True,
            show_answer=False,
            cite_n=0,
            latency=None,
        )
    )
    durations.append(400)

    # Thinking
    frames.append(
        frame(
            url="http://127.0.0.1:8000/query?strategy=auto",
            typed=QUERY,
            health_on=True,
            gate_on=True,
            models_on=True,
            show_answer=False,
            cite_n=0,
            latency=None,
        )
    )
    durations.append(700)

    # Answer + citations appear
    for n in range(1, len(CITES) + 1):
        frames.append(
            frame(
                url="http://127.0.0.1:8000/query?strategy=auto",
                typed=QUERY,
                health_on=True,
                gate_on=True,
                models_on=True,
                show_answer=True,
                cite_n=n,
                latency="5.7s" if n == len(CITES) else None,
            )
        )
        durations.append(550)

    # Hold final
    for _ in range(8):
        frames.append(frames[-1])
        durations.append(350)

    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {out} ({out.stat().st_size} bytes, {len(frames)} frames)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
