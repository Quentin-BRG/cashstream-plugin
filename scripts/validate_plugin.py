#!/usr/bin/env python3
"""Validate schemas, skill metadata, client packages, and repository catalogs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import jsonschema
import yaml

from sync_packages import PACKAGES, ROOT, SCOPES, differences


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def contained(root: Path, relative: str) -> Path:
    if not relative.startswith("./") or ".." in Path(relative).parts:
        raise ValueError(f"invalid package-relative path: {relative}")
    path = (root / relative).resolve()
    if root.resolve() not in path.parents or not path.exists():
        raise ValueError(f"missing or escaping package path: {relative}")
    return path


def validate() -> list[str]:
    errors = []
    for filename, schema in (("plugin.json", "plugin.schema.json"), ("mcp.json", "mcp.schema.json")):
        try:
            jsonschema.Draft202012Validator(read_json(ROOT / "scripts/schemas" / schema)).validate(read_json(ROOT / filename))
        except (ValueError, jsonschema.ValidationError) as exc:
            errors.append(f"{filename}: {exc}")
    if errors:
        return errors

    manifest = read_json(ROOT / "plugin.json")
    for extension in manifest.get("extensions", {}).values():
        for field in ("packageDirectory", "marketplace"):
            if field in extension:
                contained(ROOT, extension[field])
    resource = read_json(ROOT / "mcp.json")["mcpServers"]["cashstream"]
    url = urlsplit(resource["url"])
    if url.scheme != "https" or url.username or url.password or url.fragment or url.query or not url.path.endswith("/mcp"):
        errors.append("MCP endpoint must be an HTTPS /mcp URL without credentials, query, or fragment")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", manifest["version"]):
        errors.append("plugin version must follow semantic versioning")

    skills = list((ROOT / "skills").glob("*/SKILL.md"))
    if {path.parent.name for path in skills} != {"cashstream", "cashstream-import-statement"}:
        errors.append("keep the CashStream documentation and transaction-import skills as the two entry points")
    # The import workflow shares the documentation skill's model. References
    # may cross skill folders but must resolve within the distributed package.
    for path in [ROOT / "README.md", *(ROOT / "skills").rglob("*.md")]:
        for link in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if ROOT.resolve() not in target.parents or not target.is_file():
                errors.append(f"{path.relative_to(ROOT)}: missing or escaping reference {link}")
    for path in skills:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n(.+)\Z", text, re.S)
        if not match:
            errors.append(f"{path.relative_to(ROOT)}: missing frontmatter or body")
            continue
        metadata = yaml.safe_load(match[1])
        if not isinstance(metadata, dict) or metadata.get("name") != path.parent.name:
            errors.append(f"{path.relative_to(ROOT)}: name must match skill folder")
            continue
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"]) or len(metadata["name"]) > 64:
            errors.append(f"{path.relative_to(ROOT)}: invalid skill name")
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(f"{path.relative_to(ROOT)}: invalid description")
        ui = yaml.safe_load((path.parent / "agents/openai.yaml").read_text(encoding="utf-8"))["interface"]
        if not 25 <= len(ui["short_description"]) <= 64 or f'${metadata["name"]}' not in ui["default_prompt"]:
            errors.append(f"{path.relative_to(ROOT)}: invalid UI description or skill invocation")

    for client, directory in PACKAGES.items():
        errors.extend(differences(ROOT, client))
        package = ROOT / directory
        filename = ".codex-plugin/plugin.json" if client == "codex" else ".claude-plugin/plugin.json"
        client_manifest = read_json(package / filename)
        if client_manifest["name"] != manifest["name"] or client_manifest["version"] != manifest["version"]:
            errors.append(f"{client}: inconsistent plugin identity")
        for key in ("skills", "mcpServers"):
            contained(package, client_manifest[key])
        server = read_json(package / ".mcp.json")["mcpServers"]["cashstream"]
        if server["type"] != "http" or server["url"] != resource["url"]:
            errors.append(f"{client}: inconsistent MCP endpoint")
        scopes = server["scopes"] if client == "codex" else server["oauth"]["scopes"].split()
        if scopes != SCOPES:
            errors.append(f"{client}: inconsistent OAuth scopes")
        if client == "codex":
            for key in ("composerIcon", "logo"):
                contained(package, client_manifest["interface"][key])

    codex_catalog = read_json(ROOT / ".agents/plugins/marketplace.json")
    claude_catalog = read_json(ROOT / ".claude-plugin/marketplace.json")
    for catalog in (codex_catalog, claude_catalog):
        if catalog["name"] != "cashstream-marketplace" or len(catalog["plugins"]) != 1 or catalog["plugins"][0]["name"] != manifest["name"]:
            errors.append("marketplace must preserve cashstream@cashstream-marketplace")
    codex_entry = codex_catalog["plugins"][0]
    if contained(ROOT, codex_entry["source"]["path"]) != ROOT / PACKAGES["codex"]:
        errors.append("Codex marketplace points to the wrong package")
    if codex_entry["policy"] != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
        errors.append("Codex marketplace must retain installation and authentication policies")
    if contained(ROOT, claude_catalog["plugins"][0]["source"]) != ROOT / PACKAGES["claude"]:
        errors.append("Claude marketplace points to the wrong package")
    return errors


if __name__ == "__main__":
    try:
        problems = validate()
    except (KeyError, ValueError, OSError, TypeError, yaml.YAMLError) as exc:
        problems = [str(exc)]
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("Validated portable schemas, skill metadata, client packages, OAuth scopes, and marketplaces.")
