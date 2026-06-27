# CashStream Codex Marketplace

This repository is a small local Codex marketplace that exposes the CashStream plugin.

## Install

Register the marketplace once:

```powershell
codex plugin marketplace add C:\Users\Quentin\Documents\cashstream\cashstream-codex-plugin
```

Then install the plugin:

```powershell
codex plugin add cashstream@cashstream-marketplace
```

Start a new Codex thread after installation so the CashStream skills and MCP tools are loaded.

## MCP Endpoint

The plugin connects to the production CashStream MCP endpoint:

```text
https://cashstream.quentin-berger.fr/mcp
```

The MCP server uses OAuth. Codex should discover the authorization metadata from the CashStream app and ask the user to authorize access.

## Included Skills

- `cashstream`: general CashStream read/write workflow.
- `cashstream-import-statement`: analyze a bank statement in the agent conversation and write transactions directly to CashStream.

## Contract

The plugin intentionally does not create or use a CashStream import session. The agent explains decisions in the chat, then writes the chosen batch through `add_transactions`.
