#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Open Graph card web/public/og-default.png (1200x630).

Pure stdlib: zlib + struct PNG encoder, 5x7 bitmap font. No Pillow, no headless
browser, no network — it must run inside the content pipeline, not as a separate
design step.

    python scripts/make_og.py
"""
import struct
import sys
import zlib
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

W, H = 1200, 630
OUT = Path(r"C:\BLENDER ai\web\public\og-default.png")

BG1 = (11, 15, 20)
BG2 = (24, 34, 48)
ACCENT = (76, 157, 240)
ACCENT2 = (126, 224, 192)
TEXT = (230, 237, 246)
DIM = (159, 176, 196)

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "11110", "10001", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "11110", "10000", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "11100", "10100", "10010", "10001", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00011", "00110", "00100", "01100", "11000", "11111"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    " ": ["00000"] * 7,
}

px = [[(0, 0, 0)] * W for _ in range(H)]


def rect(x0, y0, w, h, color, alpha=1.0):
    for y in range(max(0, y0), min(H, y0 + h)):
        row = px[y]
        for x in range(max(0, x0), min(W, x0 + w)):
            if alpha >= 1.0:
                row[x] = color
            else:
                r, g, b = row[x]
                row[x] = (int(r + (color[0] - r) * alpha),
                          int(g + (color[1] - g) * alpha),
                          int(b + (color[2] - b) * alpha))


def text(s, x0, y0, scale, color, alpha=1.0):
    cx = x0
    for ch in s.upper():
        for gy, row in enumerate(FONT.get(ch, FONT[" "])):
            for gx, bit in enumerate(row):
                if bit == "1":
                    rect(cx + gx * scale, y0 + gy * scale, scale, scale, color, alpha)
        cx += 6 * scale
    return cx


def main():
    for y in range(H):
        for x in range(W):
            t = (x / W * 0.55 + y / H * 0.45)
            px[y][x] = (int(BG1[0] + (BG2[0] - BG1[0]) * t),
                        int(BG1[1] + (BG2[1] - BG1[1]) * t),
                        int(BG1[2] + (BG2[2] - BG1[2]) * t))

    rect(0, 0, 10, H, ACCENT)
    rect(10, 0, 4, H, ACCENT2)

    text("BLENDER", 90, 150, 12, TEXT)
    text("AI WIKI", 90, 250, 12, ACCENT)
    text("PROMPTS - SETUPS - WORKFLOWS - CASES", 92, 390, 5, DIM, 0.95)

    cx = 90
    for code in ["RU", "EN", "ES", "DE", "ZH"]:
        w = len(code) * 5 * 5 + 40
        rect(cx, 440, w, 44, (255, 255, 255), 0.05)
        rect(cx, 440, w, 2, ACCENT if code == "RU" else (255, 255, 255), 0.6)
        text(code, cx + 20, 458, 5, TEXT if code == "RU" else DIM)
        cx += w + 14

    # knowledge graph motif — the site is a linked corpus, not a blog
    for row in range(6):
        for col in range(6):
            gx, gy = 760 + col * 62, 190 + row * 62
            d = 9 if (row * 6 + col) % 5 == 0 else 5
            c = ACCENT2 if (row + col) % 3 == 0 else ACCENT
            rect(gx, gy, d, d, c, 0.75 if d == 9 else 0.4)
            if d == 9:
                if col < 5:
                    rect(gx + 9, gy + 3, 44, 3, ACCENT, 0.22)
                if row < 5:
                    rect(gx + 3, gy + 9, 3, 44, ACCENT, 0.22)

    raw = b"".join(b"\x00" + bytes(v for p in row for v in p) for row in px)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    print(f"OK {OUT} {OUT.stat().st_size // 1024} KB {W}x{H}")


if __name__ == "__main__":
    main()
