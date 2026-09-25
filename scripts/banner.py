#!/usr/bin/env python3
"""
banner.py - generate animated GitHub profile banners (dark & light)
featuring authentic 1-bit Floyd-Steinberg dithered portrait of Sahil Belchada
in the VISUAL.MAP cybernetic terminal panel.
"""

from __future__ import annotations

import html
import math
from pathlib import Path
from collections import deque

import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "source" / "sahil.jpg"

# Fallback path if source is in Downloads
DOWNLOADS_SOURCE = Path(r"C:\Users\Sahil Belchada\Downloads\sahil.jpg")

W, H = 1180, 590

THEMES = {
    "dark": {
        "bg": "#0A101F",
        "panel": "#0D1628",
        "panel2": "#101B30",
        "line": "#25344C",
        "muted": "#8291A8",
        "text": "#DDE7F5",
        "portrait": "#AA9BEF",
        "chrome": "#22D3EE",
        "accent": "#10B981",
        "shadow": "#02050B",
        "glow": "rgba(34, 211, 238, 0.25)",
        "radar_ring": "#1F2F4A",
    },
    "light": {
        "bg": "#F6F8FA",
        "panel": "#FFFFFF",
        "panel2": "#EDF3F7",
        "line": "#CBD7E1",
        "muted": "#64748B",
        "text": "#172033",
        "portrait": "#4A3D7A",
        "chrome": "#0891B2",
        "accent": "#10B981",
        "shadow": "#AAB7C4",
        "glow": "rgba(8, 145, 178, 0.25)",
        "radar_ring": "#D6DFE8",
    },
}

ROWS = [
    ("Subject", "Sahil Belchada"),
    ("Role", "Software Engineer · Systems & AI"),
    ("Origin", "Mumbai, India"),
    ("Education", "B.Tech Computer Engineering (2027)"),
    ("Status", "Building High-Throughput & Agentic Systems"),
    ("Portfolio", "sahilbelchada.dev"),
    ("Core.Languages", "Python · Java · TypeScript · C++ · SQL"),
    ("Core.Backend", "FastAPI · Spring Boot · Node.js"),
    ("Core.Streaming", "Apache Kafka · Redis Streams · WebSockets"),
    ("Core.AI / Agents", "PyTorch · LangChain · RAG · pgvector"),
    ("Core.Databases", "PostgreSQL · MongoDB · Redis · Pinecone"),
    ("Core.Cloud & Ops", "AWS (EC2, S3) · Docker · CI/CD"),
    ("Grid.LinkedIn", "in/sahil-belchada"),
    ("Grid.GitHub", "bsahil979"),
]

def text_width(s: str, size: float = 14.0) -> float:
    return len(s) * size * 0.605

def dotted_leader(x1: float, x2: float, y: float, step: float = 6.0) -> str:
    parts = []
    x = x1
    while x <= x2:
        parts.append(f"M{x:.1f} {y:.1f}h1")
        x += step
    return "".join(parts)

def floyd_steinberg(gray_arr: np.ndarray) -> np.ndarray:
    """Serpentine 1-bit Floyd-Steinberg error diffusion."""
    work = gray_arr.copy().astype(np.float32) / 255.0
    out = np.zeros_like(work, dtype=bool)
    height, width = work.shape
    for y in range(height):
        left_to_right = (y % 2 == 0)
        xs = range(width) if left_to_right else range(width - 1, -1, -1)
        direction = 1 if left_to_right else -1
        for x in xs:
            old = work[y, x]
            new = 1.0 if old >= 0.5 else 0.0
            out[y, x] = bool(new)
            err = old - new
            nx = x + direction
            if 0 <= nx < width:
                work[y, nx] += err * 7 / 16
            if y + 1 < height:
                if 0 <= x - direction < width:
                    work[y + 1, x - direction] += err * 3 / 16
                work[y + 1, x] += err * 5 / 16
                if 0 <= nx < width:
                    work[y + 1, nx] += err * 1 / 16
    return out

