# CashStream plugin

**The precision of a spreadsheet, without the friction.**

Connect your agent to [CashStream](https://cashstream.quentin-berger.fr) to manage
accounts, transactions, recurring flows, and budget envelopes.

Version `0.2.3` includes a portable Agent Plugins package, a Codex package, and a
Claude Code package. Both client packages are generated from the same canonical
skills. Their MCP endpoint is `https://cashstream.quentin-berger.fr/mcp`.

## Included skills

- **[`cashstream`](skills/cashstream/SKILL.md)** is reference documentation:
  accounts, payees, transactions and split lines, envelopes, recurring business
  objects, occurrences, and their relationships. Its
  [data model](skills/cashstream/references/data-model.md) and
  [MCP contract](skills/cashstream/references/mcp-contract.md) explain balances,
  statuses, transfers, partial payments, and tool capabilities. Loading it does
  not start a workflow or change records.
- **[`cashstream-import-statement`](skills/cashstream-import-statement/SKILL.md)**
  imports transactions from statements, CSV/PDF files, screenshots, pasted
  lists, or messages. It matches existing records, reconciles settled planned
  entries, checks duplicates, assigns split envelopes, and links known payments
  to scheduled occurrences before writing the decided changes through MCP.
  When identification, values, matches, or requested assignments are uncertain,
  it asks the user and waits before the affected writes. Newly inferred recurring
  flows are proposed with their schedule and require the user's decision.

The package intentionally has two skills: the shared documentation and the
transaction-import workflow. Both use the same object model and live MCP tools.

## Authentication and permissions

The service uses OAuth Authorization Code with PKCE S256 and dynamic client
registration. The client opens CashStream for sign-in and consent, then uses
the issued tokens for MCP requests. No API key or secret belongs in this package.

- `cashstream.read` reads the connected user's accounts, transactions, payees,
  envelopes, and recurring schedules.
- `cashstream.write` creates, changes, and archives those records and allocates
  money to envelopes, within the connected user's server-side permissions.

The native packages request both scopes for their included read/write workflows.
For a ChatGPT connection intended only for analysis, request `cashstream.read`
alone. The service enforces authorization independently of editable skills.

CashStream does not offer automatic bank synchronization at launch. Imports
require supplied records, and reviews depend on how current the account data is.

## Install in Codex

```bash
codex plugin marketplace add cashstreamhq/cashstream-plugin
codex plugin add cashstream@cashstream-marketplace
```

Start a new session and complete OAuth when prompted. The marketplace name and
the `plugins/cashstream` package path are preserved from the original `0.1.0`
package so existing installations keep the same identity.

The repository was transferred from `Quentin-BRG/cashstream-plugin` to
`cashstreamhq/cashstream-plugin`. GitHub redirects the former clone URL; existing
installations retain `cashstream@cashstream-marketplace`, the package paths,
the public MCP endpoint, and the same OAuth scopes. New installations should use
the organization URL above.

To update the marketplace:

```bash
codex plugin marketplace upgrade cashstream-marketplace
```

Then refresh or reinstall CashStream from that marketplace in your client.

## Connect in ChatGPT

The MCP endpoint can be connected as a custom ChatGPT plugin, subject to account
and workspace policies:

1. Open **Plugins**, select **+**, then **Add custom MCP server**.
2. Enter `https://cashstream.quentin-berger.fr/mcp`.
3. Select **OAuth** and **Dynamic Client Registration** when registration options
   are offered. The service publishes its endpoints through discovery.
4. Complete the linking flow, review the discovered tools, and test the connection.

This repository does not contain a registered ChatGPT connection ID. Publishing
the GitHub repository does not register or list a plugin in the ChatGPT directory.
Use the portable package for supported package-import/submission workflows and
follow OpenAI's [connection guide](https://developers.openai.com/plugins/deploy/connect-chatgpt)
and [packaging guide](https://developers.openai.com/plugins/build/plugins).

The portable `mcp.json` stays within the Agent Plugins 1.0.0 schema; OAuth is
discovered from the service. No static bearer token is embedded in a manifest.

## Claude Code preview

The Claude Code package follows the layout used by
[synapse-plugin](https://github.com/Quentin-BRG/synapse-plugin):

```bash
claude plugin marketplace add cashstreamhq/cashstream-plugin
claude plugin install cashstream@cashstream-marketplace
```

Start a new session or reload plugins, then complete OAuth through `/mcp` if
prompted. Static package validation does not establish interactive client or
OAuth compatibility; the Claude package is a preview until that flow is tested.

## Repository layout

```text
plugin.json                         Portable Agent Plugins manifest
mcp.json                            Portable MCP configuration
skills/cashstream/                   Documentation skill and shared references
skills/cashstream-import-statement/  Transaction-import skill
assets/                             CashStream icon
plugins/cashstream/                  Generated Codex compatibility package
plugins/claude/                      Generated Claude Code compatibility package
.agents/plugins/marketplace.json     Codex repository marketplace
.claude-plugin/marketplace.json      Claude Code repository marketplace
scripts/                            Sync, validation, and ZIP packaging
```

The portable source of truth and generated compatibility packages follow the
approach used by [weave-plugin](https://github.com/Quentin-BRG/weave-plugin).

## Develop and validate

Python 3.10 or newer is sufficient. Validation uses JSON Schema and YAML:

```bash
python -m pip install -r requirements-dev.txt
python scripts/sync_packages.py
python scripts/sync_packages.py --check
python scripts/validate_plugin.py
python scripts/build_plugin.py
```

Builds create `dist/cashstream-portable-0.2.3.zip`,
`dist/cashstream-codex-0.2.3.zip`, and `dist/cashstream-claude-0.2.3.zip`.
CI validates schema conformance, skill metadata, package paths, OAuth scope
consistency, and generated-file parity. It also builds the three archives.
Actual login, token refresh, and financial writes require separate end-to-end
validation against the service; a green packaging check does not claim those pass.

## Repository boundary and license

This public repository contains plugin manifests, skills, packaging scripts,
catalogs, and documentation. The CashStream service, application source,
database, financial records, and infrastructure are outside this distribution.

Copyright 2026 Quentin Berger. Licensed under [Apache License 2.0](LICENSE).
This license applies to the plugin distribution, not the CashStream service.
