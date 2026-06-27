---
name: cashstream
description: Use CashStream through its MCP connector to read and update accounts, transactions, payees, envelopes, and recurring flows.
---

# CashStream

Use this skill when the user asks about their CashStream data or wants an agent to update CashStream.

## Operating Model

- CashStream is the system of record. Read current data through the MCP tools before making assumptions.
- Do not use or mention a CashStream import session. The agent reasons in the conversation, then writes directly through MCP.
- Prefer search tools over direct object lookups. CashStream intentionally exposes `search_transactions`, not `get_transaction` or `list_transactions`.
- Use pagination whenever a search can return many rows. Continue with `nextCursor` until you have enough evidence.
- Preserve user intent and explain material assumptions before writes, especially when creating transactions or changing recurring flows.

## Tool Surface

Read tools:

- `search_transactions`
- `search_accounts`
- `search_payees`
- `search_envelopes`
- `search_recurring_flows`

Write tools:

- `add_transactions`
- `update_transaction`
- `archive_transactions`
- `create_account`, `update_account`, `archive_account`
- `create_payee`, `update_payee`, `archive_payee`
- `create_envelope`, `update_envelope`, `archive_envelope`, `allocate_to_envelope`
- `create_recurring_flow`, `update_recurring_flow`, `archive_recurring_flow`

## Conventions

- Amounts are integer cents.
- Expense transactions are negative amounts; income transactions are positive amounts.
- Dates use `YYYY-MM-DD`.
- Use `update_payee` to replace aliases when aliases need to be added, edited, or removed.
- Use `update_transaction` to link or unlink a transaction to a recurring flow.
- Use archive tools for removals; do not expect hard delete tools.
- If the user asks for "all" rows, use the matching search tool with no filters and paginate.

## Write Discipline

Before a write:

1. Search the relevant existing data.
2. Identify likely duplicates or conflicts.
3. State the decision you are about to apply.
4. Call the write tool with only the chosen, already-decided payload.

After a write:

1. Summarize created or updated IDs.
2. Mention skipped or ambiguous items.
3. Suggest the next useful verification search when appropriate.
