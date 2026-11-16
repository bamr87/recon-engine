---
schema: '0.1'
coverage: listed
---

# SCHEMA — recon-engine

> The Recon Engine: a specification and, as the build order lands, a dependency-free core library with ERP adapters.

## Conventions

- `SPEC.md` is the design of record; code follows it and design changes land there first.
- The core package never imports outside the standard library; adapter dependencies live with the adapter.

## Structure

| entry | kind | purpose | rules |
| --- | --- | --- | --- |
| `recon_engine/` | dir | the core library (neutral schemas, decomposition, statistical layer) | required |
| `tests/` | dir | the pytest suite for the core library | required |
| `.github/` | dir | Actions: thin CI callers for the hub's reusable workflows | terminal |
| `SPEC.md` | file | the specification (premise, buckets, statistical layer, architecture, build order) | required |
| `README.md` | file | what the project is and how to work on it | required |
| `AGENTS.md` | file | agent instructions; `CLAUDE.md` imports it | required |
| `CLAUDE.md` | file | imports `AGENTS.md` for Claude Code | required |
| `pyproject.toml` | file | package metadata, the `dev` extra, and the pytest and ruff settings | required |
| `LICENSE` | file | MIT | required |

## Placement

- Core logic → `recon_engine/`
- An adapter → `recon_engine/adapters/<source>/` (create with its own `SCHEMA.md`)
- Tests → `tests/`
- Anything unrouted → propose an entry in this table first, then create it.

## Forbidden

- Third-party imports in the core package.
- Netting offsetting items inside or across residual buckets.
