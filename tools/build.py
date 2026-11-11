#!/usr/bin/env python3
"""Rebuild the kit: Python 3 + fonttools + Pillow, with rsvg-convert on PATH."""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BLACK, WHITE = "#000000", "#FFFFFF"
NS = "{http://www.w3.org/2000/svg}"
original = ET.parse(ROOT / "00-source/mrboxs-logo-original.svg").getroot()
SHAPES = []
for el in list(original):
    if el.tag == NS + "polygon":
        pairs = el.attrib["points"].split()
        SHAPES.append("M" + " L".join(pairs) + " Z")
    elif el.tag == NS + "path" and el.get("class") == "st0":
        SHAPES.append(el.attrib["d"])

font_path = ROOT / "06-typography/AdwaitaSans-Regular.ttf"
raw_font = TTFont(font_path)
fonts = {}
for weight in (400, 500, 650):
    fonts[weight] = instantiateVariableFont(raw_font, {"wght": weight, "opsz": 32}, inplace=False)


def write(path, content):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def json_write(path, data):
    return write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def svg(w, h, body, title="mrboxs"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><title>{html.escape(title)}</title>{body}</svg>\n')


def rect(x, y, w, h, color, radius=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}"/>'


def mark(color, small=False):
    shapes = SHAPES if not small else [
        SHAPES[0], "M12.6,6 L16,4 L19.4,6 L16,8 Z", *SHAPES[3:]
    ]
    return f'<g fill="{color}">' + "".join(f'<path d="{d}"/>' for d in shapes) + "</g>"


def positioned_mark(cx, cy, height, color, small=False):
    # Artwork bounds in the supplied drawing: x=6..26, y=4.64..27.36.
    extent = 23.36 if small else 22.72
    scale = height / extent
    center_y = 15.68 if small else 16
    return f'<g transform="translate({cx:g} {cy:g}) scale({scale:g}) translate(-16 {-center_y:g})">{mark(color, small)}</g>'


def lettering(content, size, weight=400, tracking=0):
    font = fonts[weight]
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    em = font["head"].unitsPerEm
    scale = size / em
    x, paths = 0, []
    for char in content:
        name = cmap[ord(char)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        if pen.getCommands():
            paths.append(f'<path transform="translate({x:g} 0)" d="{pen.getCommands()}"/>')
        x += glyphs[name].width + tracking / scale
    return f'<g transform="scale({scale:g} {-scale:g})">{"".join(paths)}</g>', (x * scale - tracking)


def text(content, x, baseline, size, color, weight=400, tracking=0):
    body, _ = lettering(content, size, weight, tracking)
    return f'<g fill="{color}" transform="translate({x} {baseline})">{body}</g>'


WORD, WORD_WIDTH = lettering("mrboxs", 104, 650, -1.8)
WORDMARK = f'<g transform="translate(2 82)">{WORD}</g>'
WORD_CANVAS = round(WORD_WIDTH + 4, 3)


def wordmark(color, x=0, y=0, scale=1):
    return f'<g fill="{color}" transform="translate({x:g} {y:g}) scale({scale:g})">{WORDMARK}</g>'


def horizontal(color):
    return positioned_mark(46, 50, 86, color) + wordmark(color, 108, 0)


HORIZONTAL_WIDTH = round(108 + WORD_CANVAS, 3)


def render(source, destination, width=None, height=None):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["rsvg-convert"]
    if width is not None:
        cmd += ["-w", str(width)]
    if height is not None:
        cmd += ["-h", str(height)]
    subprocess.run(cmd + ["-o", str(destination), str(source)], check=True, capture_output=True)


def raster(path, sizes):
    for size in sizes:
        render(ROOT / path, (ROOT / path).with_name(Path(path).stem + f"-{size}.png"), width=size)


def tile(theme, rounded=False, small=False, safe=False):
    fg, bg = (BLACK, WHITE) if theme == "light" else (WHITE, BLACK)
    return rect(0, 0, 1024, 1024, bg, 192 if rounded else 0) + positioned_mark(512, 512, 532 if safe else 672, fg, small)


def favicon(theme, small=True):
    fg, bg = (BLACK, WHITE) if theme == "light" else (WHITE, BLACK)
    return rect(0, 0, 32, 32, bg, 3) + positioned_mark(16, 16, 28, fg, small)


def badge(theme):
    fg, bg = (BLACK, WHITE) if theme == "light" else (WHITE, BLACK)
    # Preserve the original tile radius and original artwork-to-tile proportions.
    return rect(0, 0, 1024, 1024, bg, 96) + f'<g transform="scale(32)">{mark(fg)}</g>'


def build_logos():
    for theme, color in (("light", BLACK), ("dark", WHITE)):
        for name, w, h, body in (
            ("symbol", 256, 256, positioned_mark(128, 128, 192, color)),
            ("symbol-small", 32, 32, positioned_mark(16, 16, 28, color, True)),
            ("horizontal", HORIZONTAL_WIDTH, 100, horizontal(color)),
            ("wordmark", WORD_CANVAS, 100, wordmark(color)),
            ("stacked", 320, 356, positioned_mark(160, 121, 224, color) + wordmark(color, (320-WORD_CANVAS)/2, 251)),
            ("badge", 1024, 1024, badge(theme)),
        ):
            path = f"01-logos/{theme}/mrboxs-{name}.svg"
            write(path, svg(w, h, body, f"mrboxs {name} · {theme}"))
            raster(path, (256, 512, 1024) if name in ("symbol", "badge", "stacked") else ((16, 24, 32, 48, 64) if name == "symbol-small" else (512, 1024, 2048)))
    for name, w, h, body in (
        ("symbol", 256, 256, positioned_mark(128, 128, 192, "currentColor")),
        ("horizontal", HORIZONTAL_WIDTH, 100, horizontal("currentColor")),
        ("wordmark", WORD_CANVAS, 100, wordmark("currentColor")),
    ):
        write(f"01-logos/inline/mrboxs-{name}-currentcolor.svg", svg(w, h, body))
        styles = '<style>:root{color:#000}@media(prefers-color-scheme:dark){:root{color:#fff}}</style>'
        write(f"01-logos/adaptive/mrboxs-{name}-auto.svg", svg(w, h, styles + body))


def build_web():
    for theme in ("light", "dark"):
        base = f"02-icons/web/{theme}"
        for small in (True, False):
            name = "favicon-small" if small else "favicon-full"
            p = write(f"{base}/{name}.svg", svg(32, 32, favicon(theme, small), "mrboxs favicon"))
            for size in ((16, 24, 32) if small else (48, 64)):
                render(p, ROOT / base / f"favicon-{size}.png", size, size)
        # The SVG favicon deliberately uses the small drawing at every size.
        shutil.copyfile(ROOT / base / "favicon-small.svg", ROOT / base / "favicon.svg")
        images = [Image.open(ROOT / base / f"favicon-{s}.png").convert("RGBA") for s in (16, 32, 48)]
        images[-1].save(ROOT / base / "favicon.ico", sizes=[(s, s) for s in (16, 32, 48)], append_images=images[:-1])
        for name, size, safe in (("apple-touch-icon", 180, False), ("icon-192", 192, False),
                                 ("icon-512", 512, False), ("maskable-192", 192, True), ("maskable-512", 512, True)):
            p = write(f"{base}/{name}.svg", svg(1024, 1024, tile(theme, safe=safe), f"mrboxs {name}"))
            render(p, ROOT / base / f"{name}.png", size, size)
        fg, bg = (BLACK, WHITE) if theme == "light" else (WHITE, BLACK)
        json_write(f"{base}/site.webmanifest", {
            "id": "/", "name": "mrboxs", "short_name": "mrboxs", "start_url": "/", "scope": "/",
            "display": "standalone", "theme_color": bg, "background_color": bg,
            "icons": [{"src": f"./icon-{s}.png", "sizes": f"{s}x{s}", "type": "image/png", "purpose": "any"} for s in (192, 512)] +
                     [{"src": f"./maskable-{s}.png", "sizes": f"{s}x{s}", "type": "image/png", "purpose": "maskable"} for s in (192, 512)]
        })
    adaptive = '<style>:root{--mark:#000;--tile:#fff}@media(prefers-color-scheme:dark){:root{--mark:#fff;--tile:#000}}</style>'
    write("02-icons/web/favicon.svg", svg(32, 32, adaptive + rect(0, 0, 32, 32, "var(--tile)", 3) + positioned_mark(16, 16, 28, "var(--mark)", True), "mrboxs favicon"))
    shutil.copyfile(ROOT / "02-icons/web/dark/favicon.ico", ROOT / "02-icons/web/favicon.ico")
    write("02-icons/web/safari-pinned-tab.svg", svg(32, 32, positioned_mark(16, 16, 28, BLACK, True), "mrboxs pinned tab"))


def build_native():
    for theme in ("light", "dark"):
        for kind in ("square", "rounded"):
            path = f"02-icons/app/{theme}/mrboxs-app-{kind}.svg"
            write(path, svg(1024, 1024, tile(theme, kind == "rounded"), f"mrboxs app icon · {theme}"))
            raster(path, (64, 128, 256, 512, 1024))
        square = ROOT / f"02-icons/app/{theme}/mrboxs-app-square-1024.png"
        rounded = ROOT / f"02-icons/app/{theme}/mrboxs-app-rounded-1024.png"
        img = Image.open(rounded)
        small_frames = [Image.open(ROOT / f"02-icons/web/{theme}/favicon-{s}.png").convert("RGBA") for s in (16, 24, 32)]
        img.save(ROOT / f"02-icons/app/{theme}/mrboxs-windows.ico", sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)], append_images=small_frames)
        img.save(ROOT / f"02-icons/app/{theme}/mrboxs-macos.icns")
        ios_dir = ROOT / f"02-icons/app/ios/{theme}/AppIcon.appiconset"
        ios_dir.mkdir(parents=True, exist_ok=True)
        specs = [("iphone", s, scale) for s in (20, 29, 40, 60) for scale in (2, 3)] + [("ipad", s, scale) for s in (20, 29, 40, 76) for scale in (1, 2)] + [("ipad", 83.5, 2), ("ios-marketing", 1024, 1)]
        entries = []
        for idiom, point, scale in specs:
            px = round(point * scale)
            filename = f"icon-{px}.png"
            Image.open(square).convert("RGB").resize((px, px), Image.Resampling.LANCZOS).save(ios_dir / filename)
            entries.append({"filename": filename, "idiom": idiom, "scale": f"{scale}x", "size": f"{point:g}x{point:g}"})
        json_write(str(ios_dir.relative_to(ROOT) / "Contents.json"), {"images": entries, "info": {"author": "xcode", "version": 1}})
    android = "02-icons/app/android/res"
    for theme in ("light", "dark"):
        fg, bg = (BLACK, WHITE) if theme == "light" else (WHITE, BLACK)
        suffix = "" if theme == "light" else "-night"
        write(f"{android}/values{suffix}/colors.xml", f'<resources><color name="mrboxs_surface">{bg}</color><color name="mrboxs_mark">{fg}</color></resources>\n')
        source = ROOT / f"02-icons/app/{theme}/mrboxs-app-square.svg"
        for density, size in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
            dest = ROOT / android / f"mipmap{suffix}-{density}"
            render(source, dest / "ic_launcher.png", size, size)
            image = Image.open(dest / "ic_launcher.png").convert("RGBA")
            mask = Image.new("L", image.size)
            ImageDraw.Draw(mask).ellipse((0, 0, size-1, size-1), fill=255)
            image.putalpha(mask)
            image.save(dest / "ic_launcher_round.png")
    paths = "".join(f'<path android:fillColor="@color/mrboxs_mark" android:pathData="{d}"/>' for d in SHAPES)
    vector = f'<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="32" android:viewportHeight="32"><group android:scaleX="0.72" android:scaleY="0.72" android:pivotX="16" android:pivotY="16">{paths}</group></vector>\n'
    write(f"{android}/drawable/ic_launcher_foreground.xml", vector)
    mono = vector.replace("@color/mrboxs_mark", "#000000")
    write(f"{android}/drawable/ic_launcher_monochrome.xml", mono)
    adaptive = '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"><background android:drawable="@color/mrboxs_surface"/><foreground android:drawable="@drawable/ic_launcher_foreground"/>{}</adaptive-icon>\n'
    for filename in ("ic_launcher", "ic_launcher_round"):
        write(f"{android}/mipmap-anydpi-v26/{filename}.xml", adaptive.format(""))
        write(f"{android}/mipmap-anydpi-v33/{filename}.xml", adaptive.format('<monochrome android:drawable="@drawable/ic_launcher_monochrome"/>'))


