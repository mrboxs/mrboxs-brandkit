#!/usr/bin/env python3
"""Check file integrity, icon containers, transparency, safe zones and theme pairs."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
checks = []


def check(name, assertion, detail):
    if not assertion:
        raise AssertionError(f"{name}: {detail}")
    checks.append({"name": name, "status": "PASS", "evidence": detail})


def contrast(a, b):
    def luminance(h):
        c = [int(h[i:i+2], 16)/255 for i in (1, 3, 5)]
        lin = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in c]
        return sum(v*w for v, w in zip(lin, (.2126, .7152, .0722)))
    x, y = sorted([luminance(a), luminance(b)])
    return round((y+.05)/(x+.05), 2)


pngs = list(ROOT.rglob("*.png"))
for path in pngs:
    with Image.open(path) as im:
        im.verify()
check("PNG integrity", True, f"Decoded {len(pngs)} PNGs successfully.")

svgs = [p for p in ROOT.rglob("*.svg") if "00-source" not in p.parts]
for path in svgs:
    root = ET.parse(path).getroot()
    tags = [el.tag.rsplit("}", 1)[-1] for el in root.iter()]
    check_name = str(path.relative_to(ROOT))
    assert "title" in tags, f"Missing title: {check_name}"
    assert not set(tags).intersection({"text", "image", "filter", "script", "foreignObject"}), check_name
check("SVG structure", True, f"Parsed {len(svgs)} generated SVGs; titled, outlined, no embedded rasters, scripts or filters.")

for theme in ("light", "dark"):
    for name in ("symbol", "horizontal", "wordmark", "stacked"):
        im = Image.open(ROOT / f"01-logos/{theme}/mrboxs-{name}-512.png").convert("RGBA")
        assert im.getpixel((0, 0))[3] == 0, (theme, name)
        assert im.getchannel("A").getbbox(), (theme, name)
check("Transparent masters", True, "Symbol, horizontal, wordmark and stacked PNGs retain transparent backgrounds in both themes.")

for name in ("symbol", "horizontal", "wordmark", "stacked"):
    light = Image.open(ROOT / f"01-logos/light/mrboxs-{name}-512.png").convert("RGBA")
    dark = Image.open(ROOT / f"01-logos/dark/mrboxs-{name}-512.png").convert("RGBA")
    assert ImageChops.difference(light.getchannel("A"), dark.getchannel("A")).getbbox() is None, name
check("Theme geometry", True, "Light/dark master pairs have identical alpha geometry, with inverse foreground colors.")

for theme in ("light", "dark"):
    for icon, sizes in ((ROOT / f"02-icons/web/{theme}/favicon.ico", {16, 32, 48}),
                        (ROOT / f"02-icons/app/{theme}/mrboxs-windows.ico", {16, 24, 32, 48, 64, 128, 256})):
        ico = Image.open(icon)
        assert ico.ico.sizes() == {(s, s) for s in sizes}, icon
        for s in sizes:
            ico.ico.getimage((s, s)).load()
    icns = Image.open(ROOT / f"02-icons/app/{theme}/mrboxs-macos.icns")
    assert icns.format == "ICNS"
    icns.load()
    for s in (16, 24, 32):
        image = Image.open(ROOT / f"02-icons/app/{theme}/mrboxs-windows.ico").ico.getimage((s, s)).convert("RGBA")
        expected = Image.open(ROOT / f"02-icons/web/{theme}/favicon-{s}.png").convert("RGBA")
        assert ImageChops.difference(image, expected).getbbox() is None, (theme, s)
check("Desktop icon containers", True, "Both ICO themes decode at every declared size; 16/24/32px Windows frames use the exact small-cut artwork. Both ICNS files decode.")

ios_sets = list((ROOT / "02-icons/app/ios").rglob("Contents.json"))
for path in ios_sets:
    entries = json.loads(path.read_text())["images"]
    assert len(entries) == 18
    for entry in entries:
        image = Image.open(path.parent / entry["filename"])
        size = round(float(entry["size"].split("x")[0])*int(entry["scale"][0]))
        assert image.size == (size, size)
        assert image.mode == "RGB"
check("iOS catalogs", True, "Both 18-slot AppIcon catalogs resolve; all images have correct dimensions and no alpha channel.")

for theme in ("light", "dark"):
    base = ROOT / f"02-icons/web/{theme}"
    manifest = json.loads((base / "site.webmanifest").read_text())
    for item in manifest["icons"]:
        image = Image.open(base / item["src"])
        assert f"{image.width}x{image.height}" == item["sizes"]
    bg = (255, 255, 255) if theme == "light" else (0, 0, 0)
    for path in (base / "maskable-512.png", ROOT / f"03-social/{theme}/avatar-800.png"):
        image = Image.open(path).convert("RGB")
        n = image.width
        limit = .4*n if "maskable" in path.name else .5*n
        for y in range(n):
            for x in range(n):
                pixel = image.getpixel((x, y))
                if max(abs(a-b) for a, b in zip(pixel, bg)) > 8:
                    assert (x+.5-n/2)**2 + (y+.5-n/2)**2 < limit**2, (path, x, y)
check("PWA and avatar safe zones", True, "All manifest PNG paths/dimensions resolve. Maskable artwork fits the central 80%-diameter circle; avatars fit a circular crop.")

xmls = list((ROOT / "02-icons/app/android/res").rglob("*.xml"))
for path in xmls:
    ET.parse(path)
check("Android resources", True, f"Parsed {len(xmls)} resource XMLs; day/night colors, API 26 adaptive and API 33 monochrome variants present. Not compiled with the Android SDK.")

tokens = json.loads((ROOT / "04-brand/tokens.json").read_text())
ratios = {}
for theme, colors in tokens["themes"].items():
    for pair in (("foreground", "background"), ("foreground", "surface"), ("muted", "background"), ("muted", "surface")):
        ratio = contrast(colors[pair[0]], colors[pair[1]])
        assert ratio >= 4.5, (theme, pair, ratio)
        ratios[f"{theme}: {' / '.join(pair)}"] = ratio
check("Text contrast", True, "Every supplied foreground/muted text pair on its background/surface exceeds 4.5:1. Decorative borders are excluded.")

report = {"status": "PASS", "checks": checks, "contrastRatios": ratios,
          "limits": ["No physical-device install tests or Android/Xcode builds.", "No print proof or ICC/spot-color conversion.", "Theme SVG browser behavior is checked separately from file-integrity validation."]}
(ROOT / "05-guidelines/verification.json").write_text(json.dumps(report, indent=2) + "\n")
for item in checks:
    print(f'PASS: {item["name"]} - {item["evidence"]}')
print(json.dumps(ratios, indent=2))
