#!/usr/bin/env python3
"""Generate client packages from the portable source; --check changes nothing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = {"codex": "plugins/cashstream", "claude": "plugins/claude"}
SCOPES = ["cashstream.read", "cashstream.write"]


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def package_files(root: Path, client: str) -> dict[str, bytes]:
    portable = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    endpoint = json.loads((root / "mcp.json").read_text(encoding="utf-8"))["mcpServers"]["cashstream"]["url"]
    manifest = {key: portable[key] for key in (
        "name", "version", "description", "author", "homepage", "repository", "license", "keywords"
    )}
    manifest.update({"skills": "./skills/", "mcpServers": "./.mcp.json"})
    server = {"type": "http", "url": endpoint}
    if client == "codex":
        manifest["interface"] = {
            "displayName": "CashStream",
            "shortDescription": "The precision of a spreadsheet, without the friction.",
            "longDescription": portable["description"],
            "developerName": "Quentin-BRG",
            "category": "Productivity",
            "capabilities": ["Read", "Write"],
            "websiteURL": portable["homepage"],
            "brandColor": "#0C7C4F",
            "composerIcon": "./assets/logo.png",
            "logo": "./assets/logo.png",
            "defaultPrompt": [
                "Explain how CashStream accounts, envelopes, and transactions relate.",
                "How do scheduled occurrences and actual payments work in CashStream?",
                "Import these transactions into my CashStream account."
            ]
        }
        server.update({"oauth_resource": endpoint, "scopes": SCOPES})
        manifest_name = ".codex-plugin/plugin.json"
    else:
        server["oauth"] = {"scopes": " ".join(SCOPES)}
        manifest_name = ".claude-plugin/plugin.json"

    files = {
        manifest_name: json_bytes(manifest),
        ".mcp.json": json_bytes({"mcpServers": {"cashstream": server}}),
        "LICENSE": (root / "LICENSE").read_bytes(),
    }
    for directory in ("skills", "assets"):
        for path in sorted((root / directory).rglob("*")):
            if path.is_file():
                files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def differences(root: Path, client: str) -> list[str]:
    target = root / PACKAGES[client]
    expected = package_files(root, client)
    actual = {p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file()}
    result = [f"stale: {PACKAGES[client]}/{name}" for name in sorted(actual - expected.keys())]
    for name, content in expected.items():
        path = target / name
        if not path.is_file() or path.read_bytes() != content:
            result.append(f"out of date: {PACKAGES[client]}/{name}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = []
    for client, directory in PACKAGES.items():
        changed.extend(differences(ROOT, client))
        if not args.check:
            target = ROOT / directory
            expected = package_files(ROOT, client)
            for path in target.rglob("*"):
                if path.is_file() and path.relative_to(target).as_posix() not in expected:
                    path.unlink()
            for name, content in expected.items():
                path = target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    if args.check and changed:
        print("\n".join(changed))
        print("Run: python scripts/sync_packages.py")
        return 1
    print("Client packages are in sync." if args.check else "Generated Codex and Claude packages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