def motif(color):
    return f'<g fill="none" stroke="{color}" stroke-width="12">' + "".join(f'<path d="M-80 {y} L240 {y+185} L560 {y}"/>' for y in range(-280, 900, 110)) + "</g>"


def build_social():
    for theme in ("light", "dark"):
        fg, bg = (BLACK, WHITE) if theme == "light" else (WHITE, BLACK)
        muted = "#DADADA" if theme == "light" else "#292929"
        for size in (400, 800, 1024):
            p = write(f"03-social/{theme}/avatar.svg", svg(1024, 1024, tile(theme, safe=True), "mrboxs avatar"))
            render(p, ROOT / f"03-social/{theme}/avatar-{size}.png", size, size)
        for name, width, height in (("social-card", 1200, 630), ("banner", 1500, 500)):
            scale = 1.5 if name == "social-card" else 1.9
            body = rect(0, 0, width, height, bg)
            body += f'<defs><clipPath id="pattern-area"><rect x="{width-300}" y="0" width="300" height="{height}"/></clipPath></defs>'
            body += f'<g clip-path="url(#pattern-area)"><g transform="translate({width-420} 0)">{motif(muted)}</g></g>'
            body += f'<g transform="translate(76 {(height-100*scale)/2:g}) scale({scale})">{horizontal(fg)}</g>'
            p = write(f"03-social/{theme}/{name}.svg", svg(width, height, body, f"mrboxs {name}"))
            render(p, ROOT / f"03-social/{theme}/{name}-{width}x{height}.png", width, height)
        p = write(f"04-brand/pattern-{theme}.svg", svg(800, 800, rect(0, 0, 800, 800, bg) + f'<g transform="translate(160 0)">{motif(muted)}</g>', "mrboxs layered pattern"))
        render(p, p.with_suffix(".png"), 800, 800)


