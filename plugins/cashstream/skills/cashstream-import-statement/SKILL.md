---
name: cashstream-import-statement
description: Analyze bank statement files in the agent conversation and add the decided transactions directly to CashStream through MCP.
---

# CashStream Statement Import

Use this skill when the user provides or references a bank statement, CSV export, PDF statement, screenshot, or raw transaction list and wants it added to CashStream.

## Core Rule

Do not create an import session. Do not emulate the old CashStream import workflow. The agent analyzes the statement, explains decisions in the chat, then calls `add_transactions` directly.

## Workflow

1. Identify the target CashStream account.
   - Use `search_accounts`.
   - If the account is ambiguous, ask a concise question before writing.
2. Parse the statement.
   - Extract date, label/payee, memo/description, amount, currency when visible, and source row/page if useful for explanation.
   - Convert amounts to integer cents.
   - Keep signs consistent with CashStream: expenses negative, income positive.
3. Read context.
   - Use `search_transactions` for the statement date range and account to detect likely duplicates.
   - Use `search_payees` to match existing payees and aliases.
   - Use `search_envelopes` and `search_recurring_flows` only when needed for categorization, envelopes, or recurring links.
4. Decide in the conversation.
   - Present assumptions, duplicate handling, payee matches, categories, envelopes, and recurring-flow decisions.
   - Keep the summary compact but concrete enough for review.
5. Write directly.
   - Use `add_transactions` for the batch the agent has decided.
   - Use `update_transaction` afterwards only if a recurring-flow link must be applied after creation.

## Duplicate Handling

- Prefer skipping likely duplicates rather than adding uncertain rows.
- A strong duplicate usually shares account, date, amount, and a close payee/memo match.
- If duplicates are ambiguous, explain the ambiguity and ask the user before writing those rows.

## Payees And Aliases

- Prefer existing payees when the statement label clearly maps to one.
- If a recurring merchant appears with a noisy bank label, propose updating the payee aliases with `update_payee`.
- Do not create payees automatically unless it improves future matching and the label is stable enough.

## Output Shape

Before the write, include:

- Number of rows parsed.
- Number planned for creation.
- Number skipped as duplicates.
- Any ambiguous rows requiring user confirmation.

After the write, include:

- Created transaction IDs.
- Skipped duplicates.
- Follow-up checks performed or recommended.
