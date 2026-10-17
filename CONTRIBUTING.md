# Contributing

Edit the canonical `plugin.json`, `mcp.json`, `skills/`, and `assets/`. Run
`python scripts/sync_packages.py` to regenerate `plugins/cashstream/` and
`plugins/claude/`. Keep the `cashstream@cashstream-marketplace` identity stable.

Install `requirements-dev.txt`, then run `python scripts/validate_plugin.py`
and `python scripts/build_plugin.py`. Commit generated changes with their
canonical source. Bump the root manifest version for a distribution change.

Keep the documentation skill and transaction-import skill as the two entry
points. Document object semantics in the shared model and MCP references, and
use current MCP schemas when updating them. Do not add financial
records, credentials, service implementation, or server infrastructure here.

Record interactive client and OAuth verification separately from static
packaging checks. Report issues at the repository's GitHub issue tracker.
