#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Social images for the site.

Three jobs, in order:

  1. og-default.png  — the site card every listing page uses (pure stdlib: zlib +
     struct PNG encoder, 5x7 bitmap font; no Pillow, no headless browser, no
     network, so it runs inside the content pipeline).
  2. og/<id>.png     — one card per published article: title, category,
     difficulty, language. Pillow + a real TrueType font, because 222 titles in
     5 languages include Cyrillic and CJK and a 5x7 ASCII bitmap font cannot
     draw them. Falls back to (1)'s encoder and says so, loudly, if Pillow or
     a usable font is missing.
  3. favicon.ico, apple-touch-icon.png, icon-192.png, icon-512.png — the same
     geometry as public/favicon.svg, rasterised with Pillow.

Idempotent: card filenames are derived from the entry id alone, and a card is
re-rendered only when it is missing, empty, or older than the database or this
script. A second run over an unchanged database renders nothing. Cards whose
entry no longer exists are pruned, so `public/og/` never accumulates orphans.

    python scripts/make_og.py               # everything
    python scripts/make_og.py --default     # only the site card
    python scripts/make_og.py --force       # re-render every card
"""
import json
import os
import struct
import sys
import zlib
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent.parent   # .../BLENDER ai
WIKI = ROOT / "WIKI"
WEB = ROOT / "web"
DB = WIKI / "db" / "wiki_database.json"

W, H = 1200, 630
OUT = WEB / "public" / "og-default.png"
OG_DIR = WEB / "public" / "og"

BG1 = (11, 15, 20)
BG2 = (24, 34, 48)
ACCENT = (76, 157, 240)
ACCENT2 = (126, 224, 192)
TEXT = (230, 237, 246)
DIM = (159, 176, 196)
STAR = (245, 197, 66)

SITE_NAME = "BLENDER AI WIKI"

# Icon geometry, as fractions of the canvas. public/favicon.svg declares the same
# numbers in user units on a 512 grid; keep the two in step.
ICON_BG_TOP = (13, 17, 23)
ICON_BG_BOTTOM = (28, 40, 56)
ICON_RADIUS = 0.219          # 112 / 512
ICON_LINE = 0.066            # 34 / 512
ICON_NODE_R = 0.121          # 62 / 512
ICON_NODES = ((0.50, 0.30, ACCENT2), (0.24, 0.66, ACCENT), (0.76, 0.66, ACCENT))
ICON_EDGES = ((1, 0), (0, 2))

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


def write_png(path, width, height, rows):
    """rows: iterable of iterable of (r,g,b). Writes a truecolour PNG, stdlib only."""
    raw = b"".join(b"\x00" + bytes(v for p in row for v in p) for row in rows)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def default_card():
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

    write_png(OUT, W, H, px)
    return f"OK {OUT} {OUT.stat().st_size // 1024} KB {W}x{H}"


# --------------------------------------------------------------- Pillow side
try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except Exception:                                       # pragma: no cover
    HAVE_PIL = False

WIN_FONTS = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
BOLD_FONTS = ["arialbd.ttf", "segoeuib.ttf", "verdanab.ttf", "tahomabd.ttf",
              "noto-bold.ttf", "DejaVuSans-Bold.ttf", "msyhbd.ttc"]
REG_FONTS = ["arial.ttf", "segoeui.ttf", "verdana.ttf", "tahoma.ttf",
             "noto.ttf", "DejaVuSans.ttf", "msyh.ttc"]

_font_cache = {}
_cmap_cache = {}


def _truetype(name, size):
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(WIN_FONTS / name), size)
    return _font_cache[key]


def _covers(name, chars):
    """True when the font's cmap has every character — Pillow silently draws
    .notdef boxes for what it lacks, which is how a Cyrillic title ends up as a
    row of empty rectangles on a card."""
    if name not in _cmap_cache:
        cmap = None
        try:
            from fontTools.ttLib import TTFont, TTCollection
            path = WIN_FONTS / name
            font = TTCollection(str(path)).fonts[0] if path.suffix.lower() == ".ttc" else TTFont(str(path))
            cmap = set(font.getBestCmap().keys())
        except Exception:
            cmap = None
        _cmap_cache[name] = cmap
    cmap = _cmap_cache[name]
    return True if cmap is None else all(ord(c) in cmap for c in chars)


def font_for(s, size, bold=True):
    """First installed font that can actually draw `s`."""
    wanted = set(s) - {" "}
    for name in (BOLD_FONTS if bold else REG_FONTS):
        if (WIN_FONTS / name).exists() and _covers(name, wanted):
            try:
                return _truetype(name, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _gradient(size, top, bottom):
    """Vertical gradient, built as a one-row image and stretched."""
    w, h = size
    strip = Image.new("RGB", (1, h))
    strip.putdata([tuple(int(top[i] + (bottom[i] - top[i]) * (y / max(1, h - 1)))
                         for i in range(3)) for y in range(h)])
    return strip.resize((w, h), Image.BILINEAR)


def _wrap(draw, s, font, max_w):
    """Greedy word wrap; CJK has no spaces, so break per character there."""
    if any("\u2e80" <= c <= "\u9fff" or "\uff00" <= c <= "\uffef" for c in s):
        lines, cur = [], ""
        for ch in s:
            cur += ch
            if draw.textlength(cur, font=font) > max_w and len(cur) > 1:
                lines.append(cur[:-1])
                cur = cur[-1]
        if cur:
            lines.append(cur)
        return lines
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and draw.textlength(trial, font=font) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]


def _star(draw, cx, cy, r, color):
    import math
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    draw.polygon(pts, fill=color)


def article_card(m):
    """One 1200x630 card. Real data only: category, title, difficulty, language,
    word count. Nothing here is invented if the database does not carry it."""
    img = _gradient((W, H), BG1, BG2)
    d = ImageDraw.Draw(img)
    pad = 90

    d.rectangle((0, 0, 10, H), fill=ACCENT)
    d.rectangle((10, 0, 14, H), fill=ACCENT2)

    # category + rule
    cat = str(m.get("category") or "").replace("_", " ").upper()
    d.text((pad, 74), cat or "ARTICLE", font=font_for(cat, 30), fill=ACCENT)
    d.rectangle((pad, 126, pad + 64, 130), fill=ACCENT2)

    # title: shrink until it fits three lines inside the block
    title = str(m.get("title") or m.get("id") or "")
    max_w = W - pad - 70
    chosen, lines, size = None, [], 30
    for size in range(74, 29, -4):
        f = font_for(title, size)
        lines = _wrap(d, title, f, max_w)
        if len(lines) <= 3:
            chosen = f
            break
    if chosen is None:
        chosen = font_for(title, 30)
        lines = _wrap(d, title, chosen, max_w)[:3]
    lh = int(size * 1.24)
    y = 176
    for line in lines:
        d.text((pad, y), line, font=chosen, fill=TEXT)
        y += lh

    # language badge, top right: white pill, accent code
    lang = str(m.get("language") or "").upper()[:3]
    if lang:
        bf = font_for(lang, 30)
        bw = int(d.textlength(lang, font=bf)) + 44
        bx = W - pad - bw
        d.rounded_rectangle((bx, 62, bx + bw, 114), radius=26, fill=(233, 240, 248))
        d.text((bx + 22, 76), lang, font=bf, fill=(17, 24, 33))

    # difficulty: filled stars for the level, outline for the missing ones
    diff = int(m.get("difficulty") or 0)
    if diff > 0:
        r, gap = 15, 14
        x, y0 = pad, H - 118
        for i in range(3):
            cx = x + i * (2 * r + gap) + r
            if i < min(3, diff):
                _star(d, cx, y0, r, STAR)
            else:
                d.ellipse((cx - r, y0 - r, cx + r, y0 + r), outline=(70, 82, 98), width=3)

    words = int(m.get("word_count") or 0)
    mins = max(1, round(words / 180)) if words else 0
    meta = f"{lang or '—'} · {mins} MIN READ" if mins else (lang or "")
    d.text((pad, H - 84), SITE_NAME, font=font_for(SITE_NAME, 26), fill=DIM)
    if meta:
        f = font_for(meta, 24)
        d.text((W - pad - d.textlength(meta, font=f), H - 82), meta, font=f, fill=DIM)
    return img


def icon(size, transparent=True, maskable=False):
    """Raster of public/favicon.svg: dark rounded square, three connected nodes.

    `maskable` is the Android adaptive-icon variant: the platform crops the file
    to its own shape, so the background goes square edge to edge and the motif
    is pulled into the middle 80% (the safe zone an adaptive mask can guarantee).
    Claiming `purpose: maskable` for the plain icon would be a promise the
    geometry does not keep."""
    s = size
    bg = _gradient((s, s), ICON_BG_TOP, ICON_BG_BOTTOM)
    d = ImageDraw.Draw(bg)
    lw = max(1, int(s * ICON_LINE))
    k = 0.62 if maskable else 1.0
    pts = [(0.5 + (x - 0.5) * k, 0.5 + (y - 0.5) * k) for x, y, _ in ICON_NODES]
    for a, b in ICON_EDGES:
        d.line([(pts[a][0] * s, pts[a][1] * s), (pts[b][0] * s, pts[b][1] * s)],
               fill=(52, 102, 162), width=int(lw * k) or 1)
    for (fx, fy, color), (px_, py_) in zip(ICON_NODES, pts):
        r = s * ICON_NODE_R * k
        d.ellipse((px_ * s - r, py_ * s - r, px_ * s + r, py_ * s + r), fill=color)
    if not transparent:
        return bg
    mask = Image.new("L", (s, s), 0)
    if not maskable:
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, s - 1, s - 1), radius=int(s * ICON_RADIUS), fill=255)
    else:
        # Full bleed: the platform supplies the shape, so rounding here would
        # leave transparent corners behind every mask it applies.
        mask.paste(255, (0, 0, s, s))
    out = bg.convert("RGBA")
    out.putalpha(mask)
    return out


def write_icons():
    out = []
    base = icon(512)
    icon(192).save(WEB / "public" / "icon-192.png", "PNG", optimize=True)
    out.append("icon-192.png 192x192")
    base.save(WEB / "public" / "icon-512.png", "PNG", optimize=True)
    out.append("icon-512.png 512x512")
    icon(512, maskable=True).save(WEB / "public" / "icon-maskable-512.png", "PNG", optimize=True)
    out.append("icon-maskable-512.png 512x512 maskable")
    # iOS does not mask apple-touch-icon itself and does not like transparency.
    icon(180, transparent=False).save(WEB / "public" / "apple-touch-icon.png", "PNG", optimize=True)
    out.append("apple-touch-icon.png 180x180")
    base.save(WEB / "public" / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    out.append("favicon.ico 16/32/48")
    return out


# ------------------------------------------------------------------- article DB
import re  # noqa: E402  (kept next to the only code that needs it)

REAL_TRANSLATIONS = {"human", "ai"}


def slugify(s):
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", str(s).lower()))


def orig_id(m):
    return m.get("orig_id") or re.sub(r"__[a-z]{2}$", "", str(m["id"]))


def card_name(meta):
    """Deterministic from the entry id alone. The `__<lang>` suffix of a
    translation is part of the id, so the five language versions of one article
    get five files instead of overwriting one another."""
    return f"{slugify(meta['id'])}.png"


def published_metas(db):
    """The publication rule, mirrored from web/src/lib/publish.mjs.

      original                                -> published
      human / ai translation in another lang  -> published
      translation in the original's own lang   -> shadow, not published
      template / legacy / unmarked             -> not a translation, not published

    Shadow mirrors are excluded on purpose: they resolve to the original's URL,
    so a card for one would be a second file the original's page never uses."""
    orig_lang = {}
    for e in db["entries"]:
        m = e["meta"]
        if not m.get("is_translation"):
            orig_lang[orig_id(m)] = m["language"]
    out = []
    for e in db["entries"]:
        m = e["meta"]
        if m.get("is_translation"):
            if m.get("translation") not in REAL_TRANSLATIONS:
                continue
            if orig_lang.get(orig_id(m)) == m["language"]:
                continue
        out.append(m)
    return out


