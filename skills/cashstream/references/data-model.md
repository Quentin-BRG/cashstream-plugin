# CashStream data model

This reference describes the MCP-facing model as reviewed on 2026-10-17. Read
the live tool schema for exact required fields. Identifiers are opaque IDs;
names, merchant labels, websites, and dates are not interchangeable IDs.

## Accounts and balances

An account has a name, currency, account `category`, and `openingBalanceCents`.
Categories include `CURRENT`, `SAVINGS`, `INVESTMENT`, `LOAN`, `CREDIT_CARD`,
`WALLET`, and `OTHER`. These account types still exist; transaction categories
have been removed.

`search_accounts` returns `currentBalanceCents`: opening balance plus the signed
sum of non-deleted `posted` transactions. `includeSimulation: true` also includes
`simulation` transactions. `planned` and `void` entries do not contribute to
that account balance. The balance is not a remaining-to-spend budget.

`openingDate` describes the baseline; it does not automatically exclude earlier
transactions from the sum. Importing history already included in the opening
balance can double-count it. Establish the covered period and baseline rather
than changing an opening balance merely to force a match.

For a catalog bank, use `bankId` with `isCustomBank: false`; its official website
comes from the catalog. For an Other/custom bank, use `isCustomBank: true` without
a catalog `bankId`; its website may be supplied or cleared. Do not override a
catalog bank's website. Amounts on a transaction use its account's currency;
there is no transaction-level currency field in `add_transactions`.

## Payees and identity

A payee is an external party, with kind `merchant`, `service`, `employer`,
`person`, or `other`. One payee can be shared by many transactions and schedules.
Aliases map noisy statement labels to that same party. Passing `aliases` to
`update_payee` replaces the whole list; omitting it preserves the list.

The payee owns `website`. HTTP(S) websites are normalized to their origin and
the UI uses the domain's favicon, with a fallback icon when unavailable. Update
identity with `create_payee` or `update_payee`; a schedule references the payee
through `payeeId` and does not own a second website. A statement label alone
does not justify inventing a website or merging two uncertain parties.

## Transactions and split lines

Each transaction belongs to one `accountId`, with a `date`, signed `amountCents`,
optional `memo`, and one status:

| Status | Meaning for accounts and scheduled payment progress |
| --- | --- |
| `posted` | Booked movement; contributes to the account balance and can settle a linked occurrence. |
| `planned` | Expected movement recorded explicitly; not yet part of actual account balance or settled progress. |
| `simulation` | A hypothetical movement; included only where a view explicitly opts into simulation. |
| `void` | A void entry; excluded from actual account balance and settlement. |

Expenses are negative, income positive. A transaction can have either a
`payeeId` or `counterpartyAccountId`, never both. A counterparty must be a
different owned account. A transaction can separately reference an envelope
and a recurring occurrence; those links represent different relationships.

A simple transaction uses parent `envelopeId`. A split transaction uses a
complete `lines` array, each with its own signed amount, memo, and optional
envelope. The sum of line amounts determines the parent total; the parent
envelope is cleared. Include every line, including amounts that remain
unassigned, and reconcile the sum to the source total before writing.

`search_transactions` returns the parent and its lines. When updating a split,
send the complete intended lines array to replace it. Assigning only a parent
envelope to an existing split is rejected. An empty replacement array is not a
safe shorthand for preserving the transaction total or assignments.

Filtering by `envelopeId` includes a split when one of its lines matches.
`envelopeId: "none"` finds unassigned simple transactions or splits containing
an unassigned line; a split parent with `envelopeId: null` is not by itself
evidence that all its lines are unassigned. For per-envelope totals, use the
matching line amounts rather than counting the entire parent in each envelope.

## Transfers between owned accounts

Create a transfer once, for example a debit on account A with account B as
`counterpartyAccountId`. The service inserts the requested row and manages the
opposite amount on B. A transfer is not external income or expenditure when
reporting across both accounts.

Each creation result includes `transactionId`, `mirroredTransactionId`, and
`mirrorOutcome`: `created`, `skipped_existing`, `skipped_ambiguous`, or
`not_requested`. A matching counterpart can be reused, or an ambiguous match
can prevent automatic mirror creation. Inspect the result; do not claim two
new rows were created from one returned source ID.

This is creation-time behavior, not a permanent paired-edit contract.
`update_transaction` edits the selected row; `archive_transactions` affects
only the supplied IDs. For a requested change to the whole transfer, identify
and verify both sides. Do not assume a stable transfer-pair ID or propagation.

When importing both account statements, match the counter-entry before adding
another transaction. Differing statement dates or labels can defeat the
server's strict mirror matching. Do not invent foreign-exchange amounts: the
mirroring contract uses equal and opposite cents, not an exchange-rate model.

## Envelopes, sections, and allocations

Envelopes group money by purpose independently of accounts. An optional
`sectionId` groups envelopes for presentation; it is not an account or a payee.

| Envelope type | Configuration | Meaning |
| --- | --- | --- |
| `spending` | `periodicity` (`monthly` or `weekly`), `periodAnchorDate`, `budgetPerPeriodCents` | A spending budget for an anchored period. |
| `saving`, `mode: "byDate"` | `targetAmountCents`, `dueDate` | An amount to build toward a date. Supply the intended target and date. |
| `saving`, `mode: "topUp"` | `capAmountCents` | A reserve to replenish toward a cap. |

