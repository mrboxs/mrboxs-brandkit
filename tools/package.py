#!/usr/bin/env python3
"""Refresh inventory/checksums and package the verified kit, excluding local tools' caches."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
paths = [p for p in sorted(ROOT.rglob("*")) if p.is_file() and not set(p.relative_to(ROOT).parts).intersection({".git", ".venv", "__pycache__", ".DS_Store"})]
inventory_paths = [p for p in paths if p.name not in ("asset-inventory.json", "SHA256SUMS.txt")]
(ROOT / "asset-inventory.json").write_text(json.dumps({"brand": "mrboxs", "version": "1.0.0", "assets": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size} for p in inventory_paths]}, indent=2) + "\n")
paths = sorted(set(paths + [ROOT / "asset-inventory.json"]))
(ROOT / "SHA256SUMS.txt").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n" for p in paths if p.name != "SHA256SUMS.txt"))
archive = ROOT.parent / "mrboxs-brandkit.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(set(paths + [ROOT / "SHA256SUMS.txt"])):
        z.write(p, str(p.relative_to(ROOT.parent)))
print(f"Packaged {len(paths)} files: {archive} ({archive.stat().st_size:,} bytes)")
