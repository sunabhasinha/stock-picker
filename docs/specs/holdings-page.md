# Spec: Holdings page
status: proposed

Goal: users add/edit/remove held positions in the web UI; the scan consumes
them exactly as the positions JSON does today.

Acceptance:
- Add position: symbol + average cost (required), open trades optional
- Positions persist across server restarts
- Running a scan uses current holdings automatically; the Section 6.3
  reconciliation section renders for every holding
- Existing positions-JSON textarea keeps working (back-compat)

Invariants (inherited apply; feature-specific):
- This page manages RECORDS only — nothing executes trades
- Stdlib-only, no framework/build step, localhost-only (AGENTS.md #5/#6)
- Money displayed to 2 decimals; stored as floats like the rest of the code

Out of scope: broker import, P&L analytics, multi-portfolio support

Deliberately left to the implementer: storage file location/name, form layout
NOT left open: persistence must be a plain local file a user can inspect and
back up (i.e. the existing positions-JSON format is the natural choice —
`scan.positions_from_dict` is the established contract)