The service records envelope movements when transactions or split lines are
assigned. A spending assignment uses a `spending` movement; saving movements
distinguish contributions and withdrawals. These movements describe budget
effects and must not be imported as a second set of bank transactions.

`allocate_to_envelope` creates an allocation without a bank transaction.
For a spending envelope it also adjusts `budgetPerPeriodCents` by the supplied
signed amount. Positive allocations are checked against the service's
available-to-budget value unless `allowOverallocate` is requested; zero is
rejected. Do not use allocation as a read operation or treat changing the
configured budget as proof that money moved between accounts.

`search_envelopes` exposes configuration, sections, and identity. It does not
return a complete movement ledger or a calculated available/spent/saved balance.
The MCP currently has no dedicated read tool for the global available-to-budget
amount. Do not invent those fields or derive them solely from account totals.

## Recurring business objects and calendars

The five business objects use the same underlying schedule model and IDs:

| Object / page | `businessType` | `kind` | Purpose |
| --- | --- | --- | --- |
| Subscription / Abonnements | `subscription` | `expense` | A continuing subscription commitment. |
| Bill / Charges | `bill` | `expense` | A charge or bill; may use `estimated: true`. |
| Income plan / Revenus | `income` | `income` | Expected salary or another recurring income. |
| Transfer plan / Virements | `transfer` | `transfer` | Expected transfer from `accountId` to `destinationAccountId`. |
| Repayment plan / Crédits & échéanciers | `repayment` | `expense` | A finite sequence of equal loan or installment payments. |

`name` identifies the object; `description` adds context. `amountCents` is a
positive nominal amount, while `kind` sets its direction. An ordinary schedule
can reference an account, payee, and envelope; `subLines` can split expected
amounts by envelope. Transfer plans use two accounts and do not use payees,
envelopes, or sub-lines. A repayment cannot use sub-lines.

Supported frequencies are `daily`, `weekly`, `monthly`, `yearly`, and `irregular`.
Weekly schedules require `dayOfWeek` (0 is Sunday); monthly schedules require
`dayOfMonth`; yearly schedules require both `dayOfMonth` and `monthOfYear`.
Month-end rules clamp to the month's last day, and 29 February resolves to
28 February in a non-leap year. Follow returned occurrence dates rather than
reconstructing a different calendar from the statement's booking date.

A repayment needs a first installment `startDate`, a finite `installmentCount`,
and `financingType` (`loan` or `installment`). Its total is the nominal amount
times the count. It is not an amortization table separating principal and
interest, and it is distinct from an account whose category is `LOAN`.

States are `active`, `paused`, and `ended`. Pausing or ending stops active
projections while retaining recorded payments. A schedule never generates
transactions automatically. A repeated merchant in a statement is not, by
itself, permission to create a subscription or change a calendar. During import,
propose the concrete new flow and clarify its schedule with the user before
creating it, unless that same flow was already explicitly authorized. A general
transaction import does not authorize new future schedules.

## Occurrences, settlements, and progress

An occurrence is a calculated date and expected amount, not a separate bank
entry. Link a payment with both `recurringFlowId` and `recurringOccurrenceDate`.
The occurrence date must belong to the calendar; the transaction's `date` is
when the movement was booked and can be different. The linked currency must
match. A transfer payment must belong to the plan's account route.

Several posted transactions can settle the same occurrence in parts. Refunds
reduce its paid amount. For a transfer plan, only the source-account debit
counts, even when both mirrored rows carry the occurrence link.

`list_flow_occurrences` returns expected, paid, remaining, and overdue amounts,
as well as repayment progress when applicable. These totals are calculated;
there is no editable paid/progress field. The occurrence's projected
`amountCents` can represent its remaining signed amount rather than the original
face amount; use the named expected/paid/remaining fields for those concepts.

Passing a date never marks it paid. Finite repayments keep the earliest unpaid
installment as next, including overdue ones. Open-ended services follow the
current period and subsequent occurrences; an old unmatched occurrence does
not indefinitely pin the next payment. Legacy links without an occurrence date
only match when the transaction date exactly belongs to the calendar;
`unassignedTransactionCount` flags amounts needing a better link.

In the application's timeline, a linked `planned` transaction reserves its
amount to avoid counting it again in the remaining projection, while not
settling the occurrence. Do not add planned reservations to actual paid totals
or assume the occurrence tool's posted-payment summary includes reservations.

## Relationship examples

- A posted grocery debit of `-7500` on account A can reference a supermarket
  payee and a spending envelope. If split into `-5000` groceries and `-2500`
  household supplies, there is still one bank debit, with two envelope lines.
- A bill due on 5 October can have payments of `-4000` on 8 October and `-6000`
  on 10 October, both linked to occurrence `2026-10-05`. Against an expected
  `10000`, that occurrence is settled once by two actual movements.
- A transfer of `-20000` from A to B has a `+20000` counter-entry on B. It changes
  each account balance while keeping their combined balance unchanged.

Archiving is a logical removal, not a hard delete. Existing object IDs and
recorded history should be preserved when changing a label or schedule.
