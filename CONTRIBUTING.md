# Contributing

Edit the canonical `plugin.json`, `mcp.json`, `skills/`, and `assets/`. Run
`python scripts/sync_packages.py` to regenerate `plugins/cashstream/` and
`plugins/claude/`. Keep the `cashstream@cashstream-marketplace` identity stable.

Install `requirements-dev.txt`, then run `python scripts/validate_plugin.py`
and `python scripts/build_plugin.py`. Commit generated changes with their
canonical source. Bump the root manifest version for a distribution change.

Keep proposed skills in `docs/SKILLS_PROPOSES.md` until their scope is chosen.
Use current MCP schemas when writing skill instructions. Do not add financial
records, credentials, service implementation, or server infrastructure here.

Record interactive client and OAuth verification separately from static
packaging checks. Report issues at the repository's GitHub issue tracker.
