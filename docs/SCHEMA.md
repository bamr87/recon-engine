---
schema: '0.1'
coverage: listed
---

# SCHEMA — docs

> The documents of record beside SPEC.md: the docs index, the constitution, its amendment log and the decision records.

## Conventions

- Every document opens with a one-line summary; `README.md` indexes them from those lines.
- Records are append-only: numbers are never reused and a ratified or accepted record is corrected by a new one.

## Structure

| entry | kind | purpose | rules |
| --- | --- | --- | --- |
| `README.md` | file | the docs index, generated between its `AUTO:docs-index` markers | required |
| `constitution.md` | file | the rules every change must satisfy; changes only by amendment | required |
| `amendments/` | dir | the amendment log: `README.md` index, `0000-template.md`, `NNNN-slug.md` records | terminal |
| `adr/` | dir | architecture decision records: `README.md` index, `0000-template.md`, `NNNN-slug.md` records | terminal |

## Placement

- A change to the constitution → `amendments/NNNN-slug.md`, next free number, with the edit it describes
- A decision that is hard to reverse → `adr/NNNN-slug.md`, next free number
- Anything unrouted → propose an entry in this table first, then create it.

## Forbidden

- Editing a ratified amendment or an accepted ADR instead of superseding it.
- Design that belongs in `SPEC.md`.
