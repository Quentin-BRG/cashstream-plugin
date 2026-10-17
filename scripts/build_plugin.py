#!/usr/bin/env python3
"""Build deterministic portable, Codex, and Claude plugin ZIP archives."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from sync_packages import PACKAGES, ROOT, differences


def build(output: Path) -> None:
    stale = [line for client in PACKAGES for line in differences(ROOT, client)]
    if stale:
        raise ValueError("Packages are out of sync; run scripts/sync_packages.py first")
    version = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))["version"]
    portable = [ROOT / name for name in (
        "plugin.json", "mcp.json", "LICENSE", "README.md",
        ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"
    )]
    # Root extension paths and README links must also resolve inside the ZIP.
    portable += [p for directory in ("skills", "assets", "plugins", "docs") for p in (ROOT / directory).rglob("*") if p.is_file()]
    layouts = {"portable": (ROOT, portable)}
    for client, directory in PACKAGES.items():
        base = ROOT / directory
        layouts[client] = (base, [p for p in base.rglob("*") if p.is_file()])
    output.mkdir(parents=True, exist_ok=True)
    for client, (base, files) in layouts.items():
        target = output / f"cashstream-{client}-{version}.zip"
        with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
            for path in sorted(files):
                info = ZipInfo(path.relative_to(base).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = ZIP_DEFLATED
                archive.writestr(info, path.read_bytes())
        print(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    build(args.output)
