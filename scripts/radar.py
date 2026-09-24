#!/usr/bin/env python3
"""
radar.py - render spider / radar chart as a standalone SVG. Stdlib only.

Usage:
    python scripts/radar.py --data assets/skills.json -o assets/radar
    python scripts/radar.py --data assets/langmix.json -o assets/radar-langs
"""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path

THEMES = {
    "dark": {
        "title": "#aa9bef",
        "grid": "#25344c",
        "spoke": "#1c283c",
        "label": "#c9d1d9",
        "value": "#8b949e",
        "fill": "rgba(170, 155, 239, 0.35)",
        "stroke": "#aa9bef",
        "vertex": "#c4b8ff",
        "bg": "none",
        "border": "#21262d",
        "card_bg": "#0d1117",
    },
    "light": {
        "title": "#4a3d7a",
        "grid": "#cbd7e1",
        "spoke": "#e2e8f0",
        "label": "#1f2328",
        "value": "#57606a",
        "fill": "rgba(74, 61, 122, 0.25)",
        "stroke": "#4a3d7a",
        "vertex": "#4a3d7a",
        "bg": "none",
        "border": "#d0d7de",
        "card_bg": "#ffffff",
    },
}

W, H = 440, 340
CX, CY, R = 220.0, 185.0, 105.0

def render_radar(title: str, axes: list[dict], theme: str) -> str:
    c = THEMES[theme]
    n = len(axes)
    if n < 3:
        raise ValueError("Radar requires at least 3 axes")

    angles = [-math.pi / 2 + (2 * math.pi * i / n) for i in range(n)]

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape(title)}">',
        f'<rect width="{W}" height="{H}" rx="10" fill="{c["card_bg"]}" stroke="{c["border"]}"/>',
        f'<text x="{W / 2}" y="32" text-anchor="middle" font-family="ui-sans-serif,Segoe UI,system-ui,sans-serif" font-size="14.5" font-weight="700" letter-spacing="0.5" fill="{c["title"]}">{html.escape(title).upper()}</text>',
    ]

    # Grid polygons (5 levels: 20%, 40%, 60%, 80%, 100%)
    for level in (0.2, 0.4, 0.6, 0.8, 1.0):
        pts = []
        lr = R * level
        for a in angles:
            x = CX + lr * math.cos(a)
            y = CY + lr * math.sin(a)
            pts.append(f"{x:.1f},{y:.1f}")
        stroke_color = c["grid"] if level == 1.0 else c["spoke"]
        out.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="{stroke_color}" stroke-width="1"/>')

    # Spoke lines
    for a in angles:
        x = CX + R * math.cos(a)
        y = CY + R * math.sin(a)
        out.append(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="{c["spoke"]}" stroke-width="1"/>')

    # Data polygon
    data_pts = []
    vertex_elements = []
    for i, item in enumerate(axes):
        val = min(max(item["value"], 0), 100)
        dr = R * (val / 100.0)
        a = angles[i]
        x = CX + dr * math.cos(a)
        y = CY + dr * math.sin(a)
        data_pts.append(f"{x:.1f},{y:.1f}")
        vertex_elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{c["vertex"]}" stroke="{c["card_bg"]}" stroke-width="1.5"/>')

    out.append(f'<polygon points="{" ".join(data_pts)}" fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="2"/>')
    out.extend(vertex_elements)

    # Labels
    for i, item in enumerate(axes):
        a = angles[i]
        cos_a = math.cos(a)
        sin_a = math.sin(a)
        
        # Label offset
        dist = R + 18.0
        lx = CX + dist * cos_a
        ly = CY + dist * sin_a

        if cos_a > 0.25:
            anchor = "start"
            lx += 4
        elif cos_a < -0.25:
            anchor = "end"
            lx -= 4
        else:
            anchor = "middle"

        if sin_a < -0.85:
            ly -= 4
        elif sin_a > 0.85:
            ly += 10

        label_txt = html.escape(item["label"])
        val_txt = f"{item['value']}%"
        out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11" font-weight="600" fill="{c["label"]}">{label_txt} <tspan fill="{c["value"]}" font-size="9.5">({val_txt})</tspan></text>')

    out.append("</svg>")
    return "".join(out)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, required=True, help="Path to JSON file")
    p.add_argument("-o", "--out", type=Path, required=True, help="Output base path")
    args = p.parse_args()

    content = json.loads(args.data.read_text(encoding="utf-8"))
    title = content.get("title", "Radar")
    axes = content.get("axes", [])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "light"):
        svg = render_radar(title, axes, theme)
        dest = Path(f"{args.out}-{theme}.svg")
        dest.write_text(svg, encoding="utf-8")
        print(f"Generated {dest.name}")

if __name__ == "__main__":
    main()