def _stale(png, db_mtime, script_mtime):
    try:
        st = png.stat()
    except FileNotFoundError:
        return True
    return st.st_size == 0 or st.st_mtime < db_mtime or st.st_mtime < script_mtime


def article_cards(force=False):
    if not HAVE_PIL:
        print("[!] Pillow is not installed — og-default.png was written, per-article "
              "cards were NOT (pip install pillow). Every article keeps pointing at "
              "the site card; nothing silently pretends otherwise.")
        return 0
    if not DB.exists():
        print(f"[!] {DB} not found — skipping per-article cards")
        return 0

    metas = published_metas(json.loads(DB.read_text(encoding="utf-8")))
    OG_DIR.mkdir(parents=True, exist_ok=True)
    db_mtime = DB.stat().st_mtime
    script_mtime = Path(__file__).stat().st_mtime

    written = skipped = 0
    for m in metas:
        png = OG_DIR / card_name(m)
        if not force and not _stale(png, db_mtime, script_mtime):
            skipped += 1
            continue
        image_card = article_card(m)
        image_card.save(png, "PNG", optimize=True)
        written += 1

    expected = {card_name(m) for m in metas}
    pruned = 0
    for f in OG_DIR.glob("*.png"):
        if f.name not in expected:
            f.unlink()
            pruned += 1

    kb = sum((OG_DIR / n).stat().st_size for n in expected) // 1024
    print(f"OK {OG_DIR}: {written} rendered, {skipped} up to date, "
          f"{len(expected)} total ({kb} KB){', %d stale pruned' % pruned if pruned else ''}")
    return written


def main():
    force = "--force" in sys.argv
    only_default = "--default" in sys.argv

    print(default_card())

    if only_default:
        return 0
    if not HAVE_PIL:
        article_cards()
        return 0

    article_cards(force=force)
    for line in write_icons():
        print(f"OK web/public/{line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
