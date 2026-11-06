---
schema: '0.1'
coverage: listed
---

# SCHEMA — recon_engine

> The core library: neutral schemas, the monthly residual, its decomposition and the statistical layer, standard library only.

## Conventions

- No third-party imports; an adapter that needs one lives under `adapters/<source>/` with its own `SCHEMA.md`.

## Structure

| entry | kind | purpose | rules |
| --- | --- | --- | --- |
| `__init__.py` | file | package marker and version | required |

## Placement

- Build step 1 (neutral schemas, the single monthly number) → `schemas.py`, `residual.py`
- Build step 2 (six-bucket decomposition, transfer log) → `decompose.py`
- Build steps 4–5 (learned expectation, anomaly detection) → `expect.py`, `anomaly.py`
- Adapters → `adapters/<source>/`
- Anything unrouted → propose an entry in this table first, then create it.

## Forbidden

- Netting offsetting items; dropping a transfer that has no operational event.
