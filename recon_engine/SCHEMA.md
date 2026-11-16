---
schema: '0.1'
coverage: listed
---

# SCHEMA — recon_engine

> The core library: neutral schemas, the monthly residual, its decomposition and the statistical layer, standard library only.

## Conventions

- No third-party imports; an adapter that needs one lives under `adapters/<source>/` with its own `SCHEMA.md`.
- Money and quantities are `Decimal`, never float; a record validates itself on construction and raises `ValueError` naming the field.
- A convention SPEC.md leaves open (GL account scope, event-type directions, the period boundary) is a caller argument, never a hard-coded default.

## Structure

| entry | kind | purpose | rules |
| --- | --- | --- | --- |
| `__init__.py` | file | the public API (`__all__`) and the version | required |
| `schemas.py` | file | build step 1: the neutral schemas, `OperationalEvent` and `GLPosting` with their `EventType` and `JournalType` enums (SPEC.md § 5.1) | required |
| `residual.py` | file | build step 1: `monthly_residual`, the single monthly number with its gross totals, and its named errors (SPEC.md § 2) | required |

## Placement

- A field or validation rule of a neutral-schema record (SPEC.md § 5.1) → `schemas.py`
- The single monthly number (SPEC.md § 2) → `residual.py`
- Build step 2 (six-bucket decomposition, transfer log) → `decompose.py`
- Build steps 4–5 (learned expectation, anomaly detection) → `expect.py`, `anomaly.py`
- Adapters → `adapters/<source>/`
- Anything unrouted → propose an entry in this table first, then create it.

## Forbidden

- Netting offsetting items; dropping a transfer that has no operational event.
