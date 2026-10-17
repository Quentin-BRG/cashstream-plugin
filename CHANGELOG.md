# Changelog

## 0.2.2 — 2026-10-17

- Require user clarification before writes affected by uncertain transaction
  identities, values, duplicate matches, transfers, or requested assignments.
- Group actionable questions, preserve prior answers, and wait for real replies;
  unresolved rows cannot be silently skipped or stripped of uncertain links.
- Propose inferred recurring flows with their concrete schedule and wait for
  explicit authorization before creation, while preserving prior authorization.
- Keep clear, already authorized imports free of redundant global confirmations.

## 0.2.1 — 2026-10-17

- Keep two skills: CashStream reference documentation and transaction import.
- Explain objects, relationships, statuses, balances, split envelopes, business
  schedules, occurrences, partial payments, and transfer mirror behavior.
- Document current MCP tools and limits, removal of transaction categories,
  and shared payee and bank identity rules.
- Extend import guidance to pasted lists and messages, opening-balance overlap,
  planned-entry reconciliation, split totals, and mirror outcomes.
- Remove the proposed extra-skill roadmap and align plugin presentation with
  the two-skill scope.

## 0.2.0 — 2026-10-17

- Add a canonical Agent Plugins 1.0.0 package and generated Codex/Claude packages.
- Preserve the original Codex marketplace identity and package path.
- Update the existing skills for business flows, occurrences, envelopes,
  mirrored transfers, complete duplicate searches, and uncertain write results.
- Add CashStream branding, public installation instructions, an Apache-2.0
  plugin license, schema validation, package parity checks, and ZIP builds.
- Document six proposed skills without activating additional workflows.

## 0.1.0 — 2026-06-27

- Initial private Codex marketplace with general CashStream and statement-import
  skills and an OAuth-protected MCP connection.