def extract_portrait_points() -> dict[str, np.ndarray]:
    """Process sahil.jpg into Floyd-Steinberg dither points for dark and light themes."""
    src = SOURCE if SOURCE.exists() else DOWNLOADS_SOURCE
    if not src.exists():
        raise FileNotFoundError(f"Source image not found at {SOURCE} or {DOWNLOADS_SOURCE}")

    im = Image.open(src).convert("RGB")
    w, h = im.size

    # Precise crop centered on face: 700x793 -> 300x340
    crop_w = 700
    crop_h = int(crop_w * 340 / 300)
    left = (w - crop_w) // 2
    top = 70
    right = left + crop_w
    bottom = top + crop_h

    crop = im.crop((left, top, right, bottom)).resize((300, 340), Image.Resampling.LANCZOS)
    rgb = np.asarray(crop, dtype=np.float32)
    gray = np.mean(rgb, axis=2)

    # Segment subject from studio background via flood fill from corners
    h_c, w_c = gray.shape
    visited = np.zeros((h_c, w_c), dtype=bool)
    is_bg = np.zeros((h_c, w_c), dtype=bool)
    q = deque([(0, 0), (0, w_c - 1), (10, 0), (10, w_c - 1)])
    for y, x in q:
        visited[y, x] = True

    while q:
        cy, cx = q.popleft()
        if gray[cy, cx] > 205 and (rgb[cy, cx, 0] - rgb[cy, cx, 2]) < 22:
            is_bg[cy, cx] = True
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h_c and 0 <= nx < w_c and not visited[ny, nx]:
                    visited[ny, nx] = True
                    q.append((ny, nx))

    subject_mask = ~is_bg

    # Contrast enhancement & equalization on the subject
    gray_im = ImageOps.grayscale(crop)
    mask_pil = Image.fromarray((subject_mask * 255).astype(np.uint8))
    eq_im = ImageOps.equalize(gray_im, mask=mask_pil)
    eq_im = ImageEnhance.Contrast(eq_im).enhance(1.4)
    eq_im = eq_im.filter(ImageFilter.UnsharpMask(radius=2, percent=180, threshold=1))
    enhanced_arr = np.asarray(eq_im, dtype=np.float32)

    # Dark mode: lit pixels against dark background
    dark_gray = enhanced_arr * subject_mask
    bits_dark = floyd_steinberg(dark_gray) & subject_mask

    # Light mode: shaded pixels against white background
    light_gray = (255 - enhanced_arr) * subject_mask
    bits_light = floyd_steinberg(light_gray) & subject_mask

    # Map to SVG coordinates inside VISUAL.MAP (x: 94..394, y: 146..486)
    # Center = 244, width = 300, offset_x = 94. Top = 146, height = 340.
    ys_d, xs_d = np.where(bits_dark)
    pts_dark = np.column_stack((94 + xs_d, 146 + ys_d))

    ys_l, xs_l = np.where(bits_light)
    pts_light = np.column_stack((94 + xs_l, 146 + ys_l))

    return {"dark": pts_dark, "light": pts_light}

def point_path(points: np.ndarray) -> str:
    """Aggregate adjacent horizontal one-pixel dots into compact SVG path runs."""
    if not len(points):
        return ""
    integer = np.rint(points).astype(int)
    unique = sorted({(int(x), int(y)) for x, y in integer}, key=lambda p: (p[1], p[0]))
    chunks: list[str] = []
    i = 0
    while i < len(unique):
        x0, y = unique[i]
        x1 = x0
        i += 1
        while i < len(unique) and unique[i][1] == y and unique[i][0] <= x1 + 1:
            x1 = unique[i][0]
            i += 1
        chunks.append(f"M{x0} {y}h{x1 - x0 + 1}")
    return "".join(chunks)

