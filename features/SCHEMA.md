---
schema: '0.1'
coverage: listed
---

# SCHEMA — features

> The feature catalog: one entry per step of the build order, with its status and the SPEC.md sections it serves.

## Structure

| entry | kind | purpose | rules |
| --- | --- | --- | --- |
| `features.yml` | file | the catalog (schema features/v1, ids `RECON-NNN`) | required |

## Placement

- A new capability → a new entry in `features.yml` with the next free id; then regenerate the SPEC.md block.
- Anything unrouted → propose an entry in this table first, then create it.

## Forbidden

- Reusing or renumbering an id.
- An entry nobody can locate: cite `link` or `docs`, or mark it `status: tbd`.
