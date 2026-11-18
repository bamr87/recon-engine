---
schema: '0.1'
coverage: listed
---

# SCHEMA — tools

> Repository scripts vendored from the bamr87/bamr87 hub; the engine's own code lives in `recon_engine/`.

## Structure

| entry | kind | purpose | rules |
| --- | --- | --- | --- |
| `unwrap-prose.py` | file | the one-paragraph-per-line check the `markdown-oneline` workflow runs | required |

## Placement

- A hub-vendored script → here, byte-identical to the hub's copy.
- Anything unrouted → propose an entry in this table first, then create it.

## Forbidden

- Hand edits to a vendored file: change it in the hub, then re-vendor.
- Engine code.