def build_boards():
    # Fixed artwork for the handover, rather than a fictional application UI.
    width, height = 1600, 1510
    body = rect(0, 0, width, height, "#F3F3F3")
    body += text("mrboxs", 64, 100, 68, BLACK, 650, -1)
    body += text("Brand kit / 01", 1270, 86, 22, BLACK, 500)
    body += text("Identitas yang sama. Di setiap ukuran.", 66, 147, 26, "#555555")
    body += rect(40, 196, 760, 510, WHITE) + rect(800, 196, 760, 510, BLACK)
    for cx, fg, label in ((420, BLACK, "Light"), (1180, WHITE, "Dark")):
        body += positioned_mark(cx, 385, 258, fg)
        body += wordmark(fg, cx-WORD_CANVAS*0.85/2, 531, .85)
        body += text(label, cx-25, 672, 18, fg, 500)
    body += text("Satu simbol, banyak tempat.", 64, 779, 34, BLACK, 650)
    # Original rounded badge, platform square, circular avatar, micro favicon.
    for x, theme in ((64, "dark"), (258, "light")):
        body += f'<g transform="translate({x} 819) scale(.15234375)">{tile(theme, True)}</g>'
    body += '<defs><clipPath id="avatar"><circle cx="542" cy="897" r="78"/></clipPath></defs>'
    body += f'<g clip-path="url(#avatar)"><g transform="translate(464 819) scale(.15234375)">{tile("dark", safe=True)}</g></g>'
    for x, theme in ((662, "dark"), (754, "light")):
        body += f'<g transform="translate({x} 861) scale(2.25)">{favicon(theme)}</g>'
    body += text("App icon", 66, 1014, 20, "#555555", 500)
    body += text("Avatar", 470, 1014, 20, "#555555", 500)
    body += text("Favicon / small cut", 660, 1014, 20, "#555555", 500)
    body += rect(950, 820, 582, 200, BLACK)
    body += f'<g transform="translate(988 870) scale(.98)">{horizontal(WHITE)}</g>'
    body += text("Horizontal lockup", 951, 1062, 20, "#555555", 500)
    body += rect(40, 1120, 760, 326, WHITE) + rect(800, 1120, 760, 326, BLACK)
    for x, fg, bg in ((64, BLACK, WHITE), (824, WHITE, BLACK)):
        body += text("mrboxs", x, 1200, 42, fg, 650, -.5)
        body += text("Bentuk kubus. Ritme lapisan.", x, 1242, 24, fg)
        body += text("SVG / PNG / ICO / ICNS", x, 1367, 21, fg, 500)
        body += text("Logo, ikon aplikasi, web, dan sosial.", x, 1405, 21, fg)
    body += rect(598, 1160, 130, 130, BLACK)
    body += rect(1358, 1160, 130, 130, WHITE)
    body += text("#000000", 599, 1328, 20, BLACK, 500)
    body += text("#FFFFFF", 1359, 1328, 20, WHITE, 500)
    p = write("05-guidelines/brand-overview.svg", svg(width, height, body, "mrboxs brand kit overview"))
    render(p, p.with_suffix(".png"), width, height)

    # Native pixels plus nearest-neighbour enlargement make small-size defects visible.
    sheet = Image.new("RGB", (1440, 900), "#E6E6E6")
    draw = ImageDraw.Draw(sheet)
    font_ui = __import__("PIL.ImageFont", fromlist=["truetype"]).truetype(str(font_path), 24)
    draw.text((40, 25), "mrboxs / Small-size and crop checks", fill="black", font=font_ui)
    for row, theme in enumerate(("light", "dark")):
        y = 105 + row * 270
        bg = WHITE if theme == "light" else BLACK
        fg = BLACK if theme == "light" else WHITE
        draw.rectangle((20, y-20, 1420, y+235), fill=bg)
        for col, size in enumerate((16, 24, 32, 48, 64)):
            x = 50 + col*270
            image = Image.open(ROOT / f"02-icons/web/{theme}/favicon-{size}.png")
            sheet.paste(image, (x, y+30), image)
            nearest = image.resize((128, 128), Image.Resampling.NEAREST)
            sheet.paste(nearest, (x+80, y+30), nearest)
            draw.text((x, y+180), f"{size}px  /  pixels", fill=fg, font=font_ui)
    for col, theme in enumerate(("light", "dark")):
        image = Image.open(ROOT / f"03-social/{theme}/avatar-400.png").convert("RGBA").resize((160, 160), Image.Resampling.LANCZOS)
        mask = Image.new("L", image.size)
        ImageDraw.Draw(mask).ellipse((0, 0, 159, 159), fill=255)
        sheet.paste(image, (50+col*240, 695), mask)
    draw.text((565, 725), "Circular avatar: all artwork stays inside crop.", fill="black", font=font_ui)
    draw.text((565, 770), "16-32px: simplified top. 48px+: full original detail.", fill="black", font=font_ui)
    sheet.save(ROOT / "05-guidelines/size-and-crop-checks.png")


def inventory():
    rows = []
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and p.name not in ("asset-inventory.json", "SHA256SUMS.txt") and not set(p.relative_to(ROOT).parts).intersection({".git", ".venv", "__pycache__", ".DS_Store"}):
            rows.append({"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size})
    json_write("asset-inventory.json", {"brand": "mrboxs", "version": "1.0.0", "assets": rows})
    lines = []
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS.txt" and not set(p.relative_to(ROOT).parts).intersection({".git", ".venv", "__pycache__", ".DS_Store"}):
            lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}")
    write("SHA256SUMS.txt", "\n".join(lines) + "\n")


if __name__ == "__main__":
    for action in (build_logos, build_web, build_native, build_social, build_boards):
        action()
        print(f"Built {action.__name__}", flush=True)
    inventory()
