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
| `docs/` | dir | the docs index, the constitution, the amendment log and the ADRs | required |
| `features/` | dir | the feature catalog, `features.yml` (schema features/v1) | required |
| `tools/` | dir | repository scripts vendored from the hub (the prose check) |  |
| `.github/` | dir | Actions: thin callers of the hub's reusable workflows, issue forms, the SDLC profile | terminal |
| `SPEC.md` | file | the specification (premise, buckets, statistical layer, architecture, build order) | required |
| `README.md` | file | what the project is and how to work on it | required |
| `AGENTS.md` | file | agent instructions; `CLAUDE.md` imports it | required |
| `CLAUDE.md` | file | imports `AGENTS.md` for Claude Code | required |
| `pyproject.toml` | file | package metadata | required |
| `LICENSE` | file | MIT | required |
| `CHANGELOG.md` | file | what shipped; written by release-please | generated |
| `release-please-config.json` | file | release-please configuration (its manifest is `.release-please-manifest.json`) |  |
| `CONTRIBUTING.md` | file | how to contribute |  |
| `SECURITY.md` | file | how to report a vulnerability |  |
| `CODE_OF_CONDUCT.md` | file | the code of conduct |  |

## Placement

- Core logic → `recon_engine/`
- An adapter → `recon_engine/adapters/<source>/` (create with its own `SCHEMA.md`)
- Tests → `tests/` (create with its own `SCHEMA.md` when the first test lands)
- A decision that is hard to reverse → `docs/adr/NNNN-slug.md`; a change to the constitution → `docs/amendments/NNNN-slug.md`
- A new capability → an entry in `features/features.yml`, then regenerate the SPEC.md block
- Anything unrouted → propose an entry in this table first, then create it.

## Forbidden

- Third-party imports in the core package.
- Netting offsetting items inside or across residual buckets.
- Hand edits to `CHANGELOG.md`, the SPEC.md "Feature catalog" block, or the vendored files in `tools/`.
