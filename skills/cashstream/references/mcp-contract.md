# CashStream MCP contract

This is an object/tool map, not a copy of every input schema. Inspect the live
tools for required fields and defaults. CashStream is reached through OAuth;
`cashstream.read` authorizes reads and `cashstream.write` authorizes mutations,
subject to server-side record ownership.

## Tool map

| Object | Read | Write |
| --- | --- | --- |
| Accounts | `search_accounts` | `create_account`, `update_account`, `archive_account` |
| Transactions and their lines | `search_transactions` | `add_transactions`, `update_transaction`, `archive_transactions` |
| Payees and aliases | `search_payees` | `create_payee`, `update_payee`, `archive_payee` |
| Envelopes and their configuration | `search_envelopes` | `create_envelope`, `update_envelope`, `archive_envelope`, `allocate_to_envelope` |
| Subscriptions | `search_subscriptions` | `create_subscription`, `update_subscription`, `archive_subscription` |
| Bills | `search_bills` | `create_bill`, `update_bill`, `archive_bill` |
| Income plans | `search_income_plans` | `create_income_plan`, `update_income_plan`, `archive_income_plan` |
| Transfer plans | `search_transfer_plans` | `create_transfer_plan`, `update_transfer_plan`, `archive_transfer_plan` |
| Repayment plans | `search_repayment_plans` | `create_repayment_plan`, `update_repayment_plan`, `archive_repayment_plan` |
| Calculated occurrences | `list_flow_occurrences` | Settle through linked transactions, not an occurrence write tool. |

The generic `search_recurring_flows`, `create_recurring_flow`,
`update_recurring_flow`, and `archive_recurring_flow` tools remain compatible.
Prefer the business-specific family when the object type is known; it supplies
that type and money direction.

Sections appear in envelope results and can be referenced with a known
`sectionId`; there is no dedicated section CRUD tool. Envelope movements,
global projections, and the available-to-budget total have no dedicated MCP
read tool. Do not infer that an application page has an equivalent MCP endpoint.

## Search results and coverage

Searches return `{ items, nextCursor }`, with a default page size of 50 and a
maximum `limit` of 200. Continue with the returned cursor and unchanged filters
until coverage is sufficient; do not manufacture cursors or assume one page
means all records. Reads normally exclude archived records.

`search_transactions` accepts `id`, `accountId`, date bounds, payee, counterparty,
envelope, status, recurring-flow, amount, and text filters. It returns split
lines with each parent. Date bounds use `startDate` and `endDate`; the envelope
sentinel `"none"` includes unassigned split lines. Without a status filter,
results can include planned, simulated, and void transactions as well as posted
ones. `includeArchived: true` includes logically deleted transactions.

`search_accounts` supplies the computed account balance. `search_envelopes`
supplies configuration rather than complete envelope balances.

`list_flow_occurrences` takes schedule `id`, optional `from`, and `limit`
(default 50, maximum 100). It has no `nextCursor`, `to`, or `includeSettled`
input in the MCP contract, even though the application's HTTP API has different
options. It returns `items`, `nextOccurrence`, `repayment`, and
`unassignedTransactionCount`. Do not claim an unbounded schedule was fetched.

## Writes and results

- `add_transactions` takes `{ transactions: [...] }`, with 1–500 entries per
  atomic call. Each entry needs `accountId`, `date`, and `amountCents`;
  `status` defaults to `posted`. Currency comes from the account. Optional
  relationships include `payeeId` OR `counterpartyAccountId`, `envelopeId`,
  `lines`, `recurringFlowId`, and `recurringOccurrenceDate`.
- The creation result's `created` array contains one result per submitted
  entry, with source ID, optional mirror ID, and mirror outcome. It is not a
  count of every newly inserted row. Duplicate checks are the importer's job;
  atomic execution is not request idempotency.
- `update_transaction` targets one `id`. An omitted field is preserved;
  accepted nullable fields can be cleared with `null`. Supplying `lines`
  replaces the complete split and recalculates the total.
- `archive_transactions` takes an `ids` array. Other archive tools take `id`.
  Only the selected transaction IDs are archived, including for transfers.
- Supplied payee `aliases` and recurring `subLines` replace their respective
  lists. Preserve existing entries when extending a list.
- A failed tool result can have `isError: true` and structured error details;
  inspect the result rather than treating transport success as a successful
  write. After an uncertain write, read back before retrying.

## Current compatibility notes

- Transaction and transaction-line categories have been removed. Use envelopes
  and line-level envelope links; account `category` remains valid.
- Older generic expenses map to bills unless an explicit business type says
  otherwise. A repeated merchant label does not establish a subscription.
- Payee websites are shared identity. Schedule `website` is not a write field;
  bank website overrides apply only to custom/Other banks.
- The import is analyzed in the agent conversation and written through MCP.
  There is no import-session, file-upload, auto-bank-sync, or mark-paid MCP tool.
