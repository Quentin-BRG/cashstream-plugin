# CashStream plugin

- Read `README.md` before changing packaging. `plugin.json`, `mcp.json`,
  `skills/`, and `assets/` are canonical. `plugins/cashstream/` and
  `plugins/claude/` are generated with `python scripts/sync_packages.py`.
- Preserve the installed identity `cashstream@cashstream-marketplace`.
- Keep the plugin separate from the CashStream application. Never copy
  application source, real financial records, credentials, or OAuth tokens here.
- Match skill guidance to the actual MCP tool schemas. Amounts are integer
  cents; transactions use envelopes, not categories. Schedules and payments
  are separate; transfers create a mirrored transaction on the server.
- `docs/SKILLS_PROPOSES.md` contains proposals, not implemented skills.
- After changes, run `python scripts/sync_packages.py --check` and
  `python scripts/validate_plugin.py`. Run `python scripts/build_plugin.py`
  when changing packaging. Do not claim interactive client or OAuth testing
  from static validation alone.