def render_banner(theme_name: str, portrait_pts: np.ndarray) -> str:
    t = THEMES[theme_name]
    num_pts = len(portrait_pts)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Sahil Belchada live profile banner">',
        '<defs>',
        f'<filter id="drop-shadow" x="-5%" y="-5%" width="110%" height="110%"><feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="{t["shadow"]}" flood-opacity="0.45"/></filter>',
        '<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<clipPath id="leftClip"><rect x="34" y="88" width="420" height="470" rx="6"/></clipPath>',
        '</defs>',

        # Outer terminal window
        f'<rect x="16" y="16" width="1148" height="558" rx="10" fill="{t["panel"]}" stroke="{t["line"]}" filter="url(#drop-shadow)"/>',

        # Traffic light buttons
        '<circle cx="42" cy="46" r="6" fill="#FF5F56"/>',
        '<circle cx="62" cy="46" r="6" fill="#FFBD2E"/>',
        '<circle cx="82" cy="46" r="6" fill="#27C93F"/>',

        # Window title bar
        f'<text x="590" y="51" text-anchor="middle" fill="{t["muted"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" font-weight="600">sahil@systems:~$ profile.sh --live</text>',
        f'<path d="M16 72H1164" stroke="{t["line"]}"/>',

        # =====================================================================
        # LEFT PANEL - VISUAL.MAP (CYBERNETIC PORTRAIT SCANNER)
        # =====================================================================
        f'<rect x="34" y="88" width="420" height="470" rx="6" fill="{t["panel2"]}" stroke="{t["line"]}"/>',
        f'<path d="M34 124H454" stroke="{t["line"]}"/>',
        f'<text x="50" y="111" fill="{t["chrome"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" font-weight="700" letter-spacing="1.2">VISUAL.MAP</text>',
        f'<text x="438" y="111" text-anchor="end" fill="{t["muted"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">300×340 / 1-BIT</text>',

        # Corner brackets on left panel
        f'<path d="M49 141h12M49 141v12M439 141h-12M439 141v12M49 539h12M49 539v-12M439 539h-12M439 539v-12" fill="none" stroke="{t["chrome"]}" opacity=".55"/>',

        # Cybernetic background grids & radar circles
        '<g clip-path="url(#leftClip)">',
        f'<line x1="244" y1="130" x2="244" y2="495" stroke="{t["line"]}" stroke-dasharray="2 6" opacity="0.45"/>',
        f'<line x1="60" y1="316" x2="428" y2="316" stroke="{t["line"]}" stroke-dasharray="2 6" opacity="0.45"/>',
        f'<circle cx="244" cy="316" r="80" fill="none" stroke="{t["radar_ring"]}" stroke-width="1" opacity="0.35"/>',
        f'<circle cx="244" cy="316" r="145" fill="none" stroke="{t["radar_ring"]}" stroke-width="1" stroke-dasharray="4 4" opacity="0.35"/>',

        # Animated expanding radar pulse rings
        f'<circle cx="244" cy="316" r="30" fill="none" stroke="{t["chrome"]}" stroke-width="1.2" opacity="0.7">',
        '<animate attributeName="r" values="30;175" dur="3.6s" repeatCount="indefinite" ease="linear"/>',
        '<animate attributeName="opacity" values="0.7;0" dur="3.6s" repeatCount="indefinite" ease="linear"/>',
        '</circle>',
        f'<circle cx="244" cy="316" r="30" fill="none" stroke="{t["portrait"]}" stroke-width="1.2" opacity="0.7">',
        '<animate attributeName="r" values="30;175" begin="1.8s" dur="3.6s" repeatCount="indefinite" ease="linear"/>',
        '<animate attributeName="opacity" values="0.7;0" begin="1.8s" dur="3.6s" repeatCount="indefinite" ease="linear"/>',
        '</circle>',
    ]

    # Target detection HUD reticle around face area
    parts.extend([
        f'<path d="M152 172h14M152 172v14M336 172h-14M336 172v14M152 386h14M152 386v-14M336 386h-14M336 386v-14" fill="none" stroke="{t["chrome"]}" stroke-width="1.2" opacity=".65"/>',
        f'<text x="156" y="165" fill="{t["chrome"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="9" font-weight="700" letter-spacing="1">ID: SAHIL_BELCHADA</text>',
        f'<text x="332" y="165" text-anchor="end" fill="{t["accent"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="9" font-weight="700">99.8%</text>',
    ])

    # Authentic 1-bit Floyd-Steinberg portrait path
    d_path = point_path(portrait_pts)
    parts.append(
        f'<path d="{d_path}" fill="none" stroke="{t["portrait"]}" stroke-width="1" opacity="0.94" shape-rendering="crispEdges">'
        '<animate attributeName="opacity" values="0.94;1;0.94" dur="4s" repeatCount="indefinite" ease="easeInOut"/>'
        '</path>'
    )

    # Animated glowing laser scanline sweeping across the portrait
    parts.extend([
        f'<line x1="84" y1="146" x2="404" y2="146" stroke="{t["chrome"]}" stroke-width="1.5" opacity="0.75" filter="url(#glow)">',
        '<animate attributeName="y1" values="146;486;146" dur="4.2s" repeatCount="indefinite" ease="easeInOut"/>',
        '<animate attributeName="y2" values="146;486;146" dur="4.2s" repeatCount="indefinite" ease="easeInOut"/>',
        '<animate attributeName="opacity" values="0.45;0.9;0.45" dur="4.2s" repeatCount="indefinite"/>',
        '</line>',
    ])

    # Real-time telemetry waveform at bottom of visual map
    wave_d = ["M 55 506"]
    for wx in range(55, 435, 10):
        wy = 506 + math.sin((wx - 55) * 0.08) * 6
        wave_d.append(f"L {wx} {wy:.1f}")
    parts.append(f'<path d="{" ".join(wave_d)}" fill="none" stroke="{t["portrait"]}" stroke-width="1.2" opacity="0.55"/>')

    # Telemetry text at bottom
    parts.append(
        f'<text x="58" y="538" fill="{t["muted"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="10">'
        f'PTS {num_pts:05d} · FS/SERPENTINE · SYS_NOMINAL</text>'
    )
    parts.append('</g>')

    # =====================================================================
    # RIGHT PANEL - SYSTEM.INFO
    # =====================================================================
    parts.extend([
        f'<rect x="474" y="88" width="672" height="470" rx="6" fill="{t["panel2"]}" stroke="{t["line"]}"/>',
        f'<path d="M474 124H1146" stroke="{t["line"]}"/>',
        f'<text x="490" y="111" fill="{t["chrome"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" font-weight="700" letter-spacing="1.2">SYSTEM.INFO</text>',

        # LIVE indicator
        '<g filter="url(#glow)"><circle cx="915" cy="106" r="4" fill="#FF4D5A">'
        '<animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/>'
        '</circle></g>',
        '<text x="927" y="111" fill="#FF4D5A" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="12" font-weight="700">LIVE</text>',

        # Handle pill
        f'<rect x="982" y="94" width="146" height="24" rx="12" fill="{t["chrome"]}" opacity=".16" stroke="{t["chrome"]}"/>',
        f'<text x="1055" y="111" text-anchor="middle" fill="{t["chrome"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="14" font-weight="700">@bsahil979</text>',
    ])

    # Dotted telemetry rows
    value_right = 1127.0
    row_y = 153.0
    for label, value in ROWS:
        value_len = text_width(value, 13.5)
        label_len = text_width(label, 13.5)
        leader_start = 491 + label_len + 12
        leader_end = value_right - value_len - 12

        parts.extend([
            f'<text x="491" y="{row_y:.1f}" fill="{t["muted"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13.5">{html.escape(label)}</text>',
            f'<path d="{dotted_leader(leader_start, leader_end, row_y - 4)}" fill="none" stroke="{t["line"]}" stroke-width="1" shape-rendering="crispEdges"/>',
            f'<text x="{value_right:.1f}" y="{row_y:.1f}" text-anchor="end" fill="{t["text"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13.5" font-weight="600">{html.escape(value)}</text>',
        ])
        row_y += 24.5

    # Bottom footer line
    parts.extend([
        f'<path d="M490 514H1130" stroke="{t["line"]}"/>',
        f'<text x="491" y="535" fill="{t["accent"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11" font-weight="700">● ALL SYSTEMS NOMINAL</text>',
        f'<text x="1128" y="535" text-anchor="end" fill="{t["muted"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">UTC+5:30 · MUMBAI NODE</text>',
        '</svg>',
    ])

    return "".join(parts)

def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Processing authentic portrait points from sahil.jpg...")
    pts = extract_portrait_points()

    for theme in ("dark", "light"):
        svg = render_banner(theme, pts[theme])
        out_file = ASSETS / f"banner-{theme}.svg"
        out_file.write_text(svg, encoding="utf-8")
        print(f"Generated {out_file.name} ({len(svg.encode('utf-8')):,} bytes, {len(pts[theme]):,} portrait dots)")

if __name__ == "__main__":
    main()
