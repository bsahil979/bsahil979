#!/usr/bin/env python3
"""
banner.py - generate animated GitHub profile banners (dark & light).
Stdlib only. Zero external dependencies.
"""

from __future__ import annotations

import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

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

def render_banner(theme_name: str) -> str:
    t = THEMES[theme_name]
    
    # SVG definition and styling
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
        
        # LEFT PANEL - VISUAL.MAP
        f'<rect x="34" y="88" width="420" height="470" rx="6" fill="{t["panel2"]}" stroke="{t["line"]}"/>',
        f'<path d="M34 124H454" stroke="{t["line"]}"/>',
        f'<text x="50" y="111" fill="{t["chrome"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" font-weight="700" letter-spacing="1.2">VISUAL.MAP</text>',
        f'<text x="438" y="111" text-anchor="end" fill="{t["muted"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">64-NODE DISTRIBUTED MESH</text>',
        
        # Corner brackets on left panel
        f'<path d="M49 141h12M49 141v12M439 141h-12M439 141v12M49 539h12M49 539v-12M439 539h-12M439 539v-12" fill="none" stroke="{t["chrome"]}" opacity=".55"/>',
        
        # Cybernetic network cluster visualization
        '<g clip-path="url(#leftClip)">',
        
        # Background coordinate grid lines
        f'<line x1="244" y1="130" x2="244" y2="490" stroke="{t["line"]}" stroke-dasharray="2 6" opacity="0.6"/>',
        f'<line x1="60" y1="310" x2="428" y2="310" stroke="{t["line"]}" stroke-dasharray="2 6" opacity="0.6"/>',
        
        # Radar circles
        f'<circle cx="244" cy="310" r="60" fill="none" stroke="{t["radar_ring"]}" stroke-width="1"/>',
        f'<circle cx="244" cy="310" r="120" fill="none" stroke="{t["radar_ring"]}" stroke-width="1" stroke-dasharray="4 4"/>',
        f'<circle cx="244" cy="310" r="165" fill="none" stroke="{t["radar_ring"]}" stroke-width="1" opacity="0.4"/>',
        
        # Animated radar sweep pulse
        f'<circle cx="244" cy="310" r="20" fill="none" stroke="{t["chrome"]}" stroke-width="1.5" opacity="0.8">',
        '<animate attributeName="r" values="20;165" dur="3.5s" repeatCount="indefinite" ease="linear"/>',
        '<animate attributeName="opacity" values="0.8;0" dur="3.5s" repeatCount="indefinite" ease="linear"/>',
        '</circle>',
        f'<circle cx="244" cy="310" r="20" fill="none" stroke="{t["portrait"]}" stroke-width="1.5" opacity="0.8">',
        '<animate attributeName="r" values="20;165" begin="1.75s" dur="3.5s" repeatCount="indefinite" ease="linear"/>',
        '<animate attributeName="opacity" values="0.8;0" begin="1.75s" dur="3.5s" repeatCount="indefinite" ease="linear"/>',
        '</circle>',
    ]
    
    # Hexagonal satellite network nodes
    cx, cy, r_nodes = 244.0, 310.0, 115.0
    node_labels = ["API GATEWAY", "KAFKA INGEST", "STREAM WORKER", "VECTOR / RAG", "LLM AGENT", "CACHE / REDIS"]
    node_coords = []
    for i in range(6):
        angle = math.radians(i * 60)
        nx = cx + r_nodes * math.cos(angle)
        ny = cy + r_nodes * math.sin(angle)
        node_coords.append((nx, ny, node_labels[i]))
        
    # Draw interconnect lines between satellites and center
    for nx, ny, _ in node_coords:
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{t["line"]}" stroke-width="1.2"/>')
        
    # Draw outer ring connecting satellites
    for i in range(6):
        x1, y1, _ = node_coords[i]
        x2, y2, _ = node_coords[(i + 1) % 6]
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["chrome"]}" stroke-width="1" stroke-dasharray="3 3" opacity="0.65"/>')
        
    # Animated data packets traveling along lines
    for i, (nx, ny, _) in enumerate(node_coords):
        dur = 2.4 + (i * 0.3)
        begin = i * 0.4
        parts.append(
            f'<circle r="3" fill="{t["chrome"]}" filter="url(#glow)">'
            f'<animate attributeName="cx" values="{cx};{nx:.1f};{cx}" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{cy};{ny:.1f};{cy}" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.2;1;0.2" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            '</circle>'
        )

    # Satellite node glyphs
    for nx, ny, label in node_coords:
        parts.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="7" fill="{t["panel"]}" stroke="{t["chrome"]}" stroke-width="2"/>')
        parts.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="3" fill="{t["portrait"]}"/>')
        
        # Labels slightly offset
        lx = nx + (14 if nx >= cx else -14)
        anchor = "start" if nx >= cx else "end"
        parts.append(f'<text x="{lx:.1f}" y="{ny + 3:.1f}" text-anchor="{anchor}" fill="{t["muted"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="9" font-weight="600">{label}</text>')

    # Central coordinator node
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="16" fill="{t["panel"]}" stroke="{t["accent"]}" stroke-width="2" filter="url(#glow)"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{t["accent"]}"/>')
    parts.append(f'<text x="{cx}" y="{cy + 27}" text-anchor="middle" fill="{t["accent"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="10" font-weight="700">CORE.COORDINATOR</text>')

    # Real-time waveform at bottom of visual map
    wave_d = ["M 55 490"]
    for wx in range(55, 435, 10):
        wy = 490 + math.sin((wx - 55) * 0.08) * 8
        wave_d.append(f"L {wx} {wy:.1f}")
    parts.append(f'<path d="{" ".join(wave_d)}" fill="none" stroke="{t["portrait"]}" stroke-width="1.5" opacity="0.6"/>')

    # Telemetry text at bottom
    parts.append(
        f'<text x="58" y="535" fill="{t["muted"]}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="10">'
        'PTS 01024 · LIVE/MESH · SYS_OK</text>'
    )
    parts.append('</g>')

    # RIGHT PANEL - SYSTEM.INFO
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
    for theme in ("dark", "light"):
        svg = render_banner(theme)
        out_file = ASSETS / f"banner-{theme}.svg"
        out_file.write_text(svg, encoding="utf-8")
        print(f"Generated {out_file.name} ({len(svg.encode('utf-8')):,} bytes)")

if __name__ == "__main__":
    main()
